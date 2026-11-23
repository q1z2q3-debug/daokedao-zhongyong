#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《中庸》全书自检：体例、字数（短/长双档）、脚注、四层标记、图、版本、章表、站点。

用法：python3 scripts/check_book.py
退出码：0 全过；1 有 FAIL。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, "book")
DOCS = os.path.join(ROOT, "docs")
FIG = os.path.join(ROOT, "assets", "fig")
BASE_FILE = os.path.join(ROOT, "data", "底本", "中庸章句·三十三章原文.md")
VERSION = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
CFG = json.load(open(os.path.join(BOOK, "chapters.json"), encoding="utf-8"))
CH = CFG["chapters"]

SECTIONS = ["本章导读", "经文", "字义与句读", "今译", "章旨", "朱子注",
            "分寸与边界", "义理", "时代之问", "跨典", "存疑", "双卡与图"]
COLORS = {"#F7F4EE", "#25211D", "#994433", "#7C6D5C", "#DCD5C8", "#FCFAF6"}
BANDS = {"短": (1500, 2500), "长": (4000, 6000)}
FU_PAGES = ["fu/index.html", "fu/01-guben.html", "fu/02-duizhao.html",
            "fu/03-jiaokan.html", "fu/04-cunyi.html", "fu/05-suoyin.html", "fu/06-zhangzhi.html"]

fails, warns = [], []


def fail(m):
    fails.append(m)


def warn(m):
    warns.append(m)


def cjk(t):
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def strip_fm(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e > 0:
            return t[e + 4:]
    return t


def body_chars(md):
    t = strip_fm(md)
    t = re.split(r"\n## 少年读", t)[0]
    t = re.sub(r"(?m)^\[\^[0-9]+\]:.*$", "", t)
    return cjk(t)


BASE = None


def load_base():
    out = {}
    if not os.path.exists(BASE_FILE):
        fail("缺底本 %s" % BASE_FILE)
        return out
    t = open(BASE_FILE, encoding="utf-8").read()
    for p in re.split(r"\n## ", t)[1:]:
        head = p.split("\n")[0].strip()
        key = head.split("　")[0].split(" ")[0]
        body = "\n".join(p.split("\n")[1:])
        body = re.sub(r"〔.*?〕", "", body, flags=re.S)
        body = re.sub(r"(?m)^原文数:.*$", "", body)
        body = body.replace("【经】", "")
        out[key] = re.sub(r"[^\u4e00-\u9fff]", "", body)
    return out


def check_text(ch):
    global BASE
    if BASE is None:
        BASE = load_base()
    base = BASE.get(ch["id"])
    if not base:
        fail("%s 底本找不到该章" % ch["id"])
        return
    p = os.path.join(ROOT, ch["file"])
    if not os.path.exists(p):
        return
    md = open(p, encoding="utf-8").read()
    if "## 二　经文" not in md:
        return
    sec = md.split("## 二　经文")[1].split("## 三　")[0]
    quoted = "".join(re.findall(r"(?m)^【经】\s*(.+)", sec))
    quoted = re.sub(r"\[\^[0-9]+\]", "", quoted)
    q = re.sub(r"[^\u4e00-\u9fff]", "", quoted)
    if q != base:
        for i in range(min(len(q), len(base))):
            if q[i] != base[i]:
                fail("%s 经文与底本不符：第 %d 字「%s」≠「%s」（…%s…）"
                     % (ch["id"], i + 1, q[i], base[i], q[max(0, i - 8):i + 8]))
                return
        fail("%s 经文长度与底本不符：%d vs %d" % (ch["id"], len(q), len(base)))


def check_chapter(ch):
    path = os.path.join(ROOT, ch["file"])
    if not os.path.exists(path):
        fail("%s 缺文件 %s" % (ch["id"], ch["file"]))
        return
    md = open(path, encoding="utf-8").read()
    fm = md.split("---")[1] if md.startswith("---") else ""
    if "version: %s" % VERSION not in fm:
        fail("%s front matter version 不是 %s" % (ch["id"], VERSION))
    if ("id: %s" % ch["id"]) not in fm:
        fail("%s front matter id 不符" % ch["id"])
    if ch["章号"] not in fm:
        fail("%s front matter 章号不符" % ch["id"])

    heads = re.findall(r"(?m)^##\s+(.+)$", md)
    names = [re.sub(r"^[一二三四五六七八九十]+　", "", h).strip() for h in heads]
    core = [n for n in names if n in SECTIONS]
    if core != SECTIONS:
        fail("%s 十二节顺序/名称不符：%s" % (ch["id"], "、".join(core)))
    extra = [n for n in names if not (n in SECTIONS or n == "少年读" or n.startswith("附论"))]
    if extra:
        fail("%s 有多余节：%s" % (ch["id"], extra))

    # 空节检查：每节至少 8 个汉字
    parts = re.split(r"(?m)^## [一二三四五六七八九十]+　", md)
    for i, name in enumerate(SECTIONS):
        if i + 1 < len(parts):
            seg = parts[i + 1].split("\n## ")[0]
            if cjk(seg) < 8 and "此章不涉" not in seg:
                fail("%s 第 %d 节「%s」空节" % (ch["id"], i + 1, name))
    if "TODO" in md or "待补" in md:
        fail("%s 有 TODO／待补" % ch["id"])

    check_text(ch)

    n = body_chars(md)
    band = BANDS.get(ch.get("档", "短"), (1500, 2500))
    if not (band[0] <= n <= band[1]):
        fail("%s 正文 %d 字，不在%s档 %d–%d" % (ch["id"], n, ch.get("档"), band[0], band[1]))

    defined = re.findall(r"(?m)^\[\^([0-9]+)\]:", md)
    used = set(re.findall(r"\[\^([0-9]+)\](?!:)", md))
    if len(defined) < 5:
        fail("%s 脚注定义 %d 条 < 5" % (ch["id"], len(defined)))
    unused = [d for d in defined if d not in used]
    if unused:
        fail("%s 脚注被定义未引用：%s（pandoc 会丢弃）" % (ch["id"], unused))

    if md.count("【义】") + md.count("【用】") < 8:
        fail("%s 【义】+【用】不足 8 段" % ch["id"])
    if "【经】" not in md:
        fail("%s 无【经】原文标记" % ch["id"])
    dui = len(re.findall(r"(?m)^-\s+.+→.+$", md))
    if dui < 4:
        fail("%s 双卡 %d 对 < 4" % (ch["id"], dui))

    if not re.search(r"## 少年读", md):
        fail("%s 缺少年读" % ch["id"])
    else:
        sw = re.split(r"## 少年读", md)[1].split("## 附论")[0]
        if not re.search(r"一件事", sw) or len(re.findall(r"(?m)^\d\.\s", sw)) != 3:
            fail("%s 少年读缺「一件事」或三个问题" % ch["id"])
        sc = cjk(re.sub(r"\*\*[^*]+\*\*", "", sw.split("**一件事")[0]))
        if not (100 <= sc <= 200):
            fail("%s 少年读散文 %d 字，不在 100–200" % (ch["id"], sc))

    svg = os.path.join(FIG, ch["id"].lower() + ".svg")
    if not os.path.exists(svg):
        if "此章无图" not in md:
            fail("%s 缺义理图且未写「此章无图」" % ch["id"])
    else:
        s = open(svg, encoding="utf-8").read()
        if "<title>" not in s or "<desc>" not in s:
            fail("%s 图缺 title/desc" % ch["id"])
        if "viewBox" not in s:
            fail("%s 图缺 viewBox" % ch["id"])
        if re.search(r'<svg[^>]*(width|height)="[0-9]', s):
            fail("%s 图写了固定 width/height" % ch["id"])
        bad = set(re.findall(r"#[0-9A-Fa-f]{6}", s)) - COLORS
        if bad:
            fail("%s 图用非规定色：%s" % (ch["id"], bad))
        small = [int(x) for x in re.findall(r'font-size="([0-9]+)"', s) if int(x) < 11]
        if small:
            fail("%s 图字号 <11：%s" % (ch["id"], small))
        if "<text" not in s:
            fail("%s 图无 text" % ch["id"])


def check_front():
    for f in ("序-为什么读中庸.md", "前言-读中庸之前.md"):
        p = os.path.join(BOOK, f)
        if not os.path.exists(p):
            fail("缺卷首 %s" % f)
    p = os.path.join(BOOK, "序-为什么读中庸.md")
    if os.path.exists(p):
        n = cjk(strip_fm(open(p, encoding="utf-8").read()))
        if not (700 <= n <= 1050):
            fail("序 %d 字，不在 700–1000" % n)


def check_version():
    for f, pat in (("README.md", r"v?%s" % re.escape(VERSION)),
                   ("CHANGELOG.md", r"%s" % re.escape(VERSION)),
                   ("CITATION.cff", r"version: %s" % re.escape(VERSION))):
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            fail("缺 %s" % f)
        elif not re.search(pat, open(p, encoding="utf-8").read()):
            fail("%s 未写版本 %s" % (f, VERSION))


def check_toc():
    p = os.path.join(BOOK, "章表.md")
    if not os.path.exists(p):
        fail("缺章表.md")
        return
    t = open(p, encoding="utf-8").read()
    for ch in CH:
        if ch["id"] not in t or ch["file"] not in t:
            fail("章表.md 与 chapters.json 不一致：%s" % ch["id"])
        m = re.search(r"%s.*?\| *(\d+) *\|" % ch["id"], t)
        if m and int(m.group(1)) != ch["原文数"]:
            fail("章表 %s 原文数 %s ≠ chapters.json %d" % (ch["id"], m.group(1), ch["原文数"]))


def check_appendix():
    files = sorted(f for f in os.listdir(BOOK) if f.startswith("附录-") and f.endswith(".md"))
    if len(files) != 7:
        fail("附录文件 %d 个，应为 7 个（00 索引＋01 古本＋02 对照＋03 校勘＋04 存疑＋05 关键字＋06 章旨表）" % len(files))


def check_site():
    for p in ("index.html", "book.html", "sitemap.xml", "robots.txt", "llms.txt",
              "404.html", "favicon.svg"):
        if not os.path.exists(os.path.join(DOCS, p)):
            fail("站点缺 %s" % p)
    nfig = 0
    for ch in CH:
        if not os.path.exists(os.path.join(DOCS, ch["page"])):
            fail("站点缺章页 %s" % ch["page"])
            continue
        page = open(os.path.join(DOCS, ch["page"]), encoding="utf-8").read()
        if "../%s" % ch["fig"] not in page:
            fail("%s 页缺 SVG 直链" % ch["id"])
        if VERSION not in page:
            fail("%s 页脚版本不符" % ch["id"])
    for f in FU_PAGES:
        if not os.path.exists(os.path.join(DOCS, f)):
            fail("站点缺附录页 %s" % f)
    idx = open(os.path.join(DOCS, "index.html"), encoding="utf-8").read()
    if idx.count('href="ch/') < len(CH):
        fail("首页目录链不足 %d 条" % len(CH))
    sm = open(os.path.join(DOCS, "sitemap.xml"), encoding="utf-8").read()
    for ch in CH:
        if ch["page"] not in sm:
            fail("sitemap 缺 %s" % ch["page"])


def check_fig_count():
    n = len([f for f in os.listdir(FIG) if f.endswith(".svg")]) if os.path.isdir(FIG) else 0
    if n < 30:
        fail("全书图 %d 张 < 30" % n)


def main():
    for ch in CH:
        check_chapter(ch)
    check_front()
    check_version()
    check_toc()
    check_appendix()
    check_fig_count()
    check_site()
    print(json.dumps({"version": VERSION, "chapters": len(CH),
                      "FAIL": fails, "WARN": warns}, ensure_ascii=False, indent=1))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
