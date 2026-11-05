"""Ridge Crew app icon: the crew outrunning the bear along a ridge, silhouetted
against a huge pixel-art sunset.

Sky and sun are drawn on a 128x128 grid; the characters use chunkier 2x2 "pixels"
so they read clearly even at home-screen size. Scaled up nearest-neighbour.
Run: python3 make_icon.py <out_dir>
"""
import math
import sys

from PIL import Image

N = 128
SIL = (16, 20, 24)


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


SKY = [hexc(c) for c in ['#16193a', '#211f48', '#352452', '#522b58', '#753456', '#9c3e50',
                         '#c45244', '#e0703a', '#f08f3a', '#f8ad48']]
SUN_OUT = hexc('#ffc96a')
SUN = hexc('#ffdd85')
SUN_IN = hexc('#fff1c4')


def scene(safe=False):
    img = Image.new('RGB', (N, N))
    p = img.load()

    def put(x, y, c):
        if 0 <= x < N and 0 <= y < N:
            p[x, y] = c

    horizon = 100
    for y in range(N):
        k = min(len(SKY) - 1, int(y / horizon * len(SKY)))
        for x in range(N):
            p[x, y] = SKY[k]
    # checker dither on each band edge (2 rows) for a hand-made pixel look
    for y in range(2, horizon):
        k0 = min(len(SKY) - 1, int((y - 2) / horizon * len(SKY)))
        k1 = min(len(SKY) - 1, int(y / horizon * len(SKY)))
        if k0 != k1:
            for x in range(N):
                if (x // 2 + y // 2) % 2 == 0:
                    put(x, y, SKY[k0])
    # stars (2x2 pixels, a couple with a sparkle cross)
    for sx, sy, big in [(16, 12, 1), (38, 20, 0), (94, 9, 0), (112, 24, 1), (66, 7, 0), (24, 34, 0), (104, 40, 0), (80, 26, 0)]:
        for dx in (0, 1):
            for dy in (0, 1):
                put(sx + dx, sy + dy, (255, 244, 214))
        if big:
            for d in (2, 3):
                for qx, qy in ((d, 0), (-d + 1, 0), (0, d), (0, -d + 1)):
                    for e in (0, 1):
                        put(sx + qx + (e if qy else 0), sy + qy + (0 if qy else e), (196, 182, 212))
    # the sun: big, soft-edged rings
    cx, cy, r = 64, 78, 44
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - cx + .5, y - cy + .5)
            if d <= r - 16:
                p[x, y] = SUN_IN
            elif d <= r - 6:
                p[x, y] = SUN
            elif d <= r:
                p[x, y] = SUN_OUT
            elif d <= r + 3:
                p[x, y] = tuple(int(a * .4 + b * .6) for a, b in zip(SUN_OUT, p[x, y]))

    # ground: a dark ridge with a warm rim light
    def ridge(x):
        return 101
    for x in range(N):
        t = ridge(x)
        for y in range(t, N):
            p[x, y] = SIL
        put(x, t, (70, 40, 38))
    # pines at both edges, kept out of the sun
    def pine(px0, base, h):
        for i in range(h):
            w = 1 + int(i * .75)
            if i % 4 == 3:
                w = max(1, w - 2)
            for xx in range(px0 - w, px0 + w + 1):
                put(xx, base - h + i, SIL)
    for px0, h in ((4, 30), (13, 20)):
        pine(px0, ridge(px0) + 2, h)

    # characters traced from the in-game sprites (1 game pixel = 1 icon pixel)
    def rect(x, y, w, h, c=SIL):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                put(xx, yy, c)

    def hiker(x, y, ph, cap):
        big = 0
        a, b = (-2, 1) if ph else (1, -2)
        rect(x - 9, y - 20, 6, 11)                     # backpack
        rect(x - 2 + a, y - 8, 3, 7); rect(x - 2 + a, y - 1, 4, 1)   # legs + boots
        rect(x - 1 + b, y - 8, 3, 7); rect(x - 1 + b, y - 1, 4, 1)
        rect(x - 4, y - 16, 9, 9)                      # shirt
        rect(x + 3 + ph, y - 14, 2, 5)                 # arm
        yb = y - 16
        rect(x - 3, yb - 7, 7, 7)                      # head
        if cap == 'cap':
            rect(x - 4, yb - 10, 8, 4); rect(x + 3, yb - 7, 4, 1)
        elif cap == 'beanie':
            rect(x - 4, yb - 10, 8, 4); rect(x - 3, yb - 11, 6, 1)
        elif cap == 'bucket':
            rect(x - 3, yb - 10, 7, 3); rect(x - 5, yb - 7, 11, 1)
        elif cap == 'curly':
            rect(x - 4, yb - 9, 8, 3); rect(x - 5, yb - 8, 2, 6); rect(x - 1, yb - 11, 2, 2); rect(x - 4, yb - 10, 2, 1); rect(x + 2, yb - 10, 2, 1)
        else:
            rect(x - 4, yb - 9, 8, 2); rect(x + 1, yb - 10, 4, 1)

    def bear(x, y):
        off = [1, -1, -1, 1]
        lh = 8
        for lx, i in ((x - 32, 0), (x - 17, 1), (x - 28, 2), (x - 13, 3)):
            rect(lx + off[i], y - lh, 4, lh); rect(lx + off[i], y - 1, 5, 1)
        rect(x - 34, y - 22, 24, 14); rect(x - 29, y - 25, 13, 3); rect(x - 35, y - 20, 1, 10)
        rect(x - 14, y - 26, 10, 11); rect(x - 13, y - 28, 3, 2)
        rect(x - 5, y - 24, 5, 4)                      # snout
        rect(x - 6, y - 16, 5, 2)                      # lower jaw (mouth open = gap between)
        rect(x - 4, y - 20, 1, 1); rect(x - 2, y - 20, 1, 1)   # fangs
        rect(x - 8, y - 23, 1, 1, (255, 140, 60))      # glowing eye

    feet = 101
    o = 2 if safe else 0
    bear(50 + o, feet)
    for i, (hx, cap) in enumerate(((63, 'cap'), (78, 'curly'), (93, 'beanie'), (108, 'bucket'), (123, 'plain'))):
        hiker(hx - (i * o * 2) // 2 - (o * 2 if i == 4 else 0), feet, i % 2, cap)
    return img


def save(img, size, path):
    img.resize((size, size), Image.NEAREST).save(path, optimize=True)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    full = scene()
    save(full, 512, f'{out}/icon-512.png')
    save(full, 192, f'{out}/icon-192.png')
    save(full, 180, f'{out}/apple-touch-icon.png')
    save(full, 64, f'{out}/favicon.png')
    save(scene(safe=True), 512, f'{out}/icon-maskable-512.png')
    print('icons written to', out)
