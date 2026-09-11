# -*- coding: utf-8 -*-
"""紹介ページ用のアイコンを生成する。

タロットの「運命の輪」を下敷きに、自転車のホイール（8本スポーク）と
方位磁針を重ねた図案。運命の輪の縁に並ぶ文字を、コンパスのベゼルの
目盛りに読み替えて、ひとつの図形にまとめている。
外部の画像素材は使わず、ここで描く。

    py make_icon.py
"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
S = 1024

NAVY = (29, 43, 69)        # 下地（夜のブルベ）
RIM = (150, 167, 196)      # ホイール・針の南
RIM_DIM = (96, 114, 146)   # スポーク・細かい目盛り
AMBER = (232, 163, 61)     # 針の北・四方位の目盛り
NEEDLE_TILT = -14          # 針の傾き（真上だと硬いので少し振る）


def circle(d, cx, cy, r, **kw):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), **kw)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + math.cos(a) * r, cy + math.sin(a) * r)


def draw(img):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, S, S), radius=int(S * 0.22), fill=NAVY)
    cx = cy = S * 0.5

    # ---- ベゼルの方位目盛り（運命の輪の縁の文字を目盛りに読み替える）----
    # 細かい目盛りは小さいサイズで潰れて濁るだけなので、4方位を太く短く置く
    r_out = S * 0.415
    for k in range(8):
        deg = k * 45 - 90
        cardinal = (k % 2 == 0)
        r_in = r_out - (S * 0.095 if cardinal else S * 0.045)
        d.line([polar(cx, cy, r_in, deg), polar(cx, cy, r_out, deg)],
               fill=AMBER if cardinal else RIM_DIM,
               width=int(S * (0.036 if cardinal else 0.014)))

    # ---- ホイール（タイヤ＋リム）----
    R = S * 0.288
    tire = int(S * 0.046)
    circle(d, cx, cy, R, outline=RIM, width=tire)
    circle(d, cx, cy, R - tire * 0.95, outline=RIM_DIM, width=int(S * 0.013))

    # ---- スポーク8本（運命の輪と同じ本数）----
    for k in range(8):
        deg = k * 45 + 22.5
        d.line([polar(cx, cy, S * 0.175, deg), polar(cx, cy, R - tire * 0.6, deg)],
               fill=RIM_DIM, width=int(S * 0.012))

    # ---- 方位磁針 ----
    # 針が読めなければコンパスにならないので、ここを主役にする。
    # 下地の色で一回り大きく描いてから重ねると、スポークと重なっても輪郭が立つ。
    L = S * 0.300          # 針の長さ（中心から先端まで）
    W = S * 0.105          # 針の最大幅
    for grow, colors in ((S * 0.030, (NAVY, NAVY)), (0, (AMBER, RIM))):
        for sign, color in ((1, colors[0]), (-1, colors[1])):   # 北＝アンバー
            tip = polar(cx, cy, (L + grow) * sign, NEEDLE_TILT - 90)
            left = polar(cx, cy, W + grow, NEEDLE_TILT - 90 + 90 * sign)
            right = polar(cx, cy, W + grow, NEEDLE_TILT - 90 - 90 * sign)
            d.polygon([tip, left, (cx, cy), right], fill=color)

    # 軸受け
    circle(d, cx, cy, S * 0.040, fill=NAVY)
    circle(d, cx, cy, S * 0.022, fill=RIM)


img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
draw(img)

os.makedirs(ASSETS, exist_ok=True)
img.resize((512, 512), Image.LANCZOS).save(os.path.join(ASSETS, 'icon.png'))
img.save(os.path.join(ASSETS, 'favicon.ico'), sizes=[(48, 48), (32, 32), (16, 16)])
print('書き出し:', os.path.join(ASSETS, 'icon.png'))
print('書き出し:', os.path.join(ASSETS, 'favicon.ico'))

sizes = [256, 128, 64, 48, 32, 16]
strip = Image.new('RGBA', (sum(sizes) + 20 * len(sizes), 280), (250, 250, 250, 255))
x = 10
for s in sizes:
    small = img.resize((s, s), Image.LANCZOS)
    strip.paste(small, (x, 10), small)
    x += s + 20
strip.save(os.path.join(HERE, 'icon_preview.png'))
print('確認用:', os.path.join(HERE, 'icon_preview.png'))

# 小さいサイズでも各要素が残っているかを画素で確認する
print('\n--- 小サイズでの見え方（色の占める割合）---')
for s in (48, 32, 16):
    im = img.resize((s, s), Image.LANCZOS).convert('RGB')
    px = list(im.get_flattened_data()) if hasattr(im, 'get_flattened_data') else list(im.getdata())

    def near(c, t, tol):
        return sum(abs(a - b) for a, b in zip(c, t)) < tol

    # 混色された画素も拾うため、暖色寄り（赤−青が大きい）かどうかで数える
    warm = sum(1 for c in px if c[0] - c[2] > 40)
    steel = sum(1 for c in px if near(c, RIM, 130))
    print(f'  {s:>3}px: 針の北・方位目盛り(暖色) {warm / len(px) * 100:4.1f}%  '
          f'ホイール・針の南(スチール) {steel / len(px) * 100:4.1f}%')
