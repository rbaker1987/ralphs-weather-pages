#!/usr/bin/env python3
"""Build the public weather pages from data/today.json.

Usage (from the repo root):  python3 tools/render.py [data/today.json]
Writes east-texas/index.html and nm-mountains/index.html.
Page text comes only from the JSON; layout and styling live here and in assets/style.css.
"""
import json, sys, os
from html import escape as e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700'
         '&family=Space+Grotesk:wght@500;600;700&display=swap">\n'
         '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">')
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="sun" viewBox="0 0 32 32"><circle cx="16" cy="16" r="6" fill="currentColor"/><g stroke="currentColor" stroke-width="2.2" stroke-linecap="round" fill="none"><path d="M16 3v4M16 25v4M3 16h4M25 16h4M6.8 6.8l2.8 2.8M22.4 22.4l2.8 2.8M6.8 25.2l2.8-2.8M22.4 9.6l2.8-2.8"/></g></symbol>
  <symbol id="moon" viewBox="0 0 32 32"><path d="M20.5 4.5A11.5 11.5 0 1 0 27.5 21 9 9 0 0 1 20.5 4.5z" fill="currentColor"/></symbol>
  <symbol id="pcloud" viewBox="0 0 32 32"><circle cx="11" cy="11" r="5" fill="currentColor" opacity=".55"/><path d="M10 26h14a5 5 0 0 0 0-10 7 7 0 0 0-13.4 1.8A4.2 4.2 0 0 0 10 26z" fill="currentColor"/></symbol>
  <symbol id="cloud" viewBox="0 0 32 32"><path d="M8 25h16a6 6 0 0 0 0-12 8 8 0 0 0-15.3 2.2A5 5 0 0 0 8 25z" fill="currentColor"/></symbol>
  <symbol id="rain" viewBox="0 0 32 32"><path d="M9 19h15a5 5 0 0 0 0-10 7 7 0 0 0-13.4 1.8A4.2 4.2 0 0 0 9 19z" fill="currentColor"/><g stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M11 23l-1.5 4M17 23l-1.5 4M23 23l-1.5 4"/></g></symbol>
  <symbol id="storm" viewBox="0 0 32 32"><path d="M9 18h15a5 5 0 0 0 0-10 7 7 0 0 0-13.4 1.8A4.2 4.2 0 0 0 9 18z" fill="currentColor"/><path d="M17 19l-4 6h4l-2 5 6-7h-4l2-4z" fill="currentColor"/></symbol>
  <symbol id="snow" viewBox="0 0 32 32"><path d="M9 18h15a5 5 0 0 0 0-10 7 7 0 0 0-13.4 1.8A4.2 4.2 0 0 0 9 18z" fill="currentColor"/><g fill="currentColor"><circle cx="11" cy="23" r="1.7"/><circle cx="17" cy="25" r="1.7"/><circle cx="23" cy="23" r="1.7"/><circle cx="14" cy="28.5" r="1.5"/><circle cx="20" cy="28.5" r="1.5"/></g></symbol>
  <symbol id="fog" viewBox="0 0 32 32"><g stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 11h22M3 16h26M5 21h22M8 26h16"/></g></symbol>
  <symbol id="wind" viewBox="0 0 32 32"><g stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"><path d="M4 12h15a4 4 0 1 0-4-4"/><path d="M4 18h21a4 4 0 1 1-4 4"/><path d="M4 24h9"/></g></symbol>
</svg>'''
ICONS = {"sun", "moon", "pcloud", "cloud", "rain", "storm", "snow", "fog", "wind"}


def band(t):
    """Main-app temperature color band class for a temperature in F."""
    try:
        t = int(round(float(t)))
    except (TypeError, ValueError):
        return ""
    if t <= -1: return "tb--10"
    if 30 <= t <= 32: return "tb-frz"
    return "tb-%d" % min(110, (t // 10) * 10)


def topbar(current):
    links = [("../", "Home", "home", "fa-home"), ("../east-texas/", "East Texas", "et", "fa-cloud-sun"),
             ("../nm-mountains/", "NM Mountains", "nm", "fa-mountain"), ("https://weather-1kz4.onrender.com/", "Full app", "app", "fa-chart-line")]
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if k == current else ""}><i class="fas {i}" aria-hidden="true"></i>{t}</a>' for h, t, k, i in links)
    return f'''<header class="topbar"><div class="topbar-in"><a href="../" aria-label="Ralph's Weather home"><img src="../assets/logo-mark.svg" alt="Ralph's Weather" width="300" height="60"></a><nav aria-label="Pages">{nav}</nav></div></header>'''


def icon(name):
    name = name if name in ICONS else "pcloud"
    return f'<svg aria-hidden="true"><use href="#{name}"/></svg>'


def head(title, desc, body, cls):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="../assets/logo-favicon.svg" type="image/svg+xml">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}} body{{margin:0}} img{{max-width:100%}} [hidden]{{display:none!important}}</style>
{FONTS}
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
{SPRITE}
<div class="page {cls}">
{topbar(cls)}
<main class="wrap">
{body}
</main>
</div>
</body>
</html>
'''


def mast(brand, h1, area, date_label, issued):
    return f'''  <header class="mast">
    <div class="mast-top">
      <div>
        <div class="brand">{e(brand)}</div>
        <h1>{e(h1)}</h1>
      </div>
      <div class="area">{e(area)}</div>
    </div>
    <div class="when"><b>Forecast for {e(date_label)}</b><span>Issued {e(issued)} · Updated each morning</span></div>
  </header>'''


def chips(items):
    out = "".join(f'\n    <span class="chip {e(c.get("kind", ""))}"><i></i>{e(c["text"])}</span>' for c in items[:3])
    return f'  <div class="status">{out}\n  </div>'


def hero(readings, headline, summary):
    rs = []
    for r in readings:
        rs.append(f'      <div><span class="{e(r["style"])}">{e(r["value"])}</span><small>{"<br>".join(e(x) for x in r["label"].split("|"))}</small></div>')
    return f'''  <section class="hero" aria-label="Today at a glance">
    <div class="reading">
{chr(10).join(rs)}
    </div>
    <div>
      <h2>{e(headline)}</h2>
      <p>{e(summary)}</p>
    </div>
  </section>'''


def temps(d):
    if "hi" in d or "lo" in d:
        parts = []
        if d.get("hi") is not None: parts.append(f'<span class="h">{e(str(d["hi"]))}°</span>')
        if d.get("lo") is not None: parts.append(f'<span class="l">{e(str(d["lo"]))}°</span>')
        return " / ".join(parts)
    kind = d.get("temp_kind", "")
    t = e(d.get("temp_text", ""))
    return f'<span class="{kind}">{t}</span>' if kind in ("h", "l") else t


def days(items, title, note):
    rows = "".join(
        f'\n      <div class="day{" flag" if d.get("flag") else ""}"><b>{e(d["day"])}</b>{icon(d.get("icon", ""))}'
        f'<span class="hl">{temps(d)}</span><p>{e(d["text"])}</p></div>' for d in items)
    return f'''  <section aria-label="Week ahead">
    <div class="sec-h"><h3>{e(title)}</h3><span>{e(note)}</span></div>
    <div class="days">{rows}
    </div>
  </section>'''


def panel(p, tag="section"):
    body = "".join(f"\n      <p>{e(x)}</p>" for x in p.get("paras", []))
    extra = p.get("_html", "")
    return f'''    <{tag} class="panel">
      <span class="k">{e(p["kicker"])}</span>
      <h3>{e(p["title"])}</h3>{extra}{body}
    </{tag}>'''


def panels(items):
    out, i = [], 0
    while i < len(items):
        if i + 1 < len(items):
            out.append('  <div class="grid2">\n' + panel(items[i]) + "\n" + panel(items[i + 1]) + "\n  </div>")
            i += 2
        else:
            out.append(panel(items[i]).replace("    <section", "  <section", 1).replace("\n    </section>", "\n  </section>"))
            i += 1
    return "\n\n".join(out)


def footer(links, sources):
    ls = "".join(f'\n      <a href="{e(l["url"])}">{e(l["text"])}</a>' for l in links)
    return f'''  <footer class="foot">
    <div class="links">{ls}
    </div>
    <p>Sources: {e(sources)}</p>
  </footer>'''


def table(cols, rows):
    """cols: [(header, cls)], rows: list of (row_cls, [cell_html])"""
    th = "".join(f'<th class="{c}">{e(h)}</th>' if c else f"<th>{e(h)}</th>" for h, c in cols)
    trs = []
    for rc, cells in rows:
        tds = "".join(cells)
        trs.append(f'          <tr class="{rc}">{tds}</tr>' if rc else f"          <tr>{tds}</tr>")
    return f'''    <div class="tbl">
      <table>
        <thead><tr>{th}</tr></thead>
        <tbody>
{chr(10).join(trs)}
        </tbody>
      </table>
    </div>'''


def table_panels(tables):
    """Generic table panels, e.g. "Morning lows", "Peak weather", "Travel routes":
    {"kicker","title","cols":[...],"rows":[[cell,...],...],"key_rows":[i,...],"note"}
    A first cell may be {"name","sub"}."""
    out = []
    for t in tables:
        cols = [(h, "") for h in t["cols"]]
        rows = []
        for n, row in enumerate(t["rows"]):
            cells = []
            for c, v in enumerate(row):
                if c == 0 and isinstance(v, dict):
                    cells.append(f'<td>{e(v["name"])}<span class="el">{e(v.get("sub", ""))}</span></td>')
                else:
                    cells.append(f'<td>{e(str(v))}</td>' if c == 0 else f'<td class="num">{e(str(v))}</td>')
            rows.append(("key" if n in t.get("key_rows", []) else "", cells))
        tb = table(cols, rows)
        out.append({"kicker": t["kicker"], "title": t["title"], "paras": [t["note"]] if t.get("note") else [], "_html": "\n" + tb.replace("\n    ", "\n      ")})
    return out


def east_texas(d):
    b = [mast("Ralph's Weather", "East Texas Weather", "Tyler · Smith County area", d["date_label"], d["issued"]),
         chips(d["chips"]),
         hero([{"style": "hi", "value": f'{d["hi"]}°', "label": d.get("hi_label", "High today")},
               {"style": "lo", "value": f'{d["lo"]}°', "label": d.get("lo_label", "Low tonight")}],
              d["headline"], d["summary"])]
    slots = "".join(
        f'\n      <div class="slot {band(h["temp"])}"><span class="t">{e(h["time"])}</span>{icon(h["icon"])}<span class="deg">{e(str(h["temp"]))}°</span>'
        f'<span class="d">{e(h["sky"])}</span><span class="w">{e(h["wind"])}</span></div>' for h in d["hourly"][:6])
    b.append(f'''  <section aria-label="Today hour by hour">
    <div class="sec-h"><h3>{e(d.get("hourly_title", "Today"))}</h3><span>{e(d["rain_note"])}</span></div>
    <div class="strip">{slots}
    </div>
  </section>''')
    b.append(days(d["days"], "The week ahead", d.get("days_note", "High / low")))
    facts = "".join(f'\n    <div class="fact"><div class="k">{e(f["k"])}</div><div class="v">{e(f["v"])}</div><p>{e(f["p"])}</p></div>' for f in d["facts"][:4])
    b.append(f'  <div class="facts">{facts}\n  </div>')
    b.append(panels(table_panels(d.get("tables", [])) + d["panels"]))
    b.append(footer([{"text": "Official alerts: NWS Shreveport", "url": "https://www.weather.gov/shv/"},
                     {"text": "Ralph's Weather on Facebook", "url": "https://www.facebook.com/RalphsWeather/"}], d["sources"]))
    return head("East Texas Weather | Ralph's Weather",
                "Today's forecast, the week ahead and the outlook for the Tyler and Smith County area.",
                "\n\n".join(b), "et")


def nm(d):
    b = [mast("New Mexico Mountains Weather & Info", "Northern Mountains Report", "Sangre de Cristo & Tusas Mountains", d["date_label"], d["issued"]),
         chips(d["chips"]),
         hero(d["hero"], d["headline"], d["summary"])]
    c = d["town_cols"]  # labels for the four day columns, e.g. Today high / Tonight low / Wed high / Wed night
    rows = []
    for t in d["towns"]:
        pop = int(t["pop"])
        cells = [f'<td>{e(t["name"])}<span class="el">{e(t["elev"])}</span></td>',
                 f'<td class="num hide-sm"><span class="h">{e(str(t["d1_hi"]))}°</span></td>',
                 f'<td class="num"><span class="l">{e(str(t["n1_lo"]))}°</span></td>',
                 f'<td class="num"><span class="meter"><i style="width:{pop}%"></i></span>{pop}%</td>',
                 f'<td class="num hide-sm"><span class="h">{e(str(t["d2_hi"]))}°</span></td>',
                 f'<td class="num"><span class="l">{e(str(t["n2_lo"]))}°</span></td>']
        rows.append(("key" if t.get("key") else "", cells))
    b.append(f'''  <section aria-label="Town forecasts">
    <div class="sec-h"><h3>{e(d.get("town_title", "Mountain towns"))}</h3><span>NWS Albuquerque</span></div>
{table([("Town", ""), (c[0], "hide-sm"), (c[1], ""), ("Precip", ""), (c[2], "hide-sm"), (c[3], "")], rows).replace(chr(10) + "    ", chr(10) + "    ")}
  </section>''')
    b.append(days(d["days"], "The week ahead", "Northern mountains"))
    extra = []
    if d.get("snowpack"):
        snow = table([("Station", ""), ("Depth", ""), ("Water", "")],
                     [("", [f'<td>{e(s["station"])}<span class="el">{e(s["elev"])}</span></td>',
                            f'<td class="num">{e(s["depth"])}</td>', f'<td class="num">{e(s["swe"])}</td>']) for s in d["snowpack"]])
        extra.append({"kicker": "Snowpack", "title": "Snow on the ground (SNOTEL)", "paras": [d.get("snow_note", "")] if d.get("snow_note") else [], "_html": "\n" + snow.replace("\n    ", "\n      ")})
    if d.get("ski"):
        ski = table([("Resort", ""), (d.get("ski_col", "Opens"), "")],
                    [("key" if s.get("key") else "", [f'<td>{e(s["name"])}</td>', f'<td class="num">{e(s["status"])}</td>']) for s in d["ski"]])
        extra.append({"kicker": "Ski areas", "title": d.get("ski_title", "Opening days"), "paras": [d["ski_note"]] if d.get("ski_note") else [], "_html": "\n" + ski.replace("\n    ", "\n      ")})
    extra += table_panels(d.get("tables", []))
    b.append(panels(extra + d["panels"]))
    b.append(footer([{"text": "Official alerts: NWS Albuquerque", "url": "https://www.weather.gov/abq/"},
                     {"text": "Road conditions: NMRoads", "url": "https://www.nmroads.com"},
                     {"text": "NM Mountains Weather on Facebook", "url": "https://www.facebook.com/jicaritapeak/"}], d["sources"]))
    return head("Northern Mountains Report | NM Mountains Weather & Info",
                "Town forecasts, snowpack, ski area openings and road conditions for the northern New Mexico mountains.",
                "\n\n".join(b), "nm")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "today.json")
    data = json.load(open(path, encoding="utf-8"))
    for folder, fn, key in (("east-texas", east_texas, "east_texas"), ("nm-mountains", nm, "nm")):
        os.makedirs(os.path.join(ROOT, folder), exist_ok=True)
        with open(os.path.join(ROOT, folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(fn(data[key]))
        print("wrote", folder + "/index.html")


if __name__ == "__main__":
    main()
