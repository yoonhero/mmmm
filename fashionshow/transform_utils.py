from PIL import Image
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms

ascii = [' ', '.', '-', '_', ',', ':', '^', 'i', 'u', 'V', '8', '#'] + ["_", "|", "/", "\\"] # 12(bright) + 4(edge)

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
    width, _ = quantized_img.shape

    result = []
    for row in quantized_img.tolist():
        ascii_row = ""
        for cell in row:
            ascii_row += ascii[int(cell)]
        result.append(f"{ascii_row:<{width}}")
    return result

# give your best fashion design 160 pics.
def fashion_show(quantized_imgs, labels, name):
    width = 14
    wpadding, hpadding = 4, 4
    hspace = (width+hpadding)
    result = [""]*hspace*32

    for i in range(32):
        for j in range(5):
            index = 5*i+j
            quantized_img, label = quantized_imgs[index], labels[index]
            ascii_img = transform_ascii(quantized_img)

            for ii, row in enumerate(ascii_img):
                result[2+ii+i*hspace] += row + " "*wpadding
            result[i*hspace] += f"{label:<{width+wpadding}}"
                
    with open(f"fashion_show_{name}.txt", "w") as f:
        f.write("\n".join(result))

def get_mask(img: np.ndarray) -> torch.Tensor:
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    s = hsv[...,1]
    return torch.from_numpy(s>30)

def edge_detect(tensor_img, filter, threshold) -> torch.Tensor:
    filtered = F.conv2d(tensor_img, filter.unsqueeze(0), padding=1).abs() > threshold
    return filtered

def pipeline(path):
    img = cv2.imread(path)
    tensor_img = load_tensor_img(img).mean(0, keepdim=True)
    quantized_img = torch.floor(tensor_img*11.9)
    mask = get_mask(img)
    quantized_img = quantized_img * mask

    for i, filterT in enumerate([filter_horizontal, filter_vertical, filter_rightup, filter_leftup]):
        threshold = 0.9 if i < 2 else 0.8
        edges = edge_detect(tensor_img, filterT, threshold=threshold)
        transforms.ToPILImage()(1.0-edges*1).show()
        print(edges)
        quantized_img[edges] = 12+i
    return quantized_img

def make_width_80(tensor_img):
    c, w, h = tensor_img.shape
    compress_ratio = (w // 80)
    return F.max_pool2d(tensor_img[:, :compress_ratio*80, :compress_ratio*80], compress_ratio)

if __name__ == "__main__":
    result = make_width_80(pipeline("snu_jacket.png"))
    # transforms.ToPILImage()(result).show()
    print(result.shape)
    with open("snu_jacket.txt", "w") as f:
        f.write("\n".join(transform_ascii(result)))