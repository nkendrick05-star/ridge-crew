"""Build 'RCD': a tiny add-on font holding only a clearer pixel-style "5"
(Pixelify Sans' own 5 reads like a letter S).

It matches Pixelify Sans' metrics (advance width, cap height, stroke weight), so
it can sit first in the font stack with unicode-range U+0038 and every other
character keeps using Pixelify Sans.
Run: python3 make_five.py   -> writes rcd-500.ttf, rcd-700.ttf and rcd.css
"""
import base64

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

SRC = {500: 'pix500.ttf', 700: 'pix700.ttf'}
# glyph box taken from Pixelify Sans' own "8"/"0" at each weight: left, right, bottom, top, stroke
BOX = {500: (60, 530, -11, 633, 90), 700: (61, 542, -11, 638, 113)}


def five_glyph(weight):
    l, r, b, t, _ = BOX[weight]
    v, h = (104, 98) if weight < 600 else (126, 120)   # vertical / horizontal stroke, matched to Pixelify
    mid = b + int((t - b) * .56)                          # middle bar sits a little above centre
    rects = [
        (l, t - h, r, t),                                 # flat top bar with square corners (the "not an S" part)
        (l, mid + h // 2, l + v, t - h),                  # straight drop down the left
        (l, mid - h // 2, r - v, mid + h // 2),           # middle bar
        (r - v, b + h, r, mid - h // 2),                  # right side of the belly
        (l + v, b, r - v, b + h),                         # bottom of the belly (notched corners)
        (l, b + h, l + v, b + 2 * h),                     # little hook bottom-left
    ]
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1 in rects:
        pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0)); pen.closePath()
    return pen.glyph()


def build(weight):
    src = TTFont(SRC[weight])
    adv = src['hmtx']['five'][0]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'five'])
    fb.setupCharacterMap({0x35: 'five'})
    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({'.notdef': empty, 'five': five_glyph(weight)})
    l = BOX[weight][0]
    fb.setupHorizontalMetrics({'.notdef': (adv, 0), 'five': (adv, l)})
    hh = src['hhea']
    fb.setupHorizontalHeader(ascent=hh.ascent, descent=hh.descent)
    fb.setupNameTable({'familyName': 'RCD', 'styleName': 'Regular' if weight < 600 else 'Bold'})
    os2 = src['OS/2']
    fb.setupOS2(sTypoAscender=os2.sTypoAscender, sTypoDescender=os2.sTypoDescender, sTypoLineGap=os2.sTypoLineGap,
                usWinAscent=os2.usWinAscent, usWinDescent=os2.usWinDescent, usWeightClass=weight,
                sxHeight=getattr(os2, 'sxHeight', 0), sCapHeight=getattr(os2, 'sCapHeight', 0), fsSelection=0x40)
    fb.setupPost()
    path = f'rcd-{weight}.ttf'
    fb.save(path)
    return path


if __name__ == '__main__':
    css = []
    for w, rng in ((500, '100 599'), (700, '600 900')):
        data = base64.b64encode(open(build(w), 'rb').read()).decode()
        css.append("@font-face{font-family:'RCD';src:url(data:font/ttf;base64,%s) format('truetype');font-weight:%s;unicode-range:U+0035;font-display:block}" % (data, rng))
    open('rcd.css', 'w').write('\n'.join(css))
    print('ok', sum(len(c) for c in css), 'bytes of CSS')
