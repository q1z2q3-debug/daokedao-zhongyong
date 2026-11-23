# -*- coding: utf-8 -*-
"""
润泽说 道可道 · 系列书共用排版件（v1.0）

只做一件事：把「封面页 / 扉页 / 譬喻图」这三类非正文页，按统一的纸墨规格生成 HTML，
供各书的 build_html.py 调用。正文排版、目录、构建流程仍由各书脚本自理。

用法（在 build_html.py 里）：

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import daokedao_book as kit

    CSS = CSS_BOOK + kit.COVER_CSS          # COVER_CSS 同时含 .cover 与 .frontis

    cover = kit.cover(
        title="六祖坛经",                    # 竖排书名（四字最稳）
        sub="六祖大师法宝坛经 · 通释",
        tag="十 品 圆 满",                   # 可留空
        seal="坛",                           # 单字印，赭底
        gatha_first=("菩提本无树", "明镜亦非台"),   # 右列（先读）
        gatha_second=("本来无一物", "何处惹尘埃"),  # 左列（后读）
        meta=["敦煌本 S.5475", "三才五蕴太极空杯", "阴阳太和", "二〇二六年十一月"],
    )
    frontis = kit.frontis(
        title="六祖坛经",
        sub="六祖大师法宝坛经 · 通释",
        author="润泽",
        lines=[("底本", "敦煌本《六祖坛经》S.5475"),
               ("体例", "十品 · 每品八段"),
               ("参证", "三才五蕴太极空杯 · 阴阳太和 · 和合之辨"),
               ("版本", "v1.2.0 · 二〇二六年十一月")],
        seal="坛",
    )

版式规矩（勿轻改，改则全书同改）：
  · 竖排只用于书名与偈语；正文一律横排。
  · 偈语分列两侧，右列先读（vertical-rl 的天然读序）。
  · 印章单字，赭底白字用于封面，朱线空心用于扉页。
  · 窄屏：书名转横排、偈语隐藏、底本行改成竖列，不得压缩字号。
"""

# ---------- 封面 / 扉页样式 ----------
COVER_CSS = """
.cover{position:relative;margin-bottom:44px;padding:78px 46px 56px;min-height:560px;display:flex;flex-direction:column;justify-content:center;overflow:hidden;
  border:1px solid var(--line);background:radial-gradient(130% 90% at 50% 0%,#FCFAF6 0%,#F7F4EE 62%,#F1EADB 100%);}
.cover::before{content:"";position:absolute;inset:13px;border:1px solid #E0D6C4;pointer-events:none;}
.cover::after{content:"";position:absolute;inset:18px;border:1px solid #EFE7D8;pointer-events:none;}
.cover .series{font-size:11.5px;letter-spacing:.52em;color:var(--brown);text-align:center;}
.cover .stage{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:20px;margin-top:30px;}
.cover .gatha{writing-mode:vertical-rl;font-size:14px;line-height:2.5;letter-spacing:.2em;color:#6E6153;}
.cover .gatha.l{justify-self:start;text-align:left;}
.cover .gatha.r{justify-self:end;text-align:left;}
.cover .center{text-align:center;}
.cover h1{writing-mode:vertical-rl;font-size:54px;font-weight:700;letter-spacing:.2em;line-height:1.35;
  margin:0 auto;color:var(--ink);}
.cover .sub{margin-top:18px;font-size:13px;color:var(--brown);letter-spacing:.14em;}
.cover .tag{display:inline-block;margin-top:12px;padding:2px 10px;font-size:11.5px;letter-spacing:.4em;
  color:var(--ochre);border:1px solid #D8B9AE;}
.cover .seal{width:46px;height:46px;margin:22px auto 0;background:var(--ochre);color:#FCFAF6;
  display:grid;place-items:center;font-size:17px;letter-spacing:0;box-shadow:0 0 0 3px #F7F4EE,0 0 0 4px #E2D5C0;}
.cover .meta{margin-top:30px;padding-top:16px;border-top:1px solid #E6DECF;
  font-size:11.5px;color:#9C8E7C;letter-spacing:.16em;text-align:center;}
.cover .meta span:not(:last-child)::after{content:"　·　";color:#C4B9A8;}

.frontis{position:relative;margin:0 0 46px;padding:72px 40px 56px;border:1px solid var(--line);
  background:var(--paper2);text-align:center;}
.frontis .fseries{font-size:11.5px;letter-spacing:.5em;color:var(--brown);}
.frontis .ftitle{font-size:34px;font-weight:700;letter-spacing:.28em;margin:26px 0 10px;color:var(--ink);}
.frontis .fsub{font-size:13.5px;color:var(--brown);letter-spacing:.16em;}
.frontis .frule{width:46px;height:1px;background:#C8B79F;margin:30px auto 26px;}
.frontis .fname{font-size:15px;letter-spacing:.4em;color:var(--ink);}
.frontis .fmeta{margin-top:26px;font-size:12px;line-height:2.35;color:#8E8071;letter-spacing:.1em;}
.frontis .fseal{width:34px;height:34px;margin:30px auto 0;background:none;border:1px solid var(--ochre);
  color:var(--ochre);display:grid;place-items:center;font-size:13px;letter-spacing:.02em;}
"""

COVER_MQ = """
  .cover{padding:46px 18px 36px;min-height:auto;}
  .cover .stage{grid-template-columns:1fr;gap:14px;}
  .cover .gatha{display:none;}
  .cover h1{writing-mode:horizontal-tb;font-size:30px;letter-spacing:.26em;}
  .cover .meta{font-size:10.5px;letter-spacing:.08em;margin-top:26px;}
  .cover .meta span{display:block;line-height:2.1;}
  .cover .meta span:not(:last-child)::after{content:"";}
  .frontis{padding:52px 20px 44px;}
  .frontis .ftitle{font-size:24px;letter-spacing:.18em;}
"""

# 譬喻图样式（PNG 与内嵌 SVG 通用）
FIG_CSS = """
figure.fig{margin:34px 0 38px;padding:0;}
figure.fig img,figure.fig svg{display:block;width:100%;height:auto;border:1px solid var(--line);background:var(--paper2);}
figure.fig figcaption{margin-top:11px;font-size:12.5px;line-height:1.9;color:var(--brown);text-align:center;letter-spacing:.06em;}
figure.fig figcaption span{color:#9C8E7C;}
"""


def _col(lines):
    return "<br>".join(lines)


def cover(title, sub="", tag="", seal="", gatha_first=None, gatha_second=None,
          meta=None, series="润 泽 说 · 道 可 道"):
    """竖排封面。gatha_first 为右列（先读），gatha_second 为左列（后读），各为字符串元组。"""
    right = '<div class="gatha r">%s</div>' % _col(gatha_first) if gatha_first else '<div class="gatha r"></div>'
    left = '<div class="gatha l">%s</div>' % _col(gatha_second) if gatha_second else '<div class="gatha l"></div>'
    tag_html = '<div class="tag">%s</div>' % tag if tag else ""
    seal_html = '<div class="seal">%s</div>' % seal if seal else ""
    meta_html = '<div class="meta">%s</div>' % "".join("<span>%s</span>" % m for m in (meta or [])) if meta else ""
    return """  <section class="cover">
    <div class="series">%s</div>
    <div class="stage">
      %s
      <div class="center">
        <h1>%s</h1>
        <div class="sub">%s</div>
        %s
        %s
      </div>
      %s
    </div>
    %s
  </section>
""" % (series, left, title, sub, tag_html, seal_html, right, meta_html)


def frontis(title, sub="", author="润泽", lines=None, seal="", series="润 泽 说 · 道 可 道"):
    """扉页。lines 为 (标签, 内容) 列表，渲染成「标签　内容」逐行。"""
    body = "<br>".join("%s　%s" % (k, v) for k, v in (lines or []))
    seal_html = '<div class="fseal">%s</div>' % seal if seal else ""
    return """<div class="frontis">
  <div class="fseries">%s</div>
  <div class="ftitle">%s</div>
  <div class="fsub">%s</div>
  <div class="frule"></div>
  <div class="fname">%s　著</div>
  <div class="fmeta">%s</div>
  %s
</div>
""" % (series, title, sub, author, body, seal_html)


def fig_png(path, alt, cap, note=""):
    """把本地 PNG 以 base64 内嵌，保持单文件自包含。"""
    import base64
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return ('<figure class="fig"><img alt="%s" src="data:image/png;base64,%s">'
            '<figcaption>%s<br><span>%s</span></figcaption></figure>') % (alt, b64, cap, note)


def fig_svg(path, cap, note=""):
    """直插 SVG 源码，文字清晰、体积小、可随纸色缩放。"""
    svg = open(path, encoding="utf-8").read()
    return '<figure class="fig">%s<figcaption>%s<br><span>%s</span></figcaption></figure>' % (svg, cap, note)
