# -*- coding: utf-8 -*-
"""紹介ページ用のアイコンを生成する。

キューシートの矢印（右折）をモチーフにした。外部の画像素材は使わない。
    py make_icon.py
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
S = 1024

NAVY = (29, 43, 69)       # 下地（夜のブルベ）
AMBER = (232, 163, 61)    # 矢印（反射材の色）


def draw(img):
    d = ImageDraw.Draw(img)
    r = int(S * 0.22)
    d.rounded_rectangle((0, 0, S, S), radius=r, fill=NAVY)

    # 右折の矢印：下から上がって右へ曲がる
    w = int(S * 0.115)                     # 線の太さ
    x0, y0 = int(S * 0.34), int(S * 0.80)  # 下端
    y1 = int(S * 0.38)                     # 曲がる高さ
    x1 = int(S * 0.60)                     # 右へ伸ばす先

    d.line([(x0, y0), (x0, y1)], fill=AMBER, width=w)
    d.line([(x0 - w // 2, y1), (x1, y1)], fill=AMBER, width=w)
    # 角を丸める
    d.ellipse((x0 - w // 2, y1 - w // 2, x0 + w // 2, y1 + w // 2), fill=AMBER)

    # 矢じり
    head = int(S * 0.115)
    d.polygon([(x1 + head, y1), (x1 - head * 0.2, y1 - head),
               (x1 - head * 0.2, y1 + head)], fill=AMBER)

    # 距離の目盛りに見立てた点（キューシートらしさ）
    for i in range(3):
        cy = int(S * 0.80) - i * int(S * 0.115)
        d.ellipse((int(S * 0.70) - 14, cy - 14, int(S * 0.70) + 14, cy + 14),
                  fill=(90, 108, 138))


img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
draw(img)

os.makedirs(ASSETS, exist_ok=True)
img.resize((512, 512), Image.LANCZOS).save(os.path.join(ASSETS, 'icon.png'))
img.save(os.path.join(ASSETS, 'favicon.ico'), sizes=[(48, 48), (32, 32), (16, 16)])
print('書き出し:', os.path.join(ASSETS, 'icon.png'))
print('書き出し:', os.path.join(ASSETS, 'favicon.ico'))

# 確認用の実寸プレビュー
sizes = [256, 128, 64, 48, 32, 16]
strip = Image.new('RGBA', (sum(sizes) + 20 * len(sizes), 280), (250, 250, 250, 255))
x = 10
for s in sizes:
    small = img.resize((s, s), Image.LANCZOS)
    strip.paste(small, (x, 10), small)
    x += s + 20
strip.save(os.path.join(HERE, 'icon_preview.png'))
print('確認用:', os.path.join(HERE, 'icon_preview.png'))
