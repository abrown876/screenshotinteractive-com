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
    stories.sort(key=lambda s: (s['date'], s['slug']), reverse=True)
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
        cap = f'<figcaption>{esc(s.get("photoCaption", ""))}</figcaption>' if s.get('photoCaption') else ''
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
    desc = 'Industry news, numbers and know-how on activations, creators and digital outdoor advertising, from Screenshot Interactive.'
    tiles = ''.join(tile(s) for s in stories)
    img = SITE + card_url(stories[0]) if stories else SITE + '/assets/og-default.jpg'
    return head(f'{NAME} | Industry news from Screenshot Interactive', desc, url, img, style) + top + f"""

  <section class="tbp-intro">
    <div class="container">
      <div class="eyebrow">Industry update</div>
      <h1>{NAME}</h1>
      <p>What is changing in activations, creators and digital outdoor advertising, and what it means for brands in Jamaica. New stories every week.</p>
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
  </item>""")
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
    photo = (ROOT / c['photo'].lstrip('/')).as_uri()
    stat = f'<div class=stat>{esc(s["stat"])}</div><div class=statl>{esc(s["statLabel"])}</div><div class=rule></div>' if s.get('stat') else '<div class=rule></div>'
    return f"""<style>{fonts_css()}
body{{color:#fff;background:#141228 url('{photo}') {c.get('focal', 'center')}/{c.get('size', 'cover')} no-repeat;position:relative}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.68) 0%,rgba(0,0,0,.25) 12%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 36%,rgba(20,18,40,.96) 58%)}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.cat{{font:800 20px Archivo;letter-spacing:.18em;text-transform:uppercase;border:2px solid #fff;padding:9px 16px;border-radius:999px}}
.bottom{{margin-top:auto}}
.stat{{font-family:Nexa;font-size:200px;line-height:.85;letter-spacing:-.04em}}
.statl{{font:600 32px/1.25 Inter;margin:18px 0 26px;max-width:760px;color:rgba(255,255,255,.9)}}
.rule{{width:120px;height:8px;background:#EB5C77;margin-bottom:26px}}
h1{{font-family:Nexa;font-size:{s['card'].get('h1', 72)}px;line-height:1.03;letter-spacing:-.02em}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end;margin-top:40px}}
.foot small{{font:600 18px Inter;color:rgba(255,255,255,.72);max-width:640px}}
</style><div class=shade></div><div class=wrap>
<div class=top><div class=tbp>THE BIGGER <i>PICTURE</i></div><div class=cat>{esc(s['category'])}</div></div>
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


def render_cards(stories):
    from playwright.sync_api import sync_playwright
    import tempfile
    CARDS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for s in stories:
            fn = card_cover if s['card']['style'] == 'cover' else card_navy
            h = pathlib.Path(tmp) / f'{s["slug"]}.html'
            h.write_text('<!doctype html><meta charset=utf-8>' + fn(s))
            pg.goto(h.as_uri())
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(CARDS / f'{s["slug"]}.jpg'), type='jpeg', quality=88)
            print('card', s['slug'])
        b.close()


def main():
    stories = load_stories()
    if '--no-cards' not in sys.argv:
        render_cards(stories)
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
