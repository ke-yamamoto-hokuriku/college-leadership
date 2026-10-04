#!/usr/bin/env python3
"""events.json から研究会サイト（index.html + events/*.html）を生成する。"""
import json, os, html
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "dist_b"
D = json.load(open(ROOT / "events.json", encoding="utf-8"))
S, EVENTS = D["site"], D["events"]
KAKEN = {k["period"][:4]: k for k in S["kaken"]}

def esc(s): return html.escape(s or "", quote=True)

LOGO = """<svg class="mon" viewBox="-110 -110 220 220" width="{w}" height="{w}" aria-hidden="true">
<circle cx="0" cy="0" r="92" fill="none" stroke="currentColor" stroke-width="8"/>
<g stroke="currentColor" stroke-width="11" stroke-linecap="round" fill="none">
<g transform="translate(0,-10) scale(1.17)"><line x1="0" y1="-62" x2="0" y2="-15"/><line x1="-52" y1="-15" x2="52" y2="-15"/><line x1="0" y1="-15" x2="-46" y2="62"/><line x1="0" y1="-15" x2="46" y2="62"/></g>
<g transform="translate(0,41) scale(0.5)"><line x1="-16" y1="-52" x2="-16" y2="8"/><path d="M 16 -52 L 16 22 Q 16 46 -8 58"/></g>
</g></svg>"""

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap">'

CSS = """
:root{
  --ai:#22406b; --ai-deep:#16304f; --shu:#b14a3a; --ink:#16202c; --gray:#66717f;
  --paper:#f7f8f8; --panel:#ffffff; --line:#dfe3e8; --c1:#3a6bb0; --c2:#b14a3a; --rule:#22406b; --th:#eef1f5; --band:#1c2b45; --onband:#f4f6fa; --onband-dim:#b7c3d6;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ai:#8fb0e0; --ai-deep:#e6e9ee; --shu:#e08a7c; --ink:#e6e9ee; --gray:#98a3b3;
    --paper:#0e141c; --panel:#161e29; --line:#2a3542; --c1:#5a8fd8; --c2:#d1694f; --rule:#8fb0e0; --th:#1d2733; --band:#111a26; --onband:#f4f6fa; --onband-dim:#8f9db3;
  }
}
:root[data-theme="dark"]{
  --ai:#8fb0e0; --ai-deep:#e6e9ee; --shu:#e08a7c; --ink:#e6e9ee; --gray:#98a3b3;
  --paper:#0e141c; --panel:#161e29; --line:#2a3542; --c1:#5a8fd8; --c2:#d1694f; --rule:#8fb0e0; --th:#1d2733; --band:#111a26; --onband:#f4f6fa; --onband-dim:#8f9db3;
}
*{box-sizing:border-box;margin:0;padding:0}
html{color-scheme:light dark}
body{background:var(--paper);color:var(--ink);font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic',sans-serif;line-height:1.85;font-size:17px;font-feature-settings:"palt"}
a{color:var(--ai);text-decoration:underline;text-underline-offset:.22em;text-decoration-thickness:1px}
a:hover{color:var(--shu)}
a:focus-visible{outline:2px solid var(--shu);outline-offset:2px}
.wrap{max-width:960px;margin:0 auto;padding-block:0 96px;padding-inline:24px}
@media(max-width:480px){.wrap{padding-inline:16px}}
header.site{background:var(--band);color:var(--onband);margin:0 -24px 48px;padding:22px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
@media(max-width:480px){header.site{margin-inline:-16px;padding-inline:16px}}
header.site .mon{color:var(--onband);flex:none}
header.site .name{font-size:20px;font-weight:700;letter-spacing:.04em;line-height:1.3}
header.site .name a{color:inherit;text-decoration:none}
header.site .en{font-size:11px;letter-spacing:.22em;color:var(--onband-dim);margin-top:2px;font-weight:500}
header.site nav{margin-left:auto;display:flex;gap:22px;font-size:14px;font-weight:500}
header.site nav a{text-decoration:none;color:var(--onband-dim);display:flex;align-items:center;gap:6px}
header.site nav svg{width:15px;height:15px;flex:none;fill:none;stroke:currentColor;stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round;opacity:.85}
header.site nav a:hover{color:var(--onband)}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.2em;color:var(--ai);margin-bottom:10px}
h1{font-size:36px;font-weight:700;letter-spacing:.01em;line-height:1.45;color:var(--ai-deep);text-wrap:balance}
h1 .sub{display:block;font-size:18px;font-weight:500;letter-spacing:.02em;color:var(--gray);margin-top:8px}
section{margin-bottom:64px}
h2{font-size:22px;font-weight:700;letter-spacing:.02em;color:var(--ai-deep);margin-bottom:22px;padding-bottom:10px;border-bottom:2px solid var(--rule);line-height:1.5}
h3{font-size:17px;font-weight:700;color:var(--ai-deep);margin:26px 0 10px}
p{max-width:680px;margin-bottom:14px}
.lead p{font-size:17px}
.meta{display:flex;gap:6px 22px;flex-wrap:wrap;font-size:14px;color:var(--gray);margin:16px 0 36px;font-variant-numeric:tabular-nums}
.meta b{color:var(--ink);font-weight:700;font-size:16px;margin-left:.3em}
table{width:100%;border-collapse:collapse;font-size:15px;font-variant-numeric:tabular-nums}
th,td{border-bottom:1px solid var(--line);padding:11px 14px;text-align:left;vertical-align:top;background:var(--panel)}
th{background:var(--th);font-weight:700;white-space:nowrap;width:8em;color:var(--gray)}
.tbl{overflow-x:auto;max-width:720px;border:1px solid var(--line);border-radius:4px}
/* archive list */
.archive{list-style:none;border-top:1px solid var(--line)}
.archive li{display:grid;grid-template-columns:11em 1fr;gap:6px 24px;padding:18px 0;border-bottom:1px solid var(--line);align-items:start}
.archive .when{font-size:14px;color:var(--gray);font-variant-numeric:tabular-nums;line-height:1.7}
.archive .when b{display:inline-block;color:var(--onband);background:var(--ai);font-weight:700;letter-spacing:.12em;font-size:12px;padding:2px 8px;border-radius:3px;margin-bottom:6px}
.archive .what a{font-size:18px;font-weight:700;text-decoration:none;color:var(--ai-deep);line-height:1.5}
.archive .what a:hover{color:var(--shu)}
.archive .what .sub{font-size:14px;color:var(--gray);margin-top:2px}
.archive .what .who{font-size:14px;color:var(--gray);margin-top:6px}
.archive .what .num{font-size:13px;color:var(--shu);font-weight:500;margin-top:4px}
@media(max-width:560px){.archive li{grid-template-columns:1fr}}
/* speakers */
.speakers{list-style:none}
.speakers li{padding:12px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:10em 1fr;gap:4px 18px}
.speakers li:first-child{border-top:1px solid var(--line)}
.speakers .role{font-size:13px;color:var(--shu);font-weight:700;letter-spacing:.08em;padding-top:4px}
.speakers .name{font-weight:700;color:var(--ai-deep)}
.speakers .aff{font-size:14px;color:var(--gray)}
.speakers .talk{font-size:15px;margin-top:2px}
@media(max-width:560px){.speakers li{grid-template-columns:1fr}}
.quotes{list-style:none;max-width:680px}
.quotes li{padding:10px 0 10px 16px;border-left:3px solid var(--ai);margin-bottom:8px;font-size:15px;background:var(--panel)}
.note{font-size:14px;color:var(--gray);border:1px solid var(--line);background:var(--panel);padding:14px 18px;max-width:680px;border-radius:4px}
.note.hot{border-left:3px solid var(--shu)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:28px 40px}
@media(max-width:640px){.cols{grid-template-columns:1fr}}
.founders{list-style:none}
.founders li{padding:9px 0;border-bottom:1px solid var(--line);font-size:15px}
.founders li b{font-weight:700;color:var(--ai-deep);margin-right:.6em}
.kaken{font-size:15px;max-width:680px}
.kaken li{margin-bottom:8px;list-style:none;padding-left:0}
.kaken .num{color:var(--gray);font-size:13px;letter-spacing:.06em;margin-left:.6em}
.mats{list-style:none;max-width:680px}
.mats li{display:flex;gap:16px;padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}
.mats .k{width:9em;flex:none;color:var(--gray)}
.mats .pending{color:var(--shu);font-weight:500}
.stats{width:100%;min-width:0;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums;}
.stats th{width:auto;text-align:left;font-weight:400;color:var(--ink);white-space:normal}
.stats td.bar{width:46%;padding-left:8px;padding-right:8px}
.stats .track{position:relative;display:block;height:9px;border-radius:5px;background:var(--th);overflow:hidden}
.stats .track::after{content:"";position:absolute;left:80%;top:0;bottom:0;width:1px;background:var(--line)}
.stats .fill{display:block;height:100%;border-radius:5px;background:var(--c1)}
.stats td.v{width:5em;text-align:right;font-weight:700;color:var(--ai-deep);white-space:nowrap}
.stats tr.total th{font-weight:700}
.barnote{font-size:13px;color:var(--gray);margin:10px 0 24px;line-height:1.6}
.stats tr.total .track{background:var(--line)}
.stats tr.total th,.stats tr.total td{background:var(--th);color:var(--ai-deep)}
.trend th{width:auto;white-space:nowrap}
.trend tr:first-child th{background:var(--th);text-align:left}
.trend td{text-align:right;font-variant-numeric:tabular-nums}
.trend tr:first-child th:nth-child(n+3){text-align:right}
.trend td:nth-child(2){text-align:left;white-space:nowrap}
.trend tr:last-child th,.trend tr:last-child td{border-bottom:0}

footer.site{border-top:1px solid var(--line);padding-top:24px;font-size:14px;color:var(--gray);line-height:1.8}
footer.site .mon{color:var(--ai);float:right;margin-left:20px}
.back{font-size:14px;margin-bottom:24px;display:inline-block;font-weight:500}
/* publications with covers */
.pubs{list-style:none;display:grid;gap:22px;max-width:680px}
.pubs li{display:grid;grid-template-columns:92px 1fr;gap:18px;align-items:start}
.pubs li.nocover{grid-template-columns:1fr}
.pubs .cover img{width:100%;display:block;border:1px solid var(--line);border-radius:2px}
.pubs .t{font-weight:700;color:var(--ai-deep);font-size:16px;line-height:1.6}
.pubs .d{font-size:14px;color:var(--gray);margin-top:4px;line-height:1.7}
.evcover{max-width:170px;margin:0 0 36px}
.evcover img{width:100%;display:block;border:1px solid var(--line);border-radius:2px}
.evcover figcaption{font-size:13px;color:var(--gray);margin-top:8px;line-height:1.6}
/* photos */
.ph{margin:0}
.ph img,.ph .ph-empty{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;background:var(--th);border-radius:4px;max-width:100%}
.ph .ph-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--gray);border:1px dashed var(--line);gap:4px}
.ph .ph-empty span{font-weight:700;letter-spacing:.2em;font-size:13px}
.ph .ph-empty small{font-size:11px;opacity:.8}
.ph figcaption{font-size:13px;color:var(--gray);margin-top:8px;line-height:1.6}
.hero{margin:-48px -24px 48px;position:relative}
@media(max-width:480px){.hero{margin-inline:-16px}}
.hero .ph img,.hero .ph .ph-empty{aspect-ratio:2/1;border-radius:0;object-position:50% 68%}
@media(max-width:640px){.hero .ph img,.hero .ph .ph-empty{aspect-ratio:4/3}}
.hero .ph figcaption{padding-inline:24px}
.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:8px 0 24px}
.gallery.about{grid-template-columns:1fr 1fr;margin-bottom:32px}
.gallery .ph:first-child:nth-last-child(1){grid-column:1/-1}
.gallery .ph:first-child:nth-last-child(1) img,.gallery .ph:first-child:nth-last-child(1) .ph-empty{aspect-ratio:16/9}
@media(max-width:640px){.gallery{grid-template-columns:1fr 1fr}}
.archive li{grid-template-columns:11em 1fr 160px}
.archive .thumb .ph img,.archive .thumb .ph .ph-empty{aspect-ratio:3/2}
.archive .thumb .ph figcaption{display:none}
@media(max-width:700px){.archive li{grid-template-columns:1fr}.archive .thumb{max-width:280px}}
@media (prefers-reduced-motion: reduce){*{transition:none!important;animation:none!important}}
"""

IMG_DIR = ROOT / "images"
def photo(ph, rel="", cls="ph"):
    """images/ に実ファイルがあれば <img>、なければ写真の位置を示す枠を出す。"""
    if not ph: return ""
    p = IMG_DIR / ph["file"]
    if p.exists():
        inner = f'<img src="{rel}images/{esc(ph["file"])}" alt="{esc(ph["cap"])}" loading="lazy">'
    else:
        inner = f'<div class="ph-empty"><span>写真</span><small>{esc(ph["file"])}</small></div>'
    return f'<figure class="{cls}">{inner}<figcaption>{esc(ph["cap"])}</figcaption></figure>'

def header(rel=""):
    return f"""<header class="site">
  <div><div class="name"><a href="{rel}index.html">{esc(S['name'])}</a></div><div class="en">{esc(S['en'].upper())}</div></div>
  <nav><a href="{rel}index.html#archive"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 4h8M5.5 8h8M5.5 12h8"/><path d="M2.5 4h.01M2.5 8h.01M2.5 12h.01"/></svg>研究会一覧</a><a href="{rel}index.html#about"><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2"/><path d="M8 7.2v4"/><path d="M8 4.8h.01"/></svg>研究会について</a><a href="{rel}index.html#contact"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.8" y="3.6" width="12.4" height="8.8" rx="1.2"/><path d="M2.4 4.6 8 8.8l5.6-4.2"/></svg>事務局</a></nav>
</header>"""

def footer():
    return f"""<footer class="site">
  <div>{esc(S['office']['name'])}<br>{esc(S['office']['address'])}<br>{esc(S['office']['mail'])} ／ {esc(S['office']['contact2'])}</div>
  <div style="margin-top:10px">© {esc(S['name'])} — {esc(S['en'])}</div>
</footer>"""

def label(e):
    return f"第{e['no']}回公開研究会" if e["no"] else e["kind"]

def archive_item(e):
    who = "・".join(sp["name"] for sp in e["speakers"] if sp["role"] in ("基調講演","特別講演","講演","ゲスト講演"))
    sub = f'<div class="sub">{esc(e["subtitle"])}</div>' if e["subtitle"] else ""
    whos = f'<div class="who">{esc(who)}</div>' if who else ""
    num = f'<div class="num">参加 {esc(e["participants"])}</div>' if e["participants"] else ""
    ven = f'<div>{esc(e["venue"].split("（")[0].split(" ")[0])}</div>' if e["venue"] else ""
    tag = f"FORUM {e['no']:02d}" if e["no"] else "WORKSHOP"
    return f"""<li><div class="when"><b>{tag}</b>{esc(e['date'])}{ven}</div>
<div class="what"><a href="events/{e['slug']}.html">{esc(e['title'])}</a>{sub}{whos}{num}</div>
<div class="thumb">{photo(e['photos'][0]) if e.get('photos') else ""}</div></li>"""

CHART_CSS = """
/* chart */
.chart{margin:0 0 20px;max-width:620px}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.chart .legend{display:flex;gap:20px;font-size:14px;color:var(--gray);margin-bottom:10px}
.chart .legend span{display:flex;align-items:center;gap:7px}
.chart .legend span::before{content:"";width:14px;height:3px;border-radius:2px}
.chart .legend .k1::before{background:var(--c1)}
.chart .legend .k2::before{background:var(--c2)}
.chart .g{stroke:var(--line);stroke-width:1}
.chart .ax{font-size:11px;fill:var(--gray);font-variant-numeric:tabular-nums}
.chart .l1,.chart .l2{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.chart .l1{stroke:var(--c1)}
.chart .l2{stroke:var(--c2)}
.chart .d1,.chart .d2{stroke:var(--panel);stroke-width:2}
.chart .d1{fill:var(--c1)}
.chart .d2{fill:var(--c2)}
.chart .vl{font-size:11px;font-weight:700;font-variant-numeric:tabular-nums}
.chart .t1{fill:var(--c1)}
.chart .t2{fill:var(--c2)}
.chart figcaption{font-size:13px;color:var(--gray);margin-top:10px;line-height:1.6}
"""

def trend_svg(rows):
    """全体満足度と仕事との関連性の推移を折れ線で描く。"""
    if not rows: return ""
    W, H = 620, 250
    L, R, T, B = 44, 16, 18, 34
    lo, hi = 1.0, 5.0
    n = len(rows)
    step = (W - L - R) / (n - 1)
    def X(i): return L + step * i
    def Y(v): return T + (H - T - B) * (hi - v) / (hi - lo)
    s1 = [float(r[3]) for r in rows]   # 全体の満足度
    s2 = [float(r[4]) for r in rows]   # 仕事との関連性
    grid = "".join(
        f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" class="g"/>'
        f'<text x="{L-8}" y="{Y(v)+4:.1f}" class="ax" text-anchor="end">{v:.0f}</text>'
        for v in (1.0, 2.0, 3.0, 4.0, 5.0))
    xlab = "".join(
        f'<text x="{X(i):.1f}" y="{H-12}" class="ax" text-anchor="middle">{esc(r[0])}</text>'
        for i, r in enumerate(rows))
    def path(vals):
        return "M " + " L ".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(vals))
    def dots(vals, cls):
        return "".join(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" class="{cls}"/>'
                       for i, v in enumerate(vals))
    def tag(i, v, cls, dy):
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        ox = 7 if i == 0 else (-7 if i == n - 1 else 0)
        return (f'<text x="{X(i)+ox:.1f}" y="{Y(v)+dy:.1f}" class="vl {cls}" '
                f'text-anchor="{anchor}">{v:.2f}</text>')
    labels = (tag(0, s1[0], "t1", -12) + tag(n-1, s1[-1], "t1", -12)
              + tag(0, s2[0], "t2", 18) + tag(n-1, s2[-1], "t2", 18))
    desc = (f"研究会全体の満足度は{min(s1):.2f}から{max(s1):.2f}、"
            f"仕事との関連性は{min(s2):.2f}から{max(s2):.2f}の範囲で推移しています。")
    return f"""<figure class="chart">
<div class="legend"><span class="k1">研究会全体の満足度</span><span class="k2">仕事との関連性</span></div>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(desc)}" preserveAspectRatio="xMidYMid meet">
{grid}
<path d="{path(s2)}" class="l2"/><path d="{path(s1)}" class="l1"/>
{dots(s2,'d2')}{dots(s1,'d1')}
{labels}
{xlab}
</svg>
<figcaption>縦軸は5段階評価（1＝不満足〜5＝満足）の平均値です。どの回も4.4を上回っており、回による差は小さいことが分かります。正確な数値は下の表をご覧ください。</figcaption>
</figure>"""

def index_page():
    latest = EVENTS[0]
    pending = latest["status"] == "report_pending"
    news = f"""<section>
<div class="eyebrow">LATEST</div>
<h2>直近の公開研究会について</h2>
<p><b>{esc(label(latest))}「{esc(latest['title'])}」</b>を、{esc(latest['date'])}に{esc(latest['venue'].split('（')[0])}で開催しました。<a href="events/{latest['slug']}.html">開催概要と登壇者</a>をご覧ください。</p>
{"<div class='note hot'>開催報告・発言録は、登壇者の確認を経たのち掲載します。</div>" if pending else ""}
<p style="margin-top:18px">次回・第10回公開研究会は、山本啓一の近刊『学部長の教科書』を題材に開催する予定です。日程が決まり次第ご案内します。</p>
</section>"""
    items = "\n".join(archive_item(e) for e in EVENTS)
    founders = "".join(f"<li><b>{esc(f['name'])}</b>{esc(f['aff'])}</li>" for f in S["founders"])
    kaken = "".join(f"<li>{esc(k['period'])}　「{esc(k['title'])}」（研究代表者：{esc(k['rep'])}）{'<span class=num>'+esc(k['number'])+'</span>' if k['number'] else ''}</li>" for k in S["kaken"])
    def pub(p):
        c = p.get("cover")
        img = f'<div class="cover"><img src="images/{esc(c)}" alt="{esc(p["title"])} 書影" loading="lazy"></div>' if c and (IMG_DIR/c).exists() else ""
        cls = "" if img else ' class="nocover"'
        return f'<li{cls}>{img}<div><div class="t">{esc(p["title"])}</div><div class="d">{esc(p["detail"])}</div></div></li>'
    pubs = "".join(pub(p) for p in S["publications"])
    related = "".join(f"<li><span class='k'>{esc(r['date'])}</span><span>{esc(r['text'])}</span></li>" for r in S["related"])
    trend = "".join(
        "<tr><th>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(esc(c) for c in r)
        for r in S.get("survey_trend", []))
    trend_chart = trend_svg(S.get("survey_trend", []))
    body = f"""<title>{esc(S['name'])}</title>
{FONTS}
<style>{CSS}{CHART_CSS}</style>
<div class="wrap">
{header()}
<div class="hero">{photo(S.get('hero'))}</div>
<section class="lead">
<div class="eyebrow">COLLEGE LEADERSHIP FORUM · SINCE 2018</div>
<h1>{esc(S['tagline'])}</h1>
<div class="meta"><span>発足 <b>2018年</b></span><span>公開研究会 <b>9回</b></span><span>ミドルリーダー研修 <b>1回</b></span><span>延べ参加 <b>696名</b></span><span>実人数 <b>372名</b></span></div>
{"".join(f"<p>{esc(p)}</p>" for p in S['intro'])}
</section>
{news}
<section id="archive">
<div class="eyebrow">ARCHIVE</div>
<h2>これまでの公開研究会</h2>
<ul class="archive">{items}</ul>
</section>
<section id="about">
<div class="eyebrow">ABOUT</div>
<h2>研究会について</h2>
<div class="gallery about">{"".join(photo(ph) for ph in S.get('about_photos',[]))}</div>
<div class="cols">
<div><h3>発起人</h3><ul class="founders">{founders}</ul></div>
<div><h3>科学研究費助成事業</h3><ul class="kaken">{kaken}</ul><p style="font-size:14px;color:var(--gray)">JSPS科研費 基盤研究(C)。公開研究会は本研究の一環として開催しています。</p></div>
</div>
<h3>参加者アンケートの推移</h3>
{trend_chart}
<div class="tbl" style="max-width:620px"><table class="trend">
<tr><th>回</th><th>開催</th><th>回答数</th><th>全体の満足度</th><th>仕事との関連性</th></tr>
{trend}
</table></div>
<p style="font-size:14px;color:var(--gray);margin-top:12px;max-width:680px;line-height:1.8">{esc(S.get('survey_trend_note',''))}</p>
<h3>刊行物</h3><ul class="pubs">{pubs}</ul>
<h3>関連する登壇・企画</h3><ul class="mats">{related}</ul>
</section>
<section id="contact">
<div class="eyebrow">CONTACT</div>
<h2>事務局・お問い合わせ</h2>
<div class="tbl"><table>
<tr><th>事務局</th><td>{esc(S['office']['address'])}</td></tr>
<tr><th>メール</th><td>{esc(S['office']['mail'])}（事務局・水谷）<br>{esc(S['office']['contact2'])}</td></tr>
</table></div>
</section>
{footer()}
</div>"""
    return body

def event_page(e):
    rows = []
    def row(k, v):
        if v: rows.append(f"<tr><th>{k}</th><td>{esc(v)}</td></tr>")
    row("日時", e["date"] + ("　" + e["time"] if e["time"] else ""))
    row("会場", e["venue"]); row("定員", e["capacity"]); row("参加費", e["fee"]); row("対象", e["target"])
    row("主催", e["host"]); row("共催", e["cohost"]); row("参加者", e["participants"])
    speakers = "".join(
        f"<li><span class='role'>{esc(sp['role'])}</span><div><div class='name'>{esc(sp['name'])}</div>"
        + (f"<div class='aff'>{esc(sp['aff'])}</div>" if sp['aff'] else "")
        + (f"<div class='talk'>「{esc(sp['talk'])}」</div>" if sp['talk'] else "") + "</div></li>"
        for sp in e["speakers"])
    report = "".join(f"<h3>{esc(r['h'])}</h3>" + "".join(f"<p>{esc(p)}</p>" for p in r["p"]) for r in e["report"])
    survey = "".join(f"<li>{esc(q)}</li>" for q in e["survey"])
    st = e.get("survey_stats") or []
    stats = ""
    if st:
        TOTAL = ' class="total"'
        def srow(i, k, v):
            try:
                pct = max(0.0, min(100.0, float(v) / 5 * 100))
                bar = (f'<span class="track"><span class="fill" style="width:{pct:.1f}%"></span></span>')
            except ValueError:
                bar = ""
            return ('<tr%s><th>%s</th><td class="bar">%s</td><td class="v">%s</td></tr>'
                    % (TOTAL if i == 0 else "", esc(k), bar, esc(v)))
        rows_ = "".join(srow(i, k, v) for i, (k, v) in enumerate(st))
        stats = (f'<div class="tbl" style="max-width:560px"><table class="stats">{rows_}</table></div>'
                 f'<p class="barnote">横棒は5点満点に対する位置を示します。細い縦線は4.0の目盛りです。</p>')
    slead = f'<p>{esc(e["survey_lead"])}</p>' if e.get("survey_lead") else ""
    note9 = f'<p style="font-size:14px;color:var(--gray);margin-top:12px">{esc(e["survey_note"])}</p>' if e.get("survey_note") else ""
    mlabel = {"handout":"配布資料","transcript":"発言録","survey":"アンケート結果"}
    mstate = {"available":"参加者向けに共有しています（掲載準備中）","pending":"<span class='pending'>登壇者確認後に公開</span>","none":"—"}
    mats = "".join(f"<li><span class='k'>{mlabel[k]}</span><span>{mstate[v]}</span></li>" for k,v in e["materials"].items() if v != "none")
    pnote = f'<p style="font-size:14px;color:var(--gray);margin-top:12px">{esc(e["participants_note"])}</p>' if e.get("participants_note") else ""
    kaken = KAKEN.get(e["kaken"]) if e["kaken"] else None
    kk = f"<p style='font-size:13px;color:var(--gray)'>本研究会はJSPS科研費 基盤研究(C)「{esc(kaken['title'])}」（研究代表者：{esc(kaken['rep'])}）の助成を受けて開催しました。</p>" if kaken else ""
    idx = EVENTS.index(e)
    prev_ = EVENTS[idx+1] if idx+1 < len(EVENTS) else None
    next_ = EVENTS[idx-1] if idx > 0 else None
    pn = "<div class='meta' style='margin-top:48px'>" + (f"<a href='{prev_['slug']}.html'>← {esc(label(prev_))}</a>" if prev_ else "") + (f"<a href='{next_['slug']}.html'>{esc(label(next_))} →</a>" if next_ else "") + "</div>"
    tag = f"FORUM {e['no']:02d}" if e["no"] else "WORKSHOP"
    sub = f"<span class='sub'>{esc(e['subtitle'])}</span>" if e["subtitle"] else ""
    pending = "<div class='note hot' style='margin-top:24px'>開催報告・発言録は、登壇者の確認を経たのち掲載します。</div>" if e["status"]=="report_pending" else ""
    body = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(label(e))}｜{esc(S['name'])}</title>{FONTS}<style>{CSS}</style></head><body>
<div class="wrap">
{header("../")}
<a class="back" href="../index.html#archive">← 研究会一覧</a>
<section class="lead">
<div class="eyebrow">{tag} · {esc(e['iso'])}</div>
<h1>{esc(e['title'])}{sub}</h1>
<div class="meta"><span>{esc(label(e))}</span><span>{esc(e['date'])}</span>{f"<span>{esc(e['venue'].split('（')[0])}</span>" if e['venue'] else ""}</div>
{"".join(f"<p>{esc(p)}</p>" for p in e['purpose'])}
{pending}
</section>
{f'<div class="gallery">{"".join(photo(ph, "../") for ph in e["photos"])}</div>' if e.get('photos') else ""}
{f'<figure class="evcover"><img src="../images/{esc(e["cover"]["file"])}" alt="{esc(e["cover"]["cap"])}"><figcaption>{esc(e["cover"]["cap"])}</figcaption></figure>' if e.get("cover") and (IMG_DIR/e["cover"]["file"]).exists() else ""}
<section><div class="eyebrow">OUTLINE</div><h2>開催概要</h2><div class="tbl"><table>{''.join(rows)}</table></div>{pnote}</section>
{f'<section><div class="eyebrow">PROGRAM</div><h2>登壇者とプログラム</h2><ul class="speakers">{speakers}</ul></section>' if speakers else ""}
{f'<section><div class="eyebrow">REPORT</div><h2>開催報告</h2>{report}</section>' if report else ""}
{f'<section><div class="eyebrow">VOICES</div><h2>参加者アンケートから</h2>{slead}{stats}<ul class="quotes">{survey}</ul>{note9}</section>' if (survey or stats) else ""}
{f'<section><div class="eyebrow">MATERIALS</div><h2>資料</h2><ul class="mats">{mats}</ul>{kk}</section>' if any(v!="none" for v in e["materials"].values()) else (f'<section>{kk}</section>' if kk else "")}
{pn}
{footer()}
</div></body></html>"""
    return body

OUT.mkdir(exist_ok=True); (OUT/"events").mkdir(exist_ok=True)
import shutil
if IMG_DIR.exists(): shutil.copytree(IMG_DIR, OUT/"images", dirs_exist_ok=True)
(OUT/"index.html").write_text(index_page(), encoding="utf-8")
for e in EVENTS:
    (OUT/"events"/f"{e['slug']}.html").write_text(event_page(e), encoding="utf-8")
print("built", len(EVENTS)+1, "pages ->", OUT)
