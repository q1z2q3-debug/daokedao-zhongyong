#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建《润泽说 道可道之中庸》站点（docs/）。

源：book/*.md（一章一文件，三十三章）+ assets/fig/<章号小写>.svg
产出：docs/index.html（首页与目录）、docs/book.html（封面·扉页·前言）、
      docs/ch/<章号小写>.html（33 章）、docs/fu/*.html（附录）、
      docs/fig/*.svg（义理图直链）、favicon.svg、sitemap.xml、robots.txt、llms.txt、404.html
用法：python3 scripts/build_site.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
book = os.path.join(ROOT, "book")
docs = os.path.join(ROOT, "docs")
figs = os.path.join(ROOT, "assets", "fig")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import daokedao_book as kit  # noqa: E402

SITE = "https://q1z2q3-debug.github.io/daokedao-zhongyong"
VERSION = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
DATE = "2026-11-23"
CFG = json.load(open(os.path.join(book, "chapters.json"), encoding="utf-8"))
CH = CFG["chapters"]

SERIES = [
    ("道德经", "https://q1z2q3-debug.github.io/runze-daodejing/"),
    ("论语", "https://q1z2q3-debug.github.io/daokedao-lunyu/"),
    ("千字文", "https://q1z2q3-debug.github.io/daokedao-qianziwen/"),
    ("三字经", "https://q1z2q3-debug.github.io/daokedao-sanzijing/"),
    ("甲骨文", "https://q1z2q3-debug.github.io/daokedao-jiaguwen/"),
    ("心经", "https://q1z2q3-debug.github.io/daokedao-xinjing/"),
    ("金刚经", "https://q1z2q3-debug.github.io/daokedao-jingang/"),
    ("坛经", "https://q1z2q3-debug.github.io/daokedao-tanjing/"),
    ("阴符经", "https://q1z2q3-debug.github.io/daokedao-yinfujing/"),
    ("易传", "https://q1z2q3-debug.github.io/daokedao-yijing/"),
    ("庄子", "https://q1z2q3-debug.github.io/daokedao-zhuangzi/"),
]

FU = [
    ("fu/index.html", "附录首页", "附录首页", "六件附录：古本、对照、校勘、存疑、索引、章旨表"),
    ("fu/01-guben.html", "附录一", "古本全文", "《礼记·中庸》古本全文（郑注孔疏本）"),
    ("fu/02-duizhao.html", "附录二", "古本—朱子本对照表", "逐段对照：位置、分章、合章与拆章"),
    ("fu/03-jiaokan.html", "附录三", "校勘记", "异文与异读，逐条出注"),
    ("fu/04-cunyi.html", "附录四", "存疑录", "全书未决处，按章归并"),
    ("fu/05-suoyin.html", "附录五", "关键字索引", "中庸、诚、性、命、天、德等"),
    ("fu/06-zhangzhi.html", "附录六", "三十三章章旨表", "一章一句：章旨、关键字、所引诗书"),
]

CSS = """
:root{--paper:#F7F4EE;--paper2:#FCFAF6;--ink:#25211D;--ink2:#3B352F;
  --ochre:#994433;--brown:#7C6D5C;--line:#DCD5C8}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#F7F4EE;color:#25211D;
  font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",serif;
  font-size:17px;line-height:1.95;letter-spacing:.01em}
a{color:#994433;text-decoration:none;border-bottom:1px solid rgba(153,68,51,.28)}
a:hover{border-bottom-color:#994433}
.bar{background:#FCFAF6;border-bottom:1px solid #DCD5C8;padding:9px 16px;
  font-family:"Noto Sans SC","PingFang SC",sans-serif;font-size:12px;letter-spacing:.1em;
  color:#7C6D5C;display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.wrap{max-width:780px;margin:0 auto;padding:34px 22px 64px}
h1.title{font-size:40px;line-height:1.4;margin:0 0 10px;font-weight:600;letter-spacing:.1em}
h1.ch,h2.ch{font-size:30px;letter-spacing:.16em;margin:6px 0 6px;font-weight:600}
h2{font-size:23px;margin:44px 0 8px;letter-spacing:.14em;font-weight:600}
h2 small{font-size:12px;color:#7C6D5C;letter-spacing:.1em;margin-left:10px;font-weight:400}
h3{font-size:15px;letter-spacing:.08em;color:#994433;margin:26px 0 6px;
  padding-bottom:4px;border-bottom:1px solid #DCD5C8}
p{margin:0 0 1.05em;text-align:justify}
blockquote{margin:1.1em 0;padding:14px 18px;background:#FCFAF6;
  border-left:3px solid #DCD5C8;color:#3B352F}
blockquote p{margin:0 0 .7em}
blockquote p:last-child{margin-bottom:0}
.mk{display:inline-block;font-size:11px;line-height:1.6;letter-spacing:.08em;
  padding:0 5px;margin-right:6px;border:1px solid #DCD5C8;border-radius:2px;
  vertical-align:2px;font-family:"Noto Sans SC","PingFang SC",sans-serif}
.mk.k{color:#994433;border-color:#D8B9AD;background:#FBF1EC}
.mk.z{color:#7C6D5C;border-color:#DCD5C8;background:#FCFAF6}
.mk.y{color:#25211D;border-color:#BDB4A6;background:#F5F1E8}
.mk.yong{color:#3B352F;border-color:#C9BFAF;background:#F1ECE2}
.figbox{margin:26px 0 8px;padding:14px;background:#FCFAF6;border:1px solid #DCD5C8}
.figbox svg,.fig{width:100%;height:auto;max-width:720px;display:block;margin:0 auto}
.figlink{display:block;text-decoration:none;color:inherit}
.figcap a{color:#7C6D5C;text-decoration:none;border-bottom:1px solid #DCD5C8}
.figcap{font-size:12px;color:#7C6D5C;text-align:center;margin-top:8px;letter-spacing:.06em}
.lead{font-size:13.5px;color:#7C6D5C;margin:0 0 16px;letter-spacing:.03em}
.list{border-top:1px solid #DCD5C8}
.item{padding:16px 0 14px;border-bottom:1px solid #E7E0D4}
.item .no{font-size:11.5px;letter-spacing:.22em;color:#994433;
  font-family:"Noto Sans SC",sans-serif;margin-bottom:5px}
.item .t{font-size:19px;letter-spacing:.03em;margin:0 0 4px}
.item .s{font-size:13px;color:#5C5348;margin:0 0 6px}
.item .k{font-size:12.5px;color:#7C6D5C}
.rows{border-top:1px solid #DCD5C8;margin-top:6px}
.row{display:grid;grid-template-columns:132px 1fr;gap:14px;padding:13px 0;
  border-bottom:1px solid #E7E0D4}
.row .kk{font-size:12.5px;color:#994433;letter-spacing:.12em;
  font-family:"Noto Sans SC",sans-serif}
.row .vv{font-size:15px}
.series-grid{display:grid;grid-template-columns:repeat(4,1fr);
  gap:1px;margin-top:8px;border-top:1px solid #DCD5C8;border-left:1px solid #E7E0D4}
.series-grid a{display:block;padding:11px 12px;font-size:14px;border:0;
  border-right:1px solid #E7E0D4;border-bottom:1px solid #E7E0D4;background:#FCFAF6}
.series-grid a small{display:block;font-size:11px;color:#8E8071;letter-spacing:.08em;margin-top:2px}
.btn{display:inline-block;border:1px solid #994433;color:#994433;padding:6px 16px;
  font-size:13px;letter-spacing:.12em;margin-top:10px}
.pn{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;
  margin:48px 0 0;padding:16px 0;border-top:1px solid #DCD5C8;
  font-size:13px;letter-spacing:.06em}
.pn a{border:0}
.pn .mid{text-align:center;color:#7C6D5C}
.pn .right{text-align:right}
.xu-sep{text-align:center;color:#7C6D5C;letter-spacing:.4em;margin:44px 0 40px;font-size:15px}
.foot{margin-top:36px;padding-top:14px;border-top:1px solid #DCD5C8;
  font-size:12px;color:#7C6D5C;line-height:2}
.foot a{margin-right:12px}
aside.footnotes,section.footnotes{font-size:13px;color:#3B352F;border-top:1px solid #DCD5C8;margin-top:40px;padding-top:6px}
aside.footnotes li p,section.footnotes li p{margin:.4em 0}
aside.footnotes hr,section.footnotes hr{display:none}
aside.footnotes ol,section.footnotes ol{padding-left:1.6em}
sup.fn a{font-size:11px;color:#994433;text-decoration:none;padding:0 1px}
a,code,td,th{overflow-wrap:anywhere;word-break:break-word}
ol,ul{padding-left:1.3em}
table.t{width:100%;border-collapse:collapse;margin:16px 0;table-layout:fixed;
  font-size:14px;border-top:1px solid #DCD5C8}
table.t th,table.t td{border-bottom:1px solid #E7E0D4;padding:9px 8px;text-align:left;
  vertical-align:top;word-break:break-word}
table.t th{color:#994433;font-weight:600;letter-spacing:.08em;background:#FCFAF6}
@media (max-width:640px){
  .wrap{padding:24px 16px 52px}
  h1.title{font-size:27px;letter-spacing:.05em}
  h1.ch,h2.ch{font-size:23px;letter-spacing:.08em}
  h2{font-size:19px;margin:34px 0 6px;letter-spacing:.06em}
  .row{grid-template-columns:1fr;gap:4px}
  .bar{font-size:11.5px;letter-spacing:.04em}
  .pn{grid-template-columns:1fr 1fr;row-gap:8px}
  .pn .mid{display:none}
  table.t{font-size:12.5px}
  .series-grid{grid-template-columns:1fr 1fr}
  .figbox{padding:8px 0 4px;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .figbox svg{width:620px;max-width:none;margin:0 4px}
  .figcap{font-size:11.5px;padding:0 8px}
}
""" + kit.COVER_CSS + kit.FIG_CSS + "@media (max-width:640px){" + kit.COVER_MQ + "}"


def shell(title, desc, body, canonical="", prefix=""):
    can = '<link rel="canonical" href="%s">' % canonical if canonical else ""
    from urllib.parse import quote
    fav = "data:image/svg+xml," + quote(FAVICON, safe="")
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="author" content="润泽">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="book">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:site_name" content="润泽说 道可道">
%s<link rel="icon" href="%s" type="image/svg+xml">
<style>%s</style>
</head>
<body>
%s
</body>
</html>
""" % (title, desc, title, desc, can, fav, CSS, body)


def strip_fm(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[end + 4:].lstrip("\n")
    return text


def fm_value(text, key):
    m = re.search(r"^%s:\s*(.+)$" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else ""


def prep_notes(text):
    """pandoc 会给同一脚注的每次引用各生成一条，改为自建编号：一注一号，多处引用共用。"""
    defs, body = {}, []
    for line in text.split("\n"):
        m = re.match(r"^\[\^([^\]]+)\]:\s*(.+)$", line)
        if m:
            t = re.sub(r"`([^`]+)`", r"<code>\1</code>", m.group(2))
            defs[m.group(1)] = t
        else:
            body.append(line)
    txt = "\n".join(body)
    order = []
    for m in re.finditer(r"\[\^([^\]]+)\]", txt):
        if m.group(1) in defs and m.group(1) not in order:
            order.append(m.group(1))
    num = {k: i + 1 for i, k in enumerate(order)}
    txt = re.sub(r"\[\^([^\]]+)\]",
                 lambda m: ('<sup class="fn"><a href="#fn%s">%d</a></sup>'
                            % (num[m.group(1)], num[m.group(1)]))
                 if m.group(1) in num else m.group(0), txt)
    lis = "".join('<li id="fn%d"><p>%s　<a class="footnote-back" href="#fn%d">↩</a></p></li>'
                  % (num[k], defs[k], num[k]) for k in order)
    if not lis:
        return txt
    return txt + ('\n\n<aside class="footnotes"><ol>%s</ol></aside>\n' % lis)


def md2html(text):
    frag = subprocess.run(
        ["pandoc", "-f", "markdown+pipe_tables", "-t", "html5", "--no-highlight"],
        input=prep_notes(strip_fm(text)).encode("utf-8"), stdout=subprocess.PIPE, check=True,
    ).stdout.decode()
    frag = frag.replace("<h1", "<h1 class=\"ch\"", 1)
    for tag, cls in (("经", "k"), ("注", "z"), ("义", "y"), ("用", "yong")):
        frag = frag.replace("【%s】" % tag, '<span class="mk %s">%s</span>' % (cls, tag))
    return frag


def fig_html(ch):
    path = os.path.join(figs, ch["id"].lower() + ".svg")
    if not os.path.exists(path):
        return ""
    svg = open(path, encoding="utf-8").read()
    if svg.lstrip().startswith("<?xml"):
        svg = svg.lstrip()[svg.lstrip().index("?>") + 2:].lstrip()
    svg = re.sub(r"<svg ", '<svg class="fig" ', svg, count=1)
    return ('<div class="figbox"><a class="figlink" href="../fig/%s.svg" target="_blank" '
            'rel="noopener" title="点开看大图">%s</a>'
            '<div class="figcap">图 · %s 义理图　%s　<a href="../fig/%s.svg" target="_blank" '
            'rel="noopener">点图放大</a></div></div>'
            % (ch["id"].lower(), svg, ch["章号"], ch["章题"], ch["id"].lower()))


def bar(left_html, right=""):
    return '<div class="bar"><div>%s</div><div>润 泽 说 · 道 可 道 之 中 庸　%s</div></div>' % (left_html, right)


def chapter_body(idx, ch):
    src = os.path.join(ROOT, ch["file"])
    if not os.path.exists(src):
        return None
    frag = md2html(open(src, encoding="utf-8").read())
    fig = fig_html(ch)
    if fig:
        frag = re.sub(r'(<h2[^>]*>少年读</h2>)', fig + r"\1", frag, count=1)
    else:
        print("[warn] 缺图：", ch["id"])
    prev_h = "../book.html" if idx == 0 else CH[idx - 1]["page"].split("/")[-1]
    prev_n = "卷首" if idx == 0 else CH[idx - 1]["章号"]
    if idx + 1 < len(CH):
        next_h, next_n = CH[idx + 1]["page"].split("/")[-1], CH[idx + 1]["章号"]
    else:
        next_h, next_n = "../fu/index.html", "附录"
    pn = ('<div class="pn"><div><a href="%s">← %s</a></div>'
          '<div class="mid"><a href="../index.html">目录</a>　<a href="../book.html">卷首</a></div>'
          '<div class="right"><a href="%s">%s →</a></div></div>'
          % (prev_h, prev_n, next_h, next_n))
    foot = ('<div class="foot"><div>润泽说 道可道之中庸 · %s　%s　v%s　（%s）</div>'
            '<div>底本：朱熹《四书章句集注·中庸章句》　参校：《礼记正义·中庸》郑玄注、孔颖达疏</div>'
            '<div><a href="../index.html">目录</a><a href="../book.html">卷首</a>'
            '<a href="../fu/index.html">附录</a><a href="https://github.com/q1z2q3-debug/daokedao-zhongyong">GitHub</a>'
            '<a href="../%s">义理图 SVG</a></div></div>' % (ch["章号"], ch["章题"], VERSION, DATE, ch["fig"]))
    body = bar('<a href="../index.html">← 目录</a>', ch["章号"]) + \
        '<div class="wrap">' + frag + pn + foot + "</div>"
    return shell("%s　%s｜润泽说 道可道之中庸" % (ch["章号"], ch["章题"]), ch["gist"], body,
                 "%s/%s" % (SITE, ch["page"]), "../")


def cover_block():
    return kit.cover(
        title="中庸",
        tag="三 十 三 章 · 全 本",
        seal="中",
        gatha_first=("天命之谓性", "率性之谓道"),
        gatha_second=("致中和", "天地位焉 万物育焉"),
        meta=["底本　朱熹《中庸章句》", "参校　《礼记正义》郑注孔疏", "体例　三十三章 · 每章少年读一段",
              "v" + VERSION + " · 二〇二六"],
    )


def frontis_block():
    return kit.frontis(
        title="润泽说 道可道之中庸",
        sub="中庸 · 通释读本（全本）",
        lines=[
            ("底本", "朱熹《四书章句集注·中庸章句》，三十三章"),
            ("参校", "《礼记正义·中庸》郑玄注、孔颖达疏（古本全文见附录一）"),
            ("体例", "一章一页；每章十二节，末附少年读一段；四层分离：经／注／义／用"),
            ("图", "义理图手写 SVG，一图一文件，纸墨五色"),
            ("章次", "朱子所分三十三章，短章短写、长章长写；章号固定不改"),
            ("版本", "v" + VERSION),
        ],
        seal="中",
    )


def toc_items():
    out = []
    for ch in CH:
        out.append('<div class="item"><div class="no">%s　原文 %d 字</div>'
                   '<div class="t"><a href="%s" style="border:0;color:#25211D">%s　%s</a></div>'
                   '<div class="s">%s</div><div class="k">%s</div></div>'
                   % (ch["章号"], ch["原文数"], ch["page"], ch["章号"], ch["章题"], ch["gist"], ch["首句"]))
    return "".join(out)


def fu_items():
    return "".join('<div class="item"><div class="no">%s</div><div class="t"><a href="%s" '
                   'style="border:0;color:#25211D">%s</a></div><div class="s">%s</div></div>'
                   % (no, href, name, desc) for href, no, name, desc in FU)


def build_index():
    total = sum(c["原文数"] for c in CH)
    body = bar('<span>首页 · 目录</span>', "v" + VERSION) + """
<div class="wrap">
%s
<div class="hd" style="padding:26px 0 0">
  <div class="series" style="font-size:12px;letter-spacing:.42em;color:#994433">润 泽 说 · 道 可 道</div>
  <h1 class="title">中庸 · 通释</h1>
  <p class="lead" style="font-size:15px">三十三章，一章一页；成人十二节可考，章末少年读一段可念。底本朱熹《中庸章句》，古本全文入附录。</p>
  <p class="lead">全书 <b>33</b> 章　原文 <b>%d</b> 字　版本 v%s　（%s）</p>
</div>

<h2>卷首语<small>为什么这样读</small></h2>
<p>《中庸》最容易被读成两句话：一句是「中庸就是不走极端」，一句是「诚就是真诚」。两句都太省。<b>本书先把「中庸」还原成「度」</b>——不是折中，是在两端之间找到此刻该站的那一点；再把「诚」还原成「自成」——不是对别人坦白，是自己对自己不欺。</p>
<p>全书的主线只有一条：<b>从「天命之谓性」到「无声无臭」</b>，人如何把自己这一份性，修成一件看得见的事。中间三十一章，都是这条线上的刻度。</p>

<h2>目录<small>三十三章 · 一章一页</small></h2>
<p class="lead">按朱子章次；每章十二节，末附少年读。点章号进阅读页。</p>
<div class="list">%s</div>

<h2>附录<small>古本 · 对照 · 校勘 · 存疑 · 索引 · 章旨</small></h2>
<p class="lead">朱子本为底，古本全文并陈；校勘逐条出，三十三章章旨一表可查。</p>
<div class="list">%s</div>

<h2>体例<small>四层分离，一章十二节</small></h2>
<div class="rows">
  <div class="row"><div class="kk">四层标记</div><div class="vv">【经】原文只抄底本；【注】注疏标明谁说的；【义】义理须指回原文字句；【用】今用不冒充原文。一段只归一层。</div></div>
  <div class="row"><div class="kk">十二节</div><div class="vv">本章导读、经文、字义与句读、今译、章旨、朱子注、分寸与边界、义理、时代之问、跨典、存疑、双卡与图。</div></div>
  <div class="row"><div class="kk">少年读</div><div class="vv">每章末一百至二百字，加一件事、三个问题；不删繁就简，只换一种说法。</div></div>
  <div class="row"><div class="kk">图</div><div class="vv">义理图手写 SVG，一图一文件；纸 #F7F4EE、墨 #25211D、赭 #994433、棕 #7C6D5C、线 #DCD5C8。</div></div>
  <div class="row"><div class="kk">存疑</div><div class="vv">注家分歧与本书未决处，一律入「存疑」，不写成定论；被否定的解读不销毁，另立存疑录。</div></div>
</div>

<h2>五步读法<small>前三步求真，后两步求活</small></h2>
<div class="rows">
  <div class="row"><div class="kk">一　校</div><div class="vv">校字：底本、异文、音读。</div></div>
  <div class="row"><div class="kk">二　境</div><div class="vv">还境：制度、称谓、引书的来历。</div></div>
  <div class="row"><div class="kk">三　义</div><div class="vv">立义：这一章要立的一个判断。</div></div>
  <div class="row"><div class="kk">四　疑</div><div class="vv">存疑：说不清就写出来。</div></div>
  <div class="row"><div class="kk">五　用</div><div class="vv">致用：在自己的世代里做一件。</div></div>
</div>

<h2>同系列<small>润泽说 · 道可道</small></h2>
<div class="series-grid">%s</div>
<a class="btn" href="book.html">从卷首读起（序 · 封面 · 扉页 · 前言）</a>

<div class="foot">
  <div>润泽说 道可道之中庸 · 通释　全本　v%s　（%s）</div>
  <div>底本：朱熹《四书章句集注·中庸章句》　参校：《礼记正义·中庸》郑玄注、孔颖达疏</div>
  <div>全书三十三章（朱子分章）；古本全文、对照表、章旨表见附录。许可：CC BY-NC-SA 4.0</div>
  <div><a href="https://github.com/q1z2q3-debug/daokedao-zhongyong">GitHub 仓库</a><a href="book.html">卷首</a><a href="sitemap.xml">站点地图</a></div>
</div>
</div>
""" % (cover_block(), total, VERSION, DATE, toc_items(), fu_items(),
       "".join('<a href="%s">%s<small>通释读本</small></a>' % (u, n) for n, u in SERIES),
       VERSION, DATE)
    open(os.path.join(docs, "index.html"), "w", encoding="utf-8").write(
        shell("润泽说 道可道之中庸 · 通释｜《中庸》全本读本",
              "《中庸》通释全本：三十三章，一章一页；每章十二节、末附少年读。底本朱熹《中庸章句》，古本全文、对照表、章旨表入附录。",
              body, SITE + "/"))


def build_book():
    xu = os.path.join(book, "序-为什么读中庸.md")
    pre = os.path.join(book, "前言-读中庸之前.md")
    xu_frag = md2html(open(xu, encoding="utf-8").read())
    pre_frag = md2html(open(pre, encoding="utf-8").read())
    body = bar('<a href="index.html">← 目录</a>', "卷首") + """
<div class="wrap" style="padding-bottom:0">
%s
%s
</div>
<div class="wrap" style="padding-top:0">
%s
<div class="xu-sep" aria-hidden="true">※　※　※</div>
%s
<div class="pn"><div><a href="index.html">← 目录</a></div><div class="mid">卷首</div>
<div class="right"><a href="%s">第一章 →</a></div></div>
<div class="foot"><div>润泽说 道可道之中庸 · 卷首　v%s　（%s）</div>
<div>底本：朱熹《中庸章句》　参校：《礼记正义·中庸》郑玄注、孔颖达疏</div></div>
</div>
""" % (cover_block(), frontis_block(), xu_frag, pre_frag, CH[0]["page"], VERSION, DATE)
    open(os.path.join(docs, "book.html"), "w", encoding="utf-8").write(
        shell("卷首：序 · 封面 · 扉页 · 前言｜润泽说 道可道之中庸",
              "《中庸》通释卷首：序、封面、扉页与前言（为什么读、一条主线、两个本子、四层分离、十二节、五步读法、版本）。",
              body, SITE + "/book.html"))


def build_chapters():
    outdir = os.path.join(docs, "ch")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for i, ch in enumerate(CH):
        html = chapter_body(i, ch)
        if html is None:
            print("[warn] 缺章：", ch["file"])
            continue
        open(os.path.join(outdir, ch["id"].lower() + ".html"), "w", encoding="utf-8").write(html)
        n += 1
    print("章节页 %d / %d" % (n, len(CH)))


def build_fu():
    outdir = os.path.join(docs, "fu")
    os.makedirs(outdir, exist_ok=True)
    pages = []
    for f in sorted(os.listdir(book)):
        if not f.startswith("附录-") or not f.endswith(".md"):
            continue
        text = open(os.path.join(book, f), encoding="utf-8").read()
        page = fm_value(text, "page")
        if not page:
            print("[warn] 附录缺 page：", f)
            continue
        frag = md2html(text)
        pn = ('<div class="pn"><div><a href="../index.html">← 目录</a></div>'
              '<div class="mid"><a href="index.html">附录</a></div>'
              '<div class="right"><a href="../%s">第一章 →</a></div></div>' % CH[0]["page"])
        foot = ('<div class="foot"><div>润泽说 道可道之中庸 · 附录　v%s　（%s）</div>'
                '<div>底本：朱熹《中庸章句》　参校：《礼记正义·中庸》郑玄注、孔颖达疏</div></div></div>'
                % (VERSION, DATE))
        body = bar('<a href="../index.html">← 目录</a>',
                   fm_value(text, "章号") or "附录") + '<div class="wrap">' + frag + pn + foot
        out = os.path.join(docs, page)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(
            shell("%s｜润泽说 道可道之中庸附录" % fm_value(text, "title"),
                  fm_value(text, "desc") or "《中庸》附录", body, SITE + "/" + page, "../"))
        pages.append(page)
    print("附录页 %d：%s" % (len(pages), "、".join(pages)))
    return pages


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="10" fill="#994433"/>
<text x="32" y="45" font-size="40" text-anchor="middle" fill="#F7F4EE"
font-family="'Noto Serif SC','Songti SC',serif">中</text></svg>"""


def build_meta(pages):
    open(os.path.join(docs, "favicon.svg"), "w", encoding="utf-8").write(FAVICON)
    os.makedirs(os.path.join(docs, "fig"), exist_ok=True)
    for f in os.listdir(figs):
        if f.endswith(".svg"):
            shutil.copy(os.path.join(figs, f), os.path.join(docs, "fig", f))

    urls = [""] + ["book.html"] + [c["page"] for c in CH] + pages + \
        ["fig/" + c["id"].lower() + ".svg" for c in CH
         if os.path.exists(os.path.join(figs, c["id"].lower() + ".svg"))]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sm += "<url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq></url>\n" % (SITE, u, DATE)
    sm += "</urlset>\n"
    open(os.path.join(docs, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    open(os.path.join(docs, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % SITE)

    llms = "# 润泽说 道可道之中庸 · 通释\n\n"
    llms += "> 《中庸》全本读本，三十三章。底本朱熹《四书章句集注·中庸章句》，朱子所分三十三章。\n"
    llms += "> 卷首冠序一篇，次前言七节；正文每章十二节：导读、经文、字义与句读、今译、章旨、朱子注、分寸与边界、义理、时代之问、跨典、存疑、双卡与图；章末附少年读。\n"
    llms += "> 古本《礼记·中庸》全文、古本—朱子本对照、校勘记、存疑录、关键字索引、三十三章章旨表见附录。\n\n## 卷首\n"
    llms += "- 序 · 前言：%s/book.html\n" % SITE
    llms += "\n## 章\n"
    for c in CH:
        llms += "- %s｜%s｜%s：%s/%s\n" % (c["章号"], c["章题"], c["gist"], SITE, c["page"])
    llms += "\n## 附录\n"
    for href, no, name, desc in FU:
        llms += "- %s｜%s：%s/%s\n" % (no, name, SITE, href)
    llms += "\n## 引用\n润泽《润泽说 道可道之中庸》v%s，%s/\n" % (VERSION, SITE)
    llms += "\n## 义理口径\n中庸是度：两端之间，此刻该站的那一点，不是折中。诚是自成：自己对自己不欺，不是对别人坦白。\n"
    llms += "性、命、天：性为所受，命为所赋，天为所自；三者一名三面。不新造名相；凡解读须指回原文字句，指不回者入存疑。\n"
    open(os.path.join(docs, "llms.txt"), "w", encoding="utf-8").write(llms)

    open(os.path.join(docs, "404.html"), "w", encoding="utf-8").write(
        shell("未找到｜润泽说 道可道之中庸",
              "页面未找到。",
              bar('<a href="index.html">← 目录</a>') +
              '<div class="wrap"><h2 class="ch">未找到</h2><p>此页不在书中。</p>'
              '<p><a href="index.html">回目录</a></p></div>'))


def main():
    os.makedirs(docs, exist_ok=True)
    build_index()
    build_book()
    build_chapters()
    pages = build_fu()
    build_meta(pages)
    print("站点已生成：", docs)


if __name__ == "__main__":
    main()
