
#!/usr/bin/env python3
"""build.py · content.json -> <име>.html -> <име>.pdf -> проверки.

Употреба:   python3 build.py [content.json]
Нужно:      Google Chrome (или Chromium / Edge). Само стандартната библиотека на Python 3.
По желание: poppler (pdfinfo, pdffonts, pdftotext, pdftoppm) за автоматичните проверки и PNG на всяка страница.
            macOS: brew install poppler · Ubuntu: sudo apt install poppler-utils · Windows: conda install -c conda-forge poppler

Съдържанието живее в JSON с фиксирани слотове. Шаблонът не се пипа на ръка за всеки документ:
сменяте JSON, пускате build.py, гледате всяка страница.
"""
import html, json, os, pathlib, platform, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
FAIL = []                                    # причини да спрем; печатат се накрая


def esc(s):
    """Ескейпва текста и позволява само **удебелено**."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(str(s)))


def chip(c):
    return f'<span class="chip {c["kind"]}">{esc(c["text"])}</span>' if c else ""


# ---------- блокове: всеки тип има едно място и една форма ----------

def b_answer(b):
    return f'<div class="answer keep"><p>{esc(b["text"])}</p></div>'


def b_label(b):
    return f'<div class="label">{esc(b["text"])}</div>'


def b_text(b):
    return f'<p class="text">{esc(b["text"])}</p>'


def b_tiles(b):
    out = []
    for t in b["items"]:
        est = ' <span class="chip est">оценка</span>' if t.get("estimate") else ""
        out.append(f'<div class="tile"><div class="k">{esc(t["label"])}{est}</div>'
                   f'<div class="v">{esc(t["value"])}</div>'
                   f'<div class="n">{esc(t.get("note", ""))} {chip(t.get("chip"))}</div></div>')
    return f'<div class="tiles">{"".join(out)}</div>'


def num(s):
    """'21 600' / '€41 200' / '-4%' -> число (за проверка на сумите)."""
    s = str(s).replace("\u2212", "-").replace(",", ".")
    m = re.search(r"-?[\d\s\u00a0.]*\d", s)
    return float(re.sub(r"[\s\u00a0]", "", m.group(0))) if m else None


def b_table(b):
    cols, numc = b["columns"], set(b.get("num_cols", []))
    th = "".join(f'<th class="{"num" if i in numc else ""}" style="width:{w}">{esc(c)}</th>'
                 for i, (c, w) in enumerate(zip(cols, b.get("widths", ["auto"] * len(cols)))))
    rows = []
    for r_i, r in enumerate(b["rows"]):
        cls = "total" if b.get("total_row") and r_i == len(b["rows"]) - 1 else ""
        cls += " hl" if r_i == b.get("highlight_row") else ""
        tds = "".join(f'<td class="{"num" if i in numc else ""}">{esc(v)}</td>' for i, v in enumerate(r))
        rows.append(f'<tr class="{cls.strip()}">{tds}</tr>')
    # Билдърът проверява сумата сам: общият ред = сбора на редовете над него.
    for c in b.get("check_sum_cols", []):
        parts = [num(r[c]) for r in b["rows"][:-1]]
        total = num(b["rows"][-1][c])
        if None in parts or total is None or abs(sum(parts) - total) > 0.5:
            FAIL.append(f'таблица "{cols[0]}": колона "{cols[c]}" не се сумира ({sum(p or 0 for p in parts)} срещу {total})')
    return f'<table class="t keep"><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def b_bars(b):
    """Хоризонтални ленти като inline SVG. 1 единица в viewBox ~ 1 pt на листа."""
    items, W, LW, VW, row = b["items"], 505, 150, 70, 22
    vmax = max([i["value"] for i in items] + [b.get("ref", {}).get("value", 0)])
    bw = W - LW - VW
    H = row * len(items) + 18
    g = []
    for k, it in enumerate(items):
        y = k * row
        w = max(1, bw * it["value"] / vmax)
        fill = "var(--acc)" if it.get("highlight") else "#C9CCD3"
        g.append(f'<text x="0" y="{y + 13}" font-size="8.6" fill="#3A3E49">{esc(it["label"])}</text>'
                 f'<rect x="{LW}" y="{y + 3}" width="{w:.1f}" height="13" fill="{fill}"/>'
                 f'<text x="{LW + w + 5:.1f}" y="{y + 13}" font-size="8.6" font-weight="700" fill="#16181E">{esc(it["display"])}</text>')
    if "ref" in b:  # референтна линия, напр. цената на смяната; рисува се ПОД етикетите
        x = LW + bw * b["ref"]["value"] / vmax
        g.insert(0, f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H - 14}" stroke="#16181E" stroke-width=".8" stroke-dasharray="3 2"/>'
                 f'<text x="{x:.1f}" y="{H - 3}" font-size="7.4" fill="#6C7180" text-anchor="middle">{esc(b["ref"]["label"])}</text>')
    return (f'<div class="fig"><div class="cap">{esc(b["caption"])}</div>'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg></div>')


def b_hbars(b):
    """Хоризонтални ленти с нулева ос (за положителни и отрицателни стойности) като inline SVG."""
    items, W, LW, VW, row = b["items"], 505, 150, 62, 22
    lo = min(0, min(i["value"] for i in items))
    hi = max(0, max(i["value"] for i in items))
    bw = W - LW - 2 * VW
    sc = bw / (hi - lo)
    x0 = LW + VW + (0 - lo) * sc
    H = row * len(items) + 6
    g = []
    for k, it in enumerate(items):
        y = k * row
        w = max(1, abs(it["value"]) * sc)
        x = x0 if it["value"] >= 0 else x0 - w
        fill = "var(--acc)" if it.get("highlight") else "#C9CCD3"
        tx, anchor = (x0 + w + 4, "start") if it["value"] >= 0 else (x0 - w - 4, "end")
        g.append(f'<text x="0" y="{y + 13}" font-size="8.6" fill="#3A3E49">{esc(it["label"])}</text>'
                 f'<rect x="{x:.1f}" y="{y + 3}" width="{w:.1f}" height="13" fill="{fill}"/>'
                 f'<text x="{tx:.1f}" y="{y + 13}" font-size="8.6" font-weight="700" fill="#16181E" text-anchor="{anchor}">{esc(it["display"])}</text>')
    g.append(f'<line class="axis" x1="{x0:.1f}" y1="0" x2="{x0:.1f}" y2="{H - 4}"/>')
    return (f'<div class="fig"><div class="cap">{esc(b["caption"])}</div>'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg></div>')


def b_callout(b):
    est = ' <span class="chip est">оценка</span>' if b.get("estimate") else ""
    return f'<div class="callout"><b class="h">{esc(b["title"])}</b>{esc(b["text"])}{est}</div>'


def b_quote(b):
    return f'<div class="q"><p>„{esc(b["text"])}“</p><div class="by">{esc(b["by"])}</div></div>'


def b_steps(b):
    return '<ol class="steps">' + "".join(f"<li><span>{esc(s)}</span></li>" for s in b["items"]) + "</ol>"


def b_summary(b):
    return f'<div class="wa"><span class="tag">{esc(b["title"])}</span>{esc(b["text"])}</div>'


def b_source(b):
    return f'<p class="src"><b>Източник:</b> {esc(b["text"])}</p>'


def b_cols(b):
    return f'<div class="cols"><div>{render_blocks(b["left"])}</div><div>{render_blocks(b["right"])}</div></div>'


BLOCKS = {"answer": b_answer, "label": b_label, "text": b_text, "tiles": b_tiles, "table": b_table,
          "bars": b_bars, "hbars": b_hbars, "callout": b_callout, "quote": b_quote, "steps": b_steps, "summary": b_summary, "source": b_source, "cols": b_cols}
NUMERIC = {"tiles", "table", "bars", "hbars"}


def render_blocks(blocks):
    return "".join(BLOCKS[b["type"]](b) for b in blocks)


def flat_types(blocks):
    for b in blocks:
        yield b["type"]
        if b["type"] == "cols":
            yield from flat_types(b["left"] + b["right"])


# ---------- страници ----------

def cover(m, nums, total):
    sample = '<span class="sample">ПРИМЕРНИ ДАННИ</span>' if m.get("sample") else ""
    n = "".join(f'<div><b>{esc(x["value"])}</b><span>{esc(x["label"])}</span></div>' for x in nums)
    return (f'<section class="page cover"><div class="kick">{esc(m["brand"])} · {esc(m["doc_type"])}{sample}</div>'
            f'<h1>{esc(m["title"])}</h1><p class="sub">{esc(m["subtitle"])}</p><div class="bar"></div>'
            f'<div class="spacer"></div><div class="nums">{n}</div>'
            + (f'<p class="csrc">{esc(m["cover_source"])}</p>' if m.get("cover_source") else "") +
            f'<div class="line"><span>Подготвено за {esc(m["prepared_for"])} · {esc(m["prepared_by"])} · {esc(m["date"])}</span>'
            f'<span>1 / {total}</span></div></section>')


def page(m, p, n, total):
    types = list(flat_types(p["blocks"]))
    if NUMERIC & set(types) and "source" not in types:
        FAIL.append(f'страница {n}: има числа, но няма ред "Източник"')
    return (f'<section class="page"><div class="mast"><span class="kick">{esc(p["kicker"])}</span>'
            f'<span class="r">{esc(m["brand"])} · {esc(m["date"])}</span></div>'
            f'<h2>{esc(p["title"])}</h2>' + (f'<p class="lede">{esc(p["lede"])}</p>' if p.get("lede") else "")
            + render_blocks(p["blocks"])
            + f'<div class="foot"><span>{esc(m["brand"])} · {esc(m["doc_type"])}</span><span>{n} / {total}</span></div></section>')


def build_html(c):
    m = c["meta"]
    total = 1 + len(c["pages"])
    acc = "".join(f"--{k}:{m[v]};" for k, v in (("acc", "accent"), ("acc-t", "accent_tint"), ("acc-d", "accent_on_dark")) if m.get(v))
    body = cover(m, c["cover_numbers"], total) + "".join(page(m, p, i + 2, total) for i, p in enumerate(c["pages"]))
    return (f'<!doctype html><html lang="bg"><head><meta charset="utf-8"><title>{esc(m["title"])}</title>'
            f'<link rel="stylesheet" href="tokens.css"><style>:root{{{acc}}}</style></head><body>{body}</body></html>'), total


# ---------- печат и проверки ----------

def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    cands = {"Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                        "/Applications/Chromium.app/Contents/MacOS/Chromium",
                        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
             "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]}.get(platform.system(), [])
    for p in cands:
        if os.path.exists(p):
            return p
    if os.path.exists("/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"):  # Chromium в облачната среда
        return "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"):
        if shutil.which(name):
            return shutil.which(name)
    sys.exit("Няма Chrome. Инсталирайте Google Chrome или задайте пътя: CHROME=/път/до/chrome python3 build.py")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "content.json").resolve()
    c = json.loads(src.read_text(encoding="utf-8"))
    name = c["meta"]["file_name"]
    out_html = HERE / f"{name}.html"
    out_pdf = HERE.parent.parent / "reports" / f"{name}.pdf"   # PDF-ът отива в reports/
    doc, expected = build_html(c)
    out_html.write_text(doc, encoding="utf-8")

    # Собствен профил на Chrome: отвореният ви браузър заключва основния и печатът излиза с код 2 без PDF.
    with tempfile.TemporaryDirectory() as prof:
        if out_pdf.exists():
            out_pdf.unlink()
        subprocess.run([find_chrome(), "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        "--no-first-run", "--disable-background-networking", "--disable-component-update", "--disable-sync",
                        *([f"--user-data-dir={prof}"] if platform.system() in ("Darwin", "Windows") else []),
                        f"--print-to-pdf={out_pdf}", out_html.as_uri()],
                       capture_output=True, timeout=90)
    if not out_pdf.exists():
        sys.exit("Chrome не направи PDF.")
    print(f"PDF: {out_pdf.name} ({out_pdf.stat().st_size // 1024} KB)")

    if not shutil.which("pdfinfo"):
        print("! Няма poppler: автоматичните проверки са пропуснати. Отворете PDF-а и погледнете всяка страница.")
    else:
        pages = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(out_pdf)])).group(1))
        if pages != expected:  # препълнена страница = лист повече
            FAIL.append(f"страници: {pages}, очаквани {expected} (някоя страница е препълнена)")
        fonts = run(["pdffonts", str(out_pdf)])
        if "Type 3" in fonts:
            FAIL.append("Type 3 шрифт в PDF-а (променлив шрифт или липсващ глиф)")
        text = run(["pdftotext", "-layout", str(out_pdf), "-"])
        for pat, why in [(r"TODO|TBD|\[ПОПЪЛНИ\]|lorem", "незапълнено място"),
                         (r"\b\w+\.(?:md|py|json|csv|html)\b", "вътрешно име на файл"),
                         (r"undefined|NaN|None\b", "счупена стойност"),
                         ("\u2014", "дълго тире (заменете с точка, двоеточие или запетая)")]:
            for hit in sorted(set(re.findall(pat, text))):
                FAIL.append(f'{why}: "{hit}"')
        # Застъпване с футъра: при фиксирани страници препълването не добавя лист, а се врязва във футъра.
        # Футърът започва на ~10 mm + 2 mm отстъп + линия от долния ръб; текст на тялото не бива да стига под него.
        if shutil.which("pdftotext"):
            foot_top = 841.89 - 13 / 25.4 * 72
            for pg in range(2, pages + 1):
                bbox = run(["pdftotext", "-bbox", "-f", str(pg), "-l", str(pg), str(out_pdf), "-"])
                lows = sorted(float(y) for y in re.findall(r'yMax="([\d.]+)"', bbox))
                foot_line = max((y for y in lows if foot_top - 0.5 <= y <= foot_top + 10), default=None)  # редът на футъра
                touching = [y for y in lows if foot_top - 6 < y < foot_top - 0.5]   # по-малко от ~2 mm над футъра
                below = [y for y in lows if foot_line and y > foot_line + 1]        # текст ПОД футъра
                if touching or below:
                    FAIL.append(f"страница {pg}: текстът стига до футъра или под него")
        qc = HERE / "qc"
        qc.mkdir(exist_ok=True)
        for old in qc.glob(f"{name}-*.png"):
            old.unlink()
        if shutil.which("pdftoppm"):
            run(["pdftoppm", "-r", "50", "-png", str(out_pdf), str(qc / name)])
            print(f"PNG на всяка страница: {qc}/  -> ОТВОРЕТЕ И ПОГЛЕДНЕТЕ ВСЯКА")
        print(f"страници {pages}/{expected} · Type 3: {'ДА' if 'Type 3' in fonts else 'не'}")
    if out_pdf.stat().st_size > 2 * 1024 * 1024:
        print("! PDF-ът е над 2 MB: компресирайте снимките преди изпращане.")
    if FAIL:
        print("\nСПРИ. Поправете:\n- " + "\n- ".join(FAIL))
        sys.exit(1)
    print("Автоматичните проверки минаха. Остава вашият поглед върху всяка страница.")


if __name__ == "__main__":
    main()
