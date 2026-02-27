from PIL import Image
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import math

ascii = [' ', '.', ',', '`', "'", ':', ';', '<', 'j', '*', 'd', '#'] + ["_", "|", "/", "\\"] # 12(bright) + 4(edge)
EDGE_THRESHOLDS = (0.88, 0.88, 0.56, 0.56)
BORDER_TRIM = 1

load_tensor_img = transforms.ToTensor()

filter_horizontal = torch.tensor([[
    [0., 0, 0],
    [1, 1, 1],
    [-1, -1, -1]
]])
filter_vertical = torch.tensor([[
    [0., 1, -1],
    [0, 1, -1],
    [0, 1, -1]
]])
filter_rightup = torch.tensor([[
    [0., 1, 0],
    [1, -1, 0],
    [-1, 0, 0]
]])
filter_leftup = torch.tensor([[
    [0., 1, 0],
    [0, -1, 1],
    [0, 0, -1]
]])

def transform_ascii(quantized_img) -> list:
    if quantized_img.shape.__len__() == 3:
        quantized_img = quantized_img[0]
    _, width = quantized_img.shape

    result = []
    for row in quantized_img.tolist():
        ascii_row = ""
        for cell in row:
            ascii_row += ascii[int(cell)]
        result.append(f"{ascii_row:<{width}}")
    return result

# give your best fashion design 160 pics.
def fashion_show(quantized_imgs, labels, name, cols=5, wpadding=4, hpadding=2):
    if cols <= 0:
        raise ValueError("cols must be positive")

    total = len(quantized_imgs)
    if total == 0:
        raise ValueError("quantized_imgs is empty")
    if len(labels) != total:
        raise ValueError(f"labels length mismatch: {len(labels)} != {total}")

    ascii_blocks = [transform_ascii(quantized_imgs[i]) for i in range(total)]
    cell_h = max(len(block) for block in ascii_blocks)
    cell_w = max(max((len(row) for row in block), default=0) for block in ascii_blocks)

    rows = math.ceil(total / cols)
    result = []

    for r in range(rows):
        start = r * cols
        end = min(start + cols, total)

        label_line = ""
        for idx in range(start, end):
            label_line += f"{labels[idx]:<{cell_w + wpadding}}"
        result.append(label_line.rstrip())
        result.append("")

        for line_idx in range(cell_h):
            line = ""
            for idx in range(start, end):
                block = ascii_blocks[idx]
                text = block[line_idx] if line_idx < len(block) else ""
                line += text.ljust(cell_w) + " " * wpadding
            result.append(line.rstrip())

        for _ in range(hpadding):
            result.append("")

    with open(f"fashion_show_{name}.txt", "w") as f:
        f.write("\n".join(result))

def get_mask(img: np.ndarray) -> torch.Tensor:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s = hsv[...,1]
    return torch.from_numpy(s>30)

# Sobel filter might perform better than this type of sily detection.
# But simple is the best
def edge_detect(tensor_img, filter, threshold, border_trim=BORDER_TRIM) -> torch.Tensor:
    # replicate padding prevents artificial high gradients caused by zero padding
    padded = F.pad(tensor_img.unsqueeze(0), (1, 1, 1, 1), mode="replicate")
    filtered = F.conv2d(padded, filter.unsqueeze(0)).abs() > threshold
    edges = filtered.squeeze(0)

    # clear the outer rim to avoid rendering border artifacts
    if border_trim > 0:
        edges[:, :border_trim, :] = False
        edges[:, -border_trim:, :] = False
        edges[:, :, :border_trim] = False
        edges[:, :, -border_trim:] = False
    return edges

def pipeline(path):
    img = cv2.imread(path)
    tensor_img = load_tensor_img(img).mean(0, keepdim=True)
    quantized_img = torch.floor(tensor_img*11.9)
    mask = get_mask(img)
    quantized_img = quantized_img * mask

    for i, filterT in enumerate([filter_horizontal, filter_vertical, filter_rightup, filter_leftup]):
        threshold = EDGE_THRESHOLDS[i]
        edges = edge_detect(tensor_img, filterT, threshold=threshold)
        # transforms.ToPILImage()(1.0-edges*1).show()
        quantized_img[edges] = 12+i
    return quantized_img

def make_width_80(tensor_img):
    _, h, w = tensor_img.shape
    base = min(h, w)
    compress_ratio = base // 80
    if compress_ratio < 1:
        return tensor_img

    crop_h = (h // compress_ratio) * compress_ratio
    crop_w = (w // compress_ratio) * compress_ratio
    return F.max_pool2d(tensor_img[:, :crop_h, :crop_w], compress_ratio)

if __name__ == "__main__":
    # result = make_width_80(pipeline("snu_jacket.png"))
    import glob
    import random
    import json
    with open("./codex/data/full_dataset_preprocessed/train.json", "r") as f:
        dataset = json.load(f)
    dataset = list(filter(lambda x: not bool(x['has_person']), dataset))
    random_row = random.sample(dataset, 20)
    images = [pipeline(x["imagePath"].replace("32", "64"))
            for x in random_row]
    labels = [x['displayProductName'] for x in random_row]
    fashion_show(images, labels, "train_big", cols=3)
    # transforms.ToPILImage()(result).show()
    # with open("test.txt", "w") as f:
        # f.write("\n".join(transform_ascii(result)))
