#!/usr/bin/env python3
"""Build The Bigger Picture section.

Reads every story in content/bigger-picture/*.json and writes:
  the-bigger-picture/index.html               section front page
  the-bigger-picture/<slug>/index.html        one page per story
  assets/bigger-picture/cards/<slug>.jpg      1080x1350 Instagram card (JPEG, as the IG API requires)
  the-bigger-picture/feed.xml                 RSS feed (card image + caption) that Make watches to post to Instagram

Usage:  python3 tools/bigger_picture.py            (build everything)
        python3 tools/bigger_picture.py --no-cards (pages and feed only)
Needs:  pip install playwright && python -m playwright install chromium   (for the cards)
"""
import html, json, pathlib, re, sys
from datetime import datetime
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://screenshotinteractive.com'
SECTION = 'the-bigger-picture'
NAME = 'The Bigger Picture'
CONTENT = ROOT / 'content' / 'bigger-picture'
CARDS = ROOT / 'assets' / 'bigger-picture' / 'cards'
ASSET_V = 'tbp1'

esc = html.escape


def load_stories():
    stories = [json.loads(p.read_text()) for p in sorted(CONTENT.glob('*.json'))]
    stories = [s for s in stories if not s.get('draft')]
    stories.sort(key=lambda s: (s['date'], -s.get('rank', 99)), reverse=True)
    return stories


def nice_date(d):
    return datetime.strptime(d, '%Y-%m-%d').strftime('%-d %b %Y')


# ---------- shared chrome, copied from the live About page so it stays in sync ----------
def chrome():
    about = (ROOT / 'about' / 'index.html').read_text()
    top = about[about.index('<div id="liveBanner">'):about.index('</header>') + len('</header>')]
    foot = about[about.index('<footer class="site">'):]
    style = re.search(r'<link rel="stylesheet" href="/assets/styles.css\?v=[^"]+">', about).group(0)
    return top, foot, style


def head(title, desc, url, image, style, extra=''):
    t, d = esc(title), esc(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/assets/favicon.svg?v=brand22" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/{SECTION}/feed.xml">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
{style}
{extra}</head>
<body class="tbp">
"""


def card_url(s):
    return f'/assets/bigger-picture/cards/{s["slug"]}.jpg?v={ASSET_V}'


# ---------- pages ----------
def article(s, top, foot, style, more):
    url = f'{SITE}/{SECTION}/{s["slug"]}'
    ld = {
        '@context': 'https://schema.org', '@type': 'Article', 'headline': s['title'],
        'description': s['dek'], 'datePublished': s['date'], 'image': SITE + card_url(s).split('?')[0],
        'publisher': {'@type': 'Organization', 'name': 'Screenshot Interactive Ltd.'},
        'mainEntityOfPage': url,
    }
    hero = ''
    if s.get('photo'):
        cap_txt = (s.get('photoCaption', '') + (' AI illustration.' if s.get('aiImage') else '')).strip()
        cap = f'<figcaption>{esc(cap_txt)}</figcaption>' if cap_txt else ''
        hero = f'<figure class="tbp-hero"><img src="{s["photo"]}" alt="{esc(s.get("photoCaption", s["title"]))}">{cap}</figure>'
    stat = ''
    if s.get('stat'):
        stat = f'<div class="tbp-stat"><strong>{esc(s["stat"])}</strong><span>{esc(s["statLabel"])}</span></div>'
    if s.get('sources'):
        items = ''.join(
            f'<li><a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x["title"])}</a> <span>{esc(x["publisher"])}, {nice_date(x["date"])}</span></li>'
            for x in s['sources'])
        sources = f'<div class="tbp-sources"><h5>Sources</h5><ul>{items}</ul></div>'
    else:
        sources = f'<div class="tbp-sources"><h5>About this piece</h5><p>{esc(s.get("sourceNote", ""))}</p></div>'
    related = ''.join(tile(o) for o in more)
    related_block = f'<section class="section tbp-more"><div class="container"><div class="eyebrow">More from {NAME}</div><div class="tbp-grid">{related}</div></div></section>' if related else ''
    return head(f'{s["title"]} | {NAME} | Screenshot Interactive', s['dek'], url, SITE + card_url(s), style,
                f'<script type="application/ld+json">{json.dumps(ld)}</script>\n') + top + f"""

  <article class="tbp-article">
    <div class="container tbp-narrow">
      <a class="tbp-back" href="/{SECTION}">← {NAME}</a>
      <div class="eyebrow">{esc(s['category'])} · {nice_date(s['date'])}</div>
      <h1>{esc(s['title'])}</h1>
      <p class="tbp-dek">{esc(s['dek'])}</p>
    </div>
    <div class="container tbp-wide">{hero}</div>
    <div class="container tbp-narrow tbp-body">
      {stat}
      {''.join(s['body'])}
      <div class="tbp-takeaway"><div class="eyebrow">The takeaway</div><p>{esc(s['takeaway'])}</p></div>
      <a class="tbp-service" href="{s['service']['href']}"><span>How Screenshot can help</span><strong>{esc(s['service']['label'])} →</strong></a>
      {sources}
    </div>
  </article>
  {related_block}

""" + foot


def tile(s):
    return f"""<a class="tbp-tile" href="/{SECTION}/{s['slug']}">
        <img src="{card_url(s)}" alt="{esc(s['title'])}" loading="lazy">
        <div class="tbp-tile-body"><div class="eyebrow">{esc(s['category'])}</div><h4>{esc(s['title'])}</h4><p>{esc(s['dek'])}</p><span>{nice_date(s['date'])}</span></div>
      </a>"""


def index(stories, top, foot, style):
    url = f'{SITE}/{SECTION}'
    desc = 'Marketing, events and creator news from Jamaica, the Caribbean and the diaspora, from Screenshot Interactive.'
    tiles = ''.join(tile(s) for s in stories)
    img = SITE + card_url(stories[0]) if stories else SITE + '/assets/og-default.jpg'
    return head(f'{NAME} | Industry news from Screenshot Interactive', desc, url, img, style) + top + f"""

  <section class="tbp-intro">
    <div class="container">
      <div class="eyebrow">Industry update</div>
      <h1>{NAME}</h1>
      <p>Marketing, events and creator news from Jamaica, the Caribbean and the diaspora, plus the global stories that matter here. New stories every week.</p>
      <a class="tbp-follow" href="https://www.instagram.com/screenshotja" target="_blank" rel="noopener">Follow on Instagram @screenshotja →</a>
    </div>
  </section>
  <section class="section" style="padding-top:12px">
    <div class="container"><div class="tbp-grid">{tiles}</div></div>
  </section>

""" + foot


def feed(stories):
    items = []
    for s in stories:
        link = f'{SITE}/{SECTION}/{s["slug"]}'
        img = SITE + f'/assets/bigger-picture/cards/{s["slug"]}.jpg'
        size = (CARDS / f'{s["slug"]}.jpg').stat().st_size if (CARDS / f'{s["slug"]}.jpg').exists() else 0
        extra = ''.join(f'    <media:content url="{SITE}/assets/bigger-picture/cards/{x.name}" medium="image" type="image/jpeg" width="1080" height="1350"/>\n'
                        for x in sorted(CARDS.glob(f'{s["slug"]}-*.jpg')))
        pub = format_datetime(datetime.strptime(s['date'] + ' 07:00', '%Y-%m-%d %H:%M').astimezone())
        items.append(f"""  <item>
    <title>{esc(s['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{pub}</pubDate>
    <category>{esc(s['category'])}</category>
    <description>{esc(s['caption'])}</description>
    <enclosure url="{img}" length="{size}" type="image/jpeg"/>
    <media:content url="{img}" medium="image" type="image/jpeg" width="1080" height="1350"/>
{extra}  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>{NAME} | Screenshot Interactive</title>
  <link>{SITE}/{SECTION}</link>
  <description>Industry news, numbers and know-how from Screenshot Interactive.</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


# ---------- Instagram cards ----------
def fonts_css():
    f = (ROOT / 'assets' / 'fonts').as_uri()
    a = (ROOT / 'assets').as_uri()
    return f"""
@font-face{{font-family:Nexa;src:url('{a}/NexaBlack.ttf');font-weight:900}}
@font-face{{font-family:Archivo;src:url('{f}/archivo-latin-800-normal.woff2');font-weight:800}}
@font-face{{font-family:Inter;src:url('{f}/inter-latin-400-normal.woff2');font-weight:400}}
@font-face{{font-family:Inter;src:url('{f}/inter-latin-600-normal.woff2');font-weight:600}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden;-webkit-font-smoothing:antialiased}}
.logo{{height:84px}} .logo svg{{height:100%;width:auto;display:block}}
.tbp{{font-family:Nexa;font-size:30px;letter-spacing:.03em}} .tbp i{{font-style:normal;color:#EB5C77}}
"""


def logo_svg(white=True):
    s = (ROOT / 'assets' / 'logo-full-light.svg').read_text()
    s = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', s, flags=re.S)
    return s.replace('#595496', '#FFFFFF') if white else s


def src_line(s):
    if s.get('cardSource'):
        return s['cardSource']
    if s.get('sources'):
        return 'Source: ' + '; '.join(x['publisher'].replace(', reporting', ' ·') for x in s['sources'])
    return f'{NAME} · {nice_date(s["date"])}'


def card_cover(s):
    c = s['card']
    stat_px = 200 if len(s.get('stat', '')) <= 6 else int(200 * 6.4 / len(s['stat']))
    photo = (ROOT / c['photo'].lstrip('/')).as_uri()
    stat = f'<div class=stat>{esc(s["stat"])}</div><div class=statl>{esc(s["statLabel"])}</div><div class=rule></div>' if s.get('stat') else '<div class=rule></div>'
    return f"""<style>{fonts_css()}
body{{color:#fff;background:#141228 url('{photo}') {c.get('focal', 'center')}/{c.get('size', 'cover')} no-repeat;position:relative}}
.wrap .tbp{{text-shadow:0 2px 14px rgba(0,0,0,.7),0 0 2px rgba(0,0,0,.5)}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.68) 0%,rgba(0,0,0,.25) 12%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 36%,rgba(20,18,40,.96) 58%)}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.cat{{font:800 20px Archivo;letter-spacing:.18em;text-transform:uppercase;border:2px solid #fff;padding:9px 16px;border-radius:999px}}
.bottom{{margin-top:auto}}
.ai{{align-self:flex-end;margin-top:14px;font:600 16px Inter;letter-spacing:.06em;color:rgba(255,255,255,.8);background:rgba(0,0,0,.35);padding:5px 10px;border-radius:6px}}
.stat{{font-family:Nexa;font-size:{stat_px}px;line-height:.85;letter-spacing:-.04em}}
.statl{{font:600 32px/1.25 Inter;margin:18px 0 26px;max-width:760px;color:rgba(255,255,255,.9)}}
.rule{{width:120px;height:8px;background:#EB5C77;margin-bottom:26px}}
h1{{font-family:Nexa;font-size:{s['card'].get('h1', 72)}px;line-height:1.03;letter-spacing:-.02em}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end;margin-top:40px}}
.foot small{{font:600 18px Inter;color:rgba(255,255,255,.72);max-width:640px}}
</style><div class=shade></div><div class=wrap>
<div class=top><div class=tbp>THE BIGGER <i>PICTURE</i></div><div class=cat>{esc(s['category'])}</div></div>
{'<div class=ai>AI illustration</div>' if s.get('aiImage') else ''}
<div class=bottom>{stat}<h1>{esc(s['card'].get('headline', s['title']))}</h1>
<div class=foot><small>{esc(src_line(s))}</small><div class=logo>{logo_svg()}</div></div></div></div>"""


def card_navy(s):
    mark = (ROOT / 'assets' / 's-mark.svg').read_text()
    mark = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', mark, flags=re.S)
    if s.get('stat'):
        body = f'<div class=stat>{esc(s["stat"])}</div><p class=statl>{esc(s["statLabel"])}</p><h2>{esc(s["card"].get("headline", s["title"]))}</h2>'
    else:
        body = f'<h1>{esc(s["card"].get("headline", s["title"]))}</h1><p class=dek>{esc(s["dek"])}</p>'
    return f"""<style>{fonts_css()}
body{{background:#595496;color:#fff;padding:80px;display:flex;flex-direction:column;position:relative}}
.mark{{position:absolute;right:-230px;bottom:-170px;width:900px;opacity:.12}} .mark svg{{width:100%;height:auto}} .mark svg *{{fill:#fff !important}}
.top{{display:flex;justify-content:space-between;align-items:center;position:relative}}
.pill{{font:800 22px Archivo;letter-spacing:.16em;text-transform:uppercase;background:#EB5C77;padding:12px 22px;border-radius:999px}}
.main{{flex:1;display:flex;flex-direction:column;justify-content:center;position:relative}}
h1{{font-family:Nexa;font-size:{s['card'].get('h1', 104)}px;line-height:1.0;letter-spacing:-.025em}}
h2{{font-family:Nexa;font-size:56px;line-height:1.05;margin-top:36px}}
.dek{{font:400 34px/1.4 Inter;color:rgba(255,255,255,.85);margin-top:40px;max-width:840px}}
.stat{{font-family:Nexa;font-size:300px;line-height:.9;letter-spacing:-.04em}}
.statl{{font:600 44px/1.22 Inter;margin-top:24px;max-width:820px}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end;position:relative}}
.foot small{{font:600 20px Inter;color:rgba(255,255,255,.72);max-width:560px}}
.logo{{height:96px}}
</style>
<div class=mark>{mark}</div>
<div class=top><div class=tbp>THE BIGGER <i>PICTURE</i></div><div class=pill>{esc(s['category'])}</div></div>
<div class=main>{body}</div>
<div class=foot><small>{esc(src_line(s))}</small><div class=logo>{logo_svg()}</div></div>"""


SPARKLE = '<svg viewBox="0 0 40 40"><path d="M20 0c2 11 9 18 20 20-11 2-18 9-20 20-2-11-9-18-20-20C11 18 18 11 20 0z"/></svg>'


def card_spotlight(s):
    """Creator Spotlight: two slides. 1 = fun cover with cutout, 2 = detail."""
    c = s['creator']
    cut = (ROOT / c['cutout'].lstrip('/')).as_uri()
    alias = esc(c['alias'].upper())
    alias_px = int(min(260, 1500 / max(len(c["alias"]), 1)))
    rot = [-6, 5, -3]
    pos = [(60, 470), (720, 610), (70, 760)]
    chips = ''.join(
        f'<div class=chip style="left:{x}px;top:{y}px;transform:rotate({r}deg)"><b>{esc(v)}</b><span>{esc(l)}</span></div>'
        for (v, l), (x, y), r in zip(c['stats'], pos, rot))
    niches = ''.join(f'<span>{esc(n)}</span>' for n in c['niches'])
    base = fonts_css() + """
.spark{position:absolute;width:56px;height:56px} .spark svg{width:100%;height:100%;display:block}
"""
    slide1 = f"""<style>{base}
body{{background:#EB5C77;color:#fff;position:relative;overflow:hidden}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.22) 3px,transparent 3.5px);background-size:34px 34px;-webkit-mask-image:linear-gradient(160deg,#000 0%,transparent 55%)}}
.alias{{position:absolute;left:0;right:0;top:170px;text-align:center;font-family:Nexa;font-size:{alias_px}px;line-height:.9;letter-spacing:-.03em;color:transparent;-webkit-text-stroke:5px #fff;opacity:.95}}
.alias2{{position:absolute;left:0;right:0;top:{170 + int(alias_px * .92)}px;text-align:center;font-family:Nexa;font-size:{alias_px}px;line-height:.9;letter-spacing:-.03em;color:#595496}}
.cut{{position:absolute;left:50%;bottom:250px;height:930px;transform:translateX(-46%)}}
.top{{position:absolute;top:56px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;z-index:5}}
.sticker{{background:#FFE14D;color:#1A1A1A;font:800 24px Archivo;letter-spacing:.12em;text-transform:uppercase;padding:14px 22px;border-radius:14px;transform:rotate(4deg);box-shadow:6px 6px 0 #1A1A1A}}
.chip{{position:absolute;z-index:6;background:#fff;color:#1A1A1A;border-radius:22px;padding:16px 24px 14px;box-shadow:8px 8px 0 #595496;display:flex;flex-direction:column;align-items:flex-start}}
.chip b{{font-family:Nexa;font-size:64px;line-height:1;color:#595496;letter-spacing:-.02em}}
.chip span{{font:800 19px Archivo;letter-spacing:.14em;text-transform:uppercase;color:#EB5C77;margin-top:4px}}
.band{{position:absolute;left:0;right:0;bottom:0;height:270px;background:#595496;padding:34px 64px 0;z-index:7}}
.band h1{{font-family:Nexa;font-size:58px;line-height:1.02;letter-spacing:-.02em;max-width:720px}}
.meta{{display:flex;gap:14px;align-items:center;margin-top:18px}}
.handle{{font:800 26px Archivo;background:#fff;color:#595496;padding:8px 16px;border-radius:999px}}
.niches span{{font:700 20px Inter;color:rgba(255,255,255,.85);margin-right:14px}}
.niches span::before{{content:'✦ ';color:#FFE14D}}
.logo{{position:absolute;right:64px;bottom:40px;height:80px;z-index:8}}
.s1{{left:210px;top:420px;fill:#FFE14D}} .s2{{right:130px;top:350px;width:40px;height:40px;fill:#fff}} .s3{{right:300px;top:880px;width:34px;height:34px;fill:#FFE14D}}
.spark svg{{fill:inherit}}
</style>
<div class=dots></div>
<div class=alias>{alias}</div><div class=alias2>{alias}</div>
<img class=cut src="{cut}">
<div class="spark s1" style="fill:#FFE14D">{SPARKLE}</div><div class="spark s2" style="fill:#fff">{SPARKLE}</div><div class="spark s3" style="fill:#FFE14D">{SPARKLE}</div>
<div class=top><div class=tbp>THE BIGGER <i style="color:#595496">PICTURE</i></div><div class=sticker>★ Creator Spotlight</div></div>
{chips}
<div class=band><h1>{esc(c['hook'])}</h1><div class=meta><span class=handle>{esc(c['handle'])}</span><span class=niches>{niches}</span></div></div>
<div class=logo>{logo_svg()}</div>"""

    why = ''.join(f'<li><b>{esc(a)}</b><span>{esc(b)}</span></li>' for a, b in c['why'])
    stats = ''.join(f'<div><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in c['stats'])
    slide2 = f"""<style>{base}
body{{background:#595496;color:#fff;padding:64px;display:flex;flex-direction:column;position:relative;overflow:hidden}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.pill{{font:800 22px Archivo;letter-spacing:.14em;text-transform:uppercase;background:#FFE14D;color:#1A1A1A;padding:12px 20px;border-radius:999px}}
.who{{display:flex;align-items:center;gap:26px;margin-top:48px}}
.av{{width:150px;height:150px;border-radius:50%;background:#EB5C77 url('{cut}') center 8%/150% auto no-repeat;border:6px solid #fff;flex:none}}
.who h2{{font-family:Nexa;font-size:62px;line-height:1}}
.who p{{font:800 26px Archivo;color:#FFE14D;margin-top:8px}}
.fact{{margin-top:34px;background:rgba(255,255,255,.1);border-left:8px solid #EB5C77;border-radius:0 16px 16px 0;padding:22px 26px;font:600 30px/1.3 Inter}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:30px}}
.stats div{{background:#fff;color:#1A1A1A;border-radius:18px;padding:20px 22px;box-shadow:7px 7px 0 #EB5C77}}
.stats b{{display:block;font-family:Nexa;font-size:58px;line-height:1;color:#595496}}
.stats span{{font:800 18px Archivo;letter-spacing:.12em;text-transform:uppercase;color:#EB5C77}}
h3{{font:800 24px Archivo;letter-spacing:.16em;text-transform:uppercase;color:#FFE14D;margin-top:44px}}
ul{{list-style:none;margin-top:14px}}
li{{display:flex;flex-direction:column;padding:16px 0;border-bottom:2px solid rgba(255,255,255,.18)}}
li b{{font-family:Nexa;font-size:40px;line-height:1.1}}
li span{{font:400 26px/1.35 Inter;color:rgba(255,255,255,.85);margin-top:4px}}
.cta{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:30px}}
.cta p{{font:700 24px/1.35 Inter;max-width:640px}}
.logo{{height:80px;flex:none}}
.spark{{position:absolute;right:70px;top:190px;width:60px;height:60px;fill:#FFE14D}}
</style>
<div class=spark>{SPARKLE}</div>
<div class=top><div class=tbp>THE BIGGER <i>PICTURE</i></div><div class=pill>★ Creator Spotlight</div></div>
<div class=who><div class=av></div><div><h2>{esc(c['name'])}</h2><p>{esc(c['handle'])} · {esc(' · '.join(c['niches']))}</p></div></div>
<div class=fact>{esc(c['fact'])}</div>
<div class=stats>{stats}</div>
<h3>Why brands work with {esc(c['name'].split()[0])}</h3>
<ul>{why}</ul>
<div class=cta><p>{esc(c['cta'])}</p><div class=logo>{logo_svg()}</div></div>"""
    return [slide1, slide2]


def render_cards(stories):
    from playwright.sync_api import sync_playwright
    import tempfile
    CARDS.mkdir(parents=True, exist_ok=True)
    styles = {'cover': card_cover, 'navy': card_navy, 'spotlight': card_spotlight}
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in stories:
            slides = styles[s['card']['style']](s)
            if isinstance(slides, str):
                slides = [slides]
            for old in CARDS.glob(f'{s["slug"]}-*.jpg'):
                old.unlink()
            for i, html_ in enumerate(slides):
                h = pathlib.Path(tmp) / f'{s["slug"]}-{i}.html'
                h.write_text('<!doctype html><meta charset=utf-8>' + html_)
                pg.goto(h.as_uri())
                pg.wait_for_timeout(300)
                name = f'{s["slug"]}.jpg' if i == 0 else f'{s["slug"]}-{i + 1}.jpg'
                pg.screenshot(path=str(CARDS / name), type='jpeg', quality=88)
            print('card', s['slug'], len(slides), 'slide(s)')
        b.close()


def main():
    stories = load_stories()
    only = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--only=')]
    if '--no-cards' not in sys.argv:
        render_cards([s for s in stories if not only or s['slug'] in only])
    top, foot, style = chrome()
    out = ROOT / SECTION
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(index(stories, top, foot, style))
    for s in stories:
        more = [o for o in stories if o['slug'] != s['slug']][:3]
        d = out / s['slug']
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(article(s, top, foot, style, more))
    (out / 'feed.xml').write_text(feed(stories))
    print(f'built {len(stories)} stories')


if __name__ == '__main__':
    main()
