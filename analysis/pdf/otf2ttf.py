"""Превръща статични OTF (CFF) шрифтове в TTF, за да не ги печата Chrome като Type 3.
Употреба: python3 analysis/pdf/otf2ttf.py <вход.otf> <изход.ttf>"""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


def convert(src, dst, max_err=1.0):
    font = TTFont(src)
    gs = font.getGlyphSet()
    glyf = {}
    for name in font.getGlyphOrder():
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err, reverse_direction=True))
        glyf[name] = pen.glyph()
    font["loca"] = newTable("loca")
    font["glyf"] = t = newTable("glyf")
    t.glyphOrder = font.getGlyphOrder()
    t.glyphs = glyf
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    font["maxp"] = m = newTable("maxp")
    m.tableVersion = 0x00010000
    m.maxZones, m.maxTwilightPoints, m.maxStorage, m.maxFunctionDefs = 1, 0, 0, 0
    m.maxInstructionDefs, m.maxStackElements, m.maxSizeOfInstructions, m.maxComponentElements = 0, 0, 0, 0
    m.maxPoints = m.maxContours = m.maxCompositePoints = m.maxCompositeContours = m.maxComponentDepth = 0
    font["head"].indexToLocFormat = 0
    font["head"].glyphDataFormat = 0
    post = font["post"]
    post.formatType, post.extraNames, post.mapping = 2.0, [], {}
    post.glyphOrder = font.getGlyphOrder()
    font.sfntVersion = "\x00\x01\x00\x00"
    font.recalcBBoxes = True
    font.save(dst)


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
