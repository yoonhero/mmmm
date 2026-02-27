#!/usr/bin/env python3
import argparse
import json
import math
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
from torch import optim
from torch.utils.data import DataLoader, TensorDataset

from model import TinyTransformer
from transform_utils import ascii, pipeline

PAT_KEEP_ALNUM_SPACE = re.compile(r"[^a-z0-9 ]")
PAT_MULTI_SPACE = re.compile(r"\s+")
PAT_IMAGE_DIR = re.compile(r"images_\d+x\d+")
PANTY_KEYWORDS = (
    "panty",
    "panties",
    "brief",
    "briefs",
    "trunk",
    "trunks",
    "boxer",
    "boxers",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train an autoregressive model that maps char 3-gram text tokens to "
            "ASCII image tokens (0~15). Sequence format: [3-grams + <pad> + <start> + image]."
        )
    )
    parser.add_argument(
        "--train-json",
        type=Path,
        default=Path("codex/data/full_dataset_preprocessed/train_64.json"),
        help="Path to training json records.",
    )
    parser.add_argument(
        "--vocab-path",
        type=Path,
        default=Path("vocabs.txt"),
        help="Path to vocabs.txt (char 3-gram list).",
    )
    parser.add_argument("--model-out", type=Path, default=Path("fashion_ascii_trigram.pt"))
    parser.add_argument("--sample-out", type=Path, default=Path("sample_generated.txt"))
    parser.add_argument("--sample-text", type=str, default="men blue shirt")
    parser.add_argument(
        "--image-size",
        type=int,
        default=32,
        help=(
            "Preferred source image side length. "
            "Example: --image-size 64 will try images_64x64 paths."
        ),
    )
    parser.add_argument(
        "--pool-size",
        type=int,
        default=0,
        help="Adaptive pool size for image tokens. Use <=0 to keep source image size.",
    )
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--n-layer", type=int, default=2)
    parser.add_argument("--max-cond-len", type=int, default=0, help="0 means auto from dataset max.")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="0 means use all rows after filtering.",
    )
    parser.add_argument(
        "--allow-human",
        action="store_true",
        help="Disable default no_human filter and allow has_person == 1 rows.",
    )
    parser.add_argument(
        "--allow-panty",
        action="store_true",
        help="Disable default panty exclusion filter.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=str, default="")
    parser.add_argument("--log-every", type=int, default=100)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument(
        "--resume",
        type=Path,
        default=None,
        help="Optional checkpoint path to resume from.",
    )
    parser.add_argument(
        "--allow-image-size-fallback",
        action="store_true",
        help=(
            "If set, fall back to the original imagePath when the requested "
            "image-size path does not exist."
        ),
    )
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_device(user_device: str) -> str:
    if user_device:
        return user_device
    return "cuda" if torch.cuda.is_available() else "cpu"


def normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = PAT_KEEP_ALNUM_SPACE.sub(" ", text)
    text = PAT_MULTI_SPACE.sub(" ", text).strip()
    return text


def char_ngrams(text: str, n: int = 3) -> List[str]:
    text = normalize_text(text)
    if len(text) < n:
        return []
    return [text[i : i + n] for i in range(len(text) - n + 1)]


def load_vocab(vocab_path: Path) -> Tuple[List[str], Dict[str, int], int, int, int]:
    if not vocab_path.exists():
        raise SystemExit(f"vocab file not found: {vocab_path}")

    trigram_tokens = [line for line in vocab_path.read_text(encoding="utf-8").splitlines() if line]
    base_tokens = [f"<pix_{i}>" for i in range(16)] + ["<pad>", "<start>", "<unk>"]
    merged = []
    seen = set()
    for tok in base_tokens + trigram_tokens:
        if tok in seen:
            continue
        seen.add(tok)
        merged.append(tok)

    stoi = {tok: i for i, tok in enumerate(merged)}
    pad_id = stoi["<pad>"]
    start_id = stoi["<start>"]
    unk_id = stoi["<unk>"]
    return merged, stoi, pad_id, start_id, unk_id


def encode_text(text: str, stoi: Dict[str, int], unk_id: int) -> List[int]:
    return [stoi.get(tok, unk_id) for tok in char_ngrams(text, n=3)]


def resolve_image_path(
    image_path: str, image_size: int, allow_fallback: bool
) -> Path | None:
    original = Path(image_path)
    preferred = original

    if image_size > 0:
        parts = list(original.parts)
        replaced = False
        for i, part in enumerate(parts):
            if PAT_IMAGE_DIR.fullmatch(part):
                parts[i] = f"images_{image_size}x{image_size}"
                replaced = True
                break
        if replaced:
            preferred = Path(*parts)

    if preferred.exists():
        return preferred
    if allow_fallback and original.exists():
        return original
    return None


def encode_image_tokens(
    image_path: str, image_size: int, pool_size: int, allow_fallback: bool
) -> Tuple[List[int], int, int]:
    resolved = resolve_image_path(image_path, image_size=image_size, allow_fallback=allow_fallback)
    if resolved is None:
        raise FileNotFoundError(image_path)

    quantized = pipeline(str(resolved))
    if pool_size > 0:
        quantized = F.adaptive_max_pool2d(quantized, (pool_size, pool_size))
    quantized = quantized.squeeze(0).clamp(min=0, max=15).to(torch.long)
    h, w = quantized.shape
    return quantized.flatten().tolist(), h, w


def is_panty_item(row: dict) -> bool:
    fields = [
        normalize_text(str(row.get("type", ""))),
        normalize_text(str(row.get("displayProductName", ""))),
        normalize_text(str(row.get("subCategory", ""))),
    ]
    hay = " ".join(fields)
    return any(re.search(rf"\b{re.escape(kw)}\b", hay) for kw in PANTY_KEYWORDS)


def load_records(train_json: Path, allow_human: bool, allow_panty: bool, max_samples: int) -> List[dict]:
    if not train_json.exists():
        raise SystemExit(f"train json not found: {train_json}")
    rows = json.loads(train_json.read_text(encoding="utf-8"))

    total_rows = len(rows)
    if not allow_human:
        rows = [r for r in rows if int(r.get("has_person", 1)) == 0]
    no_human_rows = len(rows)

    removed_panty = 0
    if not allow_panty:
        kept = []
        for r in rows:
            if is_panty_item(r):
                removed_panty += 1
                continue
            kept.append(r)
        rows = kept

    print(
        "record_filters: "
        f"total={total_rows} "
        f"after_no_human={no_human_rows} "
        f"removed_panty={removed_panty} "
        f"after_all={len(rows)}"
    )

    if max_samples > 0:
        rows = rows[:max_samples]
    return rows


def infer_cond_len(records: List[dict], stoi: Dict[str, int], unk_id: int, max_cond_len: int) -> int:
    if not records:
        raise SystemExit("no records available after filtering")

    lengths = [len(encode_text(r.get("displayProductName", ""), stoi, unk_id)) for r in records]
    inferred = max(lengths) if lengths else 0
    if inferred <= 0:
        inferred = 1
    if max_cond_len > 0:
        return min(inferred, max_cond_len)
    return inferred


def build_training_tensors(
    records: List[dict],
    stoi: Dict[str, int],
    pad_id: int,
    start_id: int,
    unk_id: int,
    cond_len: int,
    image_size: int,
    pool_size: int,
    allow_image_size_fallback: bool,
) -> Tuple[TensorDataset, int, int, int]:
    xs: List[torch.Tensor] = []
    ys: List[torch.Tensor] = []
    loss_masks: List[torch.Tensor] = []

    image_token_len = -1
    image_h = -1
    image_w = -1
    skipped = 0

    for i, row in enumerate(records, start=1):
        image_path = row.get("imagePath")
        if not image_path or not Path(image_path).exists():
            skipped += 1
            continue

        try:
            image_ids, h, w = encode_image_tokens(
                image_path=image_path,
                image_size=image_size,
                pool_size=pool_size,
                allow_fallback=allow_image_size_fallback,
            )
        except Exception:
            skipped += 1
            continue

        if image_token_len < 0:
            image_token_len = len(image_ids)
            image_h, image_w = h, w
        elif len(image_ids) != image_token_len:
            skipped += 1
            continue

        text_ids = encode_text(row.get("displayProductName", ""), stoi, unk_id)
        text_ids = text_ids[:cond_len]
        text_ids = text_ids + [pad_id] * (cond_len - len(text_ids))

        full = text_ids + [start_id] + image_ids
        x = torch.tensor(full[:-1], dtype=torch.long)
        y = torch.tensor(full[1:], dtype=torch.long)

        # loss only on image token targets (the portion after <start>)
        mask = torch.zeros_like(y, dtype=torch.float32)
        mask[cond_len:] = 1.0

        xs.append(x)
        ys.append(y)
        loss_masks.append(mask)

        if i % 1000 == 0:
            print(f"encoded {i}/{len(records)} rows")

    if not xs:
        raise SystemExit("all rows were skipped while encoding")

    x_tensor = torch.stack(xs)
    y_tensor = torch.stack(ys)
    m_tensor = torch.stack(loss_masks)
    print(f"usable_rows={x_tensor.shape[0]} skipped_rows={skipped}")
    return TensorDataset(x_tensor, y_tensor, m_tensor), image_token_len, image_h, image_w


def train_loop(
    model: TinyTransformer,
    loader: DataLoader,
    device: str,
    steps: int,
    lr: float,
    weight_decay: float,
    grad_clip: float,
    log_every: int,
) -> List[float]:
    opt = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    losses: List[float] = []

    loop = iter(loader)
    model.train()
    for step in range(1, steps + 1):
        try:
            x, y, mask = next(loop)
        except StopIteration:
            loop = iter(loader)
            x, y, mask = next(loop)

        x = x.to(device)
        y = y.to(device)
        mask = mask.to(device)

        logits, _ = model(x)
        token_loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)),
            y.view(-1),
            reduction="none",
        ).view_as(y)
        loss = (token_loss * mask).sum() / mask.sum().clamp_min(1.0)

        opt.zero_grad(set_to_none=True)
        loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        opt.step()

        losses.append(loss.item())
        if step == 1 or step % log_every == 0:
            print(f"step {step:5d}/{steps}  loss={loss.item():.4f}")

    return losses


@torch.no_grad()
def sample_image_tokens(
    model: TinyTransformer,
    cond_ids: List[int],
    start_id: int,
    image_tokens: int,
    device: str,
    temperature: float,
) -> List[int]:
    model.eval()
    temperature = max(temperature, 1e-5)
    idx = torch.tensor([cond_ids + [start_id]], dtype=torch.long, device=device)

    for _ in range(image_tokens):
        idx_cond = idx[:, -model.block_size :]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :16] / temperature
        probs = F.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        idx = torch.cat([idx, next_token], dim=1)

    model.train()
    return idx[0, -image_tokens:].tolist()


def render_grids(image_ids: List[int], h: int, w: int) -> Tuple[List[str], List[str]]:
    num_lines: List[str] = []
    ascii_lines: List[str] = []

    for r in range(h):
        row = image_ids[r * w : (r + 1) * w]
        num_lines.append(" ".join(f"{v:02d}" for v in row))
        ascii_lines.append("".join(ascii[v] for v in row))
    return num_lines, ascii_lines


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    device = resolve_device(args.device)

    vocab, stoi, pad_id, start_id, unk_id = load_vocab(args.vocab_path)
    records = load_records(
        train_json=args.train_json,
        allow_human=args.allow_human,
        allow_panty=args.allow_panty,
        max_samples=args.max_samples,
    )
    cond_len = infer_cond_len(records, stoi, unk_id, args.max_cond_len)

    print(f"device={device}")
    print(f"records={len(records)}")
    print(f"vocab_size={len(vocab)}")
    print(f"cond_len={cond_len}")
    print(f"special_ids: pad={pad_id} start={start_id} unk={unk_id}")
    print("image_token_ids=0~15")
    print(f"filters: no_human={not args.allow_human} exclude_panty={not args.allow_panty}")
    print(f"image_size={args.image_size} pool_size={args.pool_size}")

    dataset, image_token_len, image_h, image_w = build_training_tensors(
        records=records,
        stoi=stoi,
        pad_id=pad_id,
        start_id=start_id,
        unk_id=unk_id,
        cond_len=cond_len,
        image_size=args.image_size,
        pool_size=args.pool_size,
        allow_image_size_fallback=args.allow_image_size_fallback,
    )
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    block_size = cond_len + image_token_len
    model = TinyTransformer(
        vocab_size=len(vocab),
        block_size=block_size,
        d_model=args.d_model,
        n_heads=args.n_heads,
        n_layer=args.n_layer,
    ).to(device)

    if args.resume is not None:
        if not args.resume.exists():
            raise SystemExit(f"resume checkpoint not found: {args.resume}")
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt["model_state"])
        print(f"resumed from: {args.resume}")

    print(
        f"model: block_size={block_size} d_model={args.d_model} "
        f"n_heads={args.n_heads} n_layer={args.n_layer}"
    )

    if args.steps > 0:
        train_loop(
            model=model,
            loader=loader,
            device=device,
            steps=args.steps,
            lr=args.lr,
            weight_decay=args.weight_decay,
            grad_clip=args.grad_clip,
            log_every=args.log_every,
        )

    checkpoint = {
        "model_state": model.state_dict(),
        "vocab": vocab,
        "config": {
            "block_size": block_size,
            "d_model": args.d_model,
            "n_heads": args.n_heads,
            "n_layer": args.n_layer,
            "cond_len": cond_len,
            "image_size": args.image_size,
            "image_h": image_h,
            "image_w": image_w,
            "pool_size": args.pool_size,
            "allow_image_size_fallback": args.allow_image_size_fallback,
        },
    }
    torch.save(checkpoint, args.model_out)
    print(f"saved checkpoint: {args.model_out}")

    sample_text_ids = encode_text(args.sample_text, stoi, unk_id)
    sample_text_ids = sample_text_ids[:cond_len]
    sample_cond = sample_text_ids + [pad_id] * (cond_len - len(sample_text_ids))

    generated_ids = sample_image_tokens(
        model=model,
        cond_ids=sample_cond,
        start_id=start_id,
        image_tokens=image_token_len,
        device=device,
        temperature=args.temperature,
    )

    # If image is square we keep the original size. Otherwise, fallback to a flat single-row render.
    if image_h * image_w != len(generated_ids):
        side = int(math.sqrt(len(generated_ids)))
        if side * side == len(generated_ids):
            image_h, image_w = side, side
        else:
            image_h, image_w = 1, len(generated_ids)

    num_lines, ascii_lines = render_grids(generated_ids, image_h, image_w)
    report = []
    report.append(f"sample_text={args.sample_text}")
    report.append(f"normalized={normalize_text(args.sample_text)}")
    report.append(f"char3gram_count={len(sample_text_ids)}")
    report.append("")
    report.append("[image tokens: 0~15]")
    report.extend(num_lines)
    report.append("")
    report.append("[ascii image]")
    report.extend(ascii_lines)
    args.sample_out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"saved sample: {args.sample_out}")
    print("\n".join(report[:12]))


if __name__ == "__main__":
    main()
