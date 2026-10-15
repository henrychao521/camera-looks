#!/usr/bin/env python3
"""把三台相機的配方 JSON 與 GR IV 刷機清單組成單一 HTML 頁面。

用法：python3 build.py   → 產出 dist/index.html
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "dist" / "index.html"   # 給 Artifact 發布
SITE = ROOT / "docs" / "index.html"  # 給 GitHub Pages（main 分支 /docs）
CAMERAS = [("gr4", "GR IV"), ("gr3x", "GR IIIx"), ("rx100", "RX100 VII")]


def inline(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = t.replace("〔通用做法〕", '<span class="tag-generic">通用做法</span>')
    return t


def checklist_html(md: str) -> str:
    """只處理清單檔用到的語法：標題、引言、勾選項、一般項目、程式碼區塊、分隔線。"""
    out, in_list, in_code, code_buf = [], None, False, []
    sec = 0
    item_n = 0

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                out.append('<pre class="cmd"><code>' + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf, in_code = [], False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(stripped)
            continue
        if not stripped:
            continue
        if stripped.startswith("# "):
            continue  # 頁面自己有標題
        if stripped == "---":
            close_list()
            continue
        if stripped.startswith("> "):
            close_list()
            out.append(f'<p class="note">{inline(stripped[2:])}</p>')
            continue
        if stripped.startswith("## "):
            close_list()
            if sec:
                out.append("</section>")
            sec += 1
            title = stripped[3:]
            m = re.match(r"(\d+)\.\s*(.*)", title)
            num, name = (m.group(1), m.group(2)) if m else ("", title)
            out.append(f'<section class="ck-sec" id="ck-{sec}"><h3><span class="ck-num">{num}</span>{inline(name)}'
                       f'<span class="ck-prog" data-sec="{sec}"></span></h3>')
            continue
        m = re.match(r"(?:-|\d+\.)\s+\[ \]\s+(.*)", stripped)
        if m:
            if in_list != "ul":
                close_list()
                out.append('<ul class="ck-list">')
                in_list = "ul"
            item_n += 1
            cid = f"ck{item_n}"
            out.append(f'<li class="ck-item"><input type="checkbox" id="{cid}" data-sec="{sec}">'
                       f'<label for="{cid}">{inline(m.group(1))}</label>')
            continue
        m = re.match(r"-\s+(.*)", stripped)
        if m:
            indent = len(line) - len(line.lstrip())
            if indent and in_list:
                out.append(f'<div class="ck-sub">{inline(m.group(1))}</div>')
                continue
            if in_list != "ul-plain":
                close_list()
                out.append('<ul class="plain">')
                in_list = "ul-plain"
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        # 一般段落，或縮排的接續說明
        if in_list and line.startswith("  "):
            out.append(f'<div class="ck-sub">{inline(stripped)}</div>')
        else:
            close_list()
            out.append(f"<p>{inline(stripped)}</p>")
    close_list()
    if sec:
        out.append("</section>")
    return "\n".join(out)


def main():
    cams = {}
    for key, _ in CAMERAS:
        cams[key] = json.loads((DATA / f"{key}.json").read_text(encoding="utf-8"))
    ck = checklist_html((ROOT / "GR4_LUTSmith_檢查與還原清單.md").read_text(encoding="utf-8"))
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(cams, ensure_ascii=False).replace("</", "<\\/")
    page = tpl.replace("/*__DATA__*/null", payload).replace("<!--__CHECKLIST__-->", ck)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    # GitHub Pages 版：Artifact 發布時會自動包外殼，Pages 要自己補完整文件結構
    site = ("<!doctype html>\n<html lang=\"zh-Hant-TW\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            "<meta name=\"description\" content=\"Ricoh GR IV、GR IIIx 與 Sony RX100 VII 的機內畫面配方，附出處與官方參數表，以及 GR IV 刷 LUTSmith 的檢查與還原清單。\">\n"
            "<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
            "</head>\n<body>\n" + page + "\n</body>\n</html>\n")
    SITE.parent.mkdir(exist_ok=True)
    SITE.write_text(site, encoding="utf-8")
    (SITE.parent / ".nojekyll").write_text("", encoding="utf-8")
    n = sum(len(c["recipes"]) for c in cams.values())
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB, {n} recipes)")


if __name__ == "__main__":
    main()
