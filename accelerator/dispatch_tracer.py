# dispatch_tracer.py
import torch
from torch.utils._python_dispatch import TorchDispatchMode

def summarize_tensor(t: torch.Tensor):
    try:
        layout = str(t.layout).split('.')[-1]
    except:
        layout = str(t.layout)
    dev = str(t.device)
    # 힌트가 되는 속성들: requires_grad, is_sparse, is_quantized, is_mkldnn 등
    flags = []
    if t.requires_grad: flags.append("grad")
    if t.is_sparse: flags.append("sparse")
    if t.is_quantized: flags.append("quant")
    if getattr(t, "is_mps", False): flags.append("mps")
    if layout != "strided": flags.append(layout)
    flagstr = ",".join(flags) if flags else "-"
    return f"Tensor(shape={tuple(t.shape)}, device={dev}, dtype={t.dtype}, flags={flagstr})"

def op_qualified_name(func):
    """
    OpOverload -> 'aten::add.Tensor' 같은 풀네임 추출
    버전에 따라 private 속성이 달라서 방어적으로 처리
    """
    name = None
    try:
        # PyTorch 2.x에서 보통 여기로 잡힘
        name = func._schema.name
    except Exception:
        pass
    if not name:
        try:
            # fallback: overloadpacket.__name__ + '.' + overloadname
            name = f"{func.overloadpacket.__name__}.{func.overloadname}"
            # 위 이름은 'aten::add.Tensor'와 같지 않을 수 있음 (e.g. 'add.Tensor')
            # _dispatch_dump_table은 fully-qualified가 좋아서 보정
            if not name.startswith("aten::"):
                name = "aten::" + name
        except Exception:
            # 최후의 안전망
            name = str(func)
    return name