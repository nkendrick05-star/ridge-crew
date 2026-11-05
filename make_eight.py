"""Build 'RC8': a tiny add-on font holding only a clearer pixel-style "8".

It matches Pixelify Sans' metrics (advance width, cap height, stroke weight), so
it can sit first in the font stack with unicode-range U+0038 and every other
character keeps using Pixelify Sans.
Run: python3 make_eight.py   -> writes rc8-500.ttf, rc8-700.ttf and rc8.css
"""
import base64

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

SRC = {500: 'pix500.ttf', 700: 'pix700.ttf'}
# glyph box taken from Pixelify Sans' own "8"/"0" at each weight: left, right, bottom, top, stroke
BOX = {500: (60, 530, -11, 633, 90), 700: (61, 542, -11, 638, 113)}


def eight_glyph(weight):
    l, r, b, t, s = BOX[weight]
    m = (b + t) // 2 + 6            # waist sits a touch above centre
    inset = 22                      # top loop is a little narrower than the bottom loop
    rects = [
        # bottom loop
        (l + s, b, r - s, b + s),                     # bottom bar
        (l, b + s, l + s, m - s // 2),                # left side
        (r - s, b + s, r, m - s // 2),                # right side
        # waist
        (l + s, m - s // 2, r - s, m + s // 2),
        # top loop (inset)
        (l + inset, m + s // 2, l + inset + s, t - s),
        (r - inset - s, m + s // 2, r - inset, t - s),
        (l + inset + s, t - s, r - inset - s, t),     # top bar
    ]
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1 in rects:
        pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1)); pen.lineTo((x1, y0)); pen.closePath()
    return pen.glyph()


def build(weight):
    src = TTFont(SRC[weight])
    adv = src['hmtx']['eight'][0]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'eight'])
    fb.setupCharacterMap({0x38: 'eight'})
    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({'.notdef': empty, 'eight': eight_glyph(weight)})
    l = BOX[weight][0]
    fb.setupHorizontalMetrics({'.notdef': (adv, 0), 'eight': (adv, l)})
    hh = src['hhea']
    fb.setupHorizontalHeader(ascent=hh.ascent, descent=hh.descent)
    fb.setupNameTable({'familyName': 'RC8', 'styleName': 'Regular' if weight < 600 else 'Bold'})
    os2 = src['OS/2']
    fb.setupOS2(sTypoAscender=os2.sTypoAscender, sTypoDescender=os2.sTypoDescender, sTypoLineGap=os2.sTypoLineGap,
                usWinAscent=os2.usWinAscent, usWinDescent=os2.usWinDescent, usWeightClass=weight,
                sxHeight=getattr(os2, 'sxHeight', 0), sCapHeight=getattr(os2, 'sCapHeight', 0), fsSelection=0x40)
    fb.setupPost()
    path = f'rc8-{weight}.ttf'
    fb.save(path)
    return path


if __name__ == '__main__':
    css = []
    for w, rng in ((500, '100 599'), (700, '600 900')):
        data = base64.b64encode(open(build(w), 'rb').read()).decode()
        css.append("@font-face{font-family:'RC8';src:url(data:font/ttf;base64,%s) format('truetype');font-weight:%s;unicode-range:U+0038;font-display:block}" % (data, rng))
    open('rc8.css', 'w').write('\n'.join(css))
    print('ok', sum(len(c) for c in css), 'bytes of CSS')
