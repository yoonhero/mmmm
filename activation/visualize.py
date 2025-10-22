import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import random

from my_beautiful_actvation import *

def plot_relu_partition(division):
    fig, ax = plt.subplots(figsize=(6,6))
    act_map = coloring(division)

    ax.imshow(
        act_map,
        origin="lower",
        extent=(lo, hi, lo, hi),
        cmap="Blues",
        alpha=0.9,
    )

    for a, b, c, _ in division:
        z = levelset(a, b, c)
        ax.plot(z[:, 0], z[:, 1], color='black', lw=0.8)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect('equal')
    ax.set_title("ReLU Activation Partition")

    return fig, ax

def render_relu(division):
    x = np.linspace(lo, hi, 500)
    y = np.linspace(lo, hi, 500)
    xx, yy = np.meshgrid(x, y)
    v = np.stack([xx, yy], axis=2)
    sign = np.array([line[-1] for line in division])
    zz = (relu(linear(v, division))*sign).sum(axis=2)
    # zz[zz<-1]=-1
    zz = np.clip(zz, -1, 1)/2

    region_key = ((linear(v, division) > 0) * np.cumprod([1]+[2]*(len(division)-1))).sum(axis=2)
    unique_regions = np.unique(region_key)

    palette = sns.color_palette("Spectral", len(unique_regions))
    mu = list(range(len(unique_regions)))
    random.shuffle(mu)
    color_dict = {rid: palette[mu[i]] for i, rid in enumerate(unique_regions)}
    # print(len(color_dict))

    nx, ny = xx.shape
    vertices = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))

    def square_to_tris(i, j):
        idx = i * ny + j
        return [
            (idx, idx + 1, idx + ny + 1),
            (idx, idx + ny + 1, idx + ny)
        ]

    faces_i, faces_j, faces_k, face_color = [], [], [], []
    for i in range(nx - 1):
        for j in range(ny - 1):
            rid = region_key[j, i]
            color = color_dict[rid]
            for (a, b, c) in square_to_tris(i, j):
                faces_i.append(a)
                faces_j.append(b)
                faces_k.append(c)
                face_color.append(f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})")

    # ----- Plotly Mesh3d -----
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces_i,
            j=faces_j,
            k=faces_k,
            facecolor=face_color,
            showscale=False,
            opacity=1.0,
            flatshading=False,        # 부드러운 셰이딩 → 더 밝아 보임
            lighting=dict(
                ambient=0.85,         # 전체 밝기 바탕
                diffuse=0.8,         # 난반사 ↑
                specular=0.1,        # 하이라이트(번쩍) 추가
                roughness=0.25,       # 하이라이트가 너무 퍼지지 않게
                fresnel=0.0           # 가장자리 어두워짐 줄이기
            ),
            lightposition=dict(x=1.5, y=2.0, z=3.0)  # 위 사선에서 비추는 느낌
        )
    ])

    # ----- 축 및 보기 설정 -----
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                showbackground=False,
                showticklabels=False,
                showgrid=False,
                zeroline=True,
                zerolinecolor="black",
                title="x",
            ),
            yaxis=dict(
                showbackground=False,
                showticklabels=False,
                showgrid=False,
                zeroline=True,
                zerolinecolor="black",
                title="y",
            ),
            zaxis=dict(
                range=[-1, 1], autorange=False,
                showbackground=False,
                showticklabels=False,
                showgrid=False,
                zeroline=True,
                zerolinecolor="black",
                title="z",
            ),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.5),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.0))  # [-1,1]x[-1,1]가 잘 보이게
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )

    fig.write_html("my_beautiful_activation.html", auto_open=True)