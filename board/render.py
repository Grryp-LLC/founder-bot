#!/usr/bin/env python3
"""Founder Bot Launch Board renderer: a mission-control progress card, HTML/CSS -> PNG via Playwright.

  python render.py spec.json --out ./out [--sizes landscape,portrait] [--sample] [--deny "Name,Other"] [--html]

Sizes: landscape 1200x675, portrait 1080x1350 (X-friendly). The spec comes from `engine/board.py spec`.
Every visible string passes the privacy lint first; a violation aborts with exit 2 and nothing is rendered.
"""
import argparse, asyncio, html, json, os, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import privacy  # noqa: E402

FONTS = HERE / "fonts"
SIZES = {"landscape": (1200, 675), "portrait": (1080, 1350)}
GREEN, AMBER, DIM, CYAN, RED = "#39ff9f", "#ffb547", "#56607a", "#5fd4ff", "#ff5b5b"


def esc(s):
    return html.escape(str(s if s is not None else ""))


def font_css():
    need = {"Orb": "Orbitron.ttf", "Grot": "SpaceGrotesk.ttf", "Mono": "JetBrainsMono.ttf"}
    missing = [f for f in need.values() if not (FONTS / f).exists()]
    if missing:
        sys.exit("fonts missing in board/fonts: " + ", ".join(missing) + " (run ./install.sh)")
    return "\n".join(f"@font-face{{font-family:'{k}';src:url('{(FONTS / v).as_uri()}');font-weight:100 900;}}"
                     for k, v in need.items())


def stars(w, h, seed, n):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, s = r.random() * w, r.random() * h * .8, r.choice([.6, .8, 1, 1, 1.4, 2])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s}" fill="#fff" opacity="{r.uniform(.25, .9):.2f}"/>')
    return f'<svg class="stars" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(out)}</svg>'


def rocket_svg(pct, h, k=1.0):
    """Launch tower + rocket. The rocket climbs with progress; flame grows; 100% = liftoff clear of the tower."""
    W = int(230 * k)
    ground = h - 40
    climb = (h - 270 * k) * pct / 100
    ry = ground - 190 * k - climb                                  # rocket top y
    flame = 0 if pct == 0 else 26 + 60 * pct / 100 + (50 if pct >= 100 else 0)
    smoke = "".join(f'<circle cx="{cx}" cy="{ground - 6 + dy}" r="{r}" fill="#cfd6ea" opacity="{op}"/>'
                    for cx, dy, r, op in [(70, 0, 22, .18), (100, 6, 28, .22), (140, 4, 30, .22),
                                          (175, 2, 22, .18), (120, -8, 20, .16)]) if pct > 0 else ""
    lattice = "".join(f'<line x1="18" y1="{y}" x2="42" y2="{y + 22}" stroke="#46506b" stroke-width="2"/>'
                      f'<line x1="42" y1="{y}" x2="18" y2="{y + 22}" stroke="#46506b" stroke-width="2"/>'
                      for y in range(int(ground - 250), int(ground), 22))
    ticks = "".join(f'<line x1="{W - 18}" y1="{ground - 10 - (h - 170) * i / 10:.0f}" x2="{W - (8 if i % 5 else 2)}" '
                    f'y2="{ground - 10 - (h - 170) * i / 10:.0f}" stroke="#5a6788" stroke-width="2"/>' for i in range(11))
    mark_y = ground - 10 - (h - 170) * pct / 100
    cx = int(120 * k)
    return f'''
<svg class="rocket" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
 <defs>
  <linearGradient id="body" x1="0" x2="1"><stop offset="0" stop-color="#cfd6e8"/><stop offset=".45" stop-color="#ffffff"/><stop offset="1" stop-color="#9aa6c4"/></linearGradient>
  <radialGradient id="fl" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#fff6c9"/><stop offset=".35" stop-color="{AMBER}"/><stop offset="1" stop-color="#ff4d2e" stop-opacity="0"/></radialGradient>
 <linearGradient id="trail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd27a" stop-opacity=".75"/><stop offset="1" stop-color="#cfd6ea" stop-opacity=".05"/></linearGradient>
 </defs>
 <g transform="translate(0,{ground}) scale({k}) translate(0,{-ground})">
 <line x1="30" y1="{ground - 262}" x2="30" y2="{ground}" stroke="#46506b" stroke-width="3"/>
 {lattice}
 <line x1="18" y1="{ground - 262}" x2="18" y2="{ground}" stroke="#46506b" stroke-width="3"/>
 <line x1="42" y1="{ground - 262}" x2="42" y2="{ground}" stroke="#46506b" stroke-width="3"/>
 <line x1="42" y1="{ground - 200}" x2="{(cx - 22 * k) / k:.0f}" y2="{ground - 200}" stroke="#46506b" stroke-width="4" opacity="{0 if pct >= 100 else 1}"/>
 <circle cx="30" cy="{ground - 266}" r="4" fill="{RED}"/>
 </g>
 <rect x="0" y="{ground}" width="{W}" height="4" fill="#2d3550"/>
 {smoke}
 {f'<rect x="{cx - 9 * k:.0f}" y="{ry + (170 + flame * .6) * k:.0f}" width="{18 * k:.0f}" height="{max(ground - ry - (170 + flame * .6) * k, 0):.0f}" rx="9" fill="url(#trail)"/>' if pct >= 100 else ''}
 <g transform="translate({cx},{ry:.0f}) scale({k})">
  <path d="M0 {170} Q -14 {170 + flame * .55} 0 {170 + flame} Q 14 {170 + flame * .55} 0 170 Z" fill="url(#fl)" transform="scale(1.6,1) translate(-0,0)"/>
  <path d="M-22 150 L-40 176 L-40 186 L-20 168 Z" fill="{RED}"/>
  <path d="M22 150 L40 176 L40 186 L20 168 Z" fill="{RED}"/>
  <path d="M0 0 C 26 26 26 60 24 110 L 22 168 L -22 168 L -24 110 C -26 60 -26 26 0 0 Z" fill="url(#body)"/>
  <path d="M0 0 C 12 12 18 24 20 34 L -20 34 C -18 24 -12 12 0 0 Z" fill="{RED}"/>
  <circle cx="0" cy="70" r="11" fill="#11203f" stroke="#8fa0c6" stroke-width="3"/>
  <circle cx="-3" cy="67" r="3" fill="{CYAN}" opacity=".8"/>
  <rect x="-22" y="118" width="44" height="6" fill="#aab4cf"/>
  <path d="M-3 110 L-3 168 L3 168 L3 110 Z" fill="{RED}" opacity=".9"/>
 </g>
 {ticks}
 <path d="M{W - 24} {mark_y:.0f} l-10 -7 v14 z" fill="{GREEN}"/>
</svg>'''


def stage_row(i, s):
    done, total = s["done"], max(s["total"], 1)
    state, color = ("GO", GREEN) if done >= total else (("BURN", AMBER) if done else ("STANDBY", DIM))
    segs = "".join(f'<i style="background:{GREEN if k < done else "#1b2340"};'
                   f'box-shadow:{"0 0 8px " + GREEN + "88" if k < done else "none"}"></i>' for k in range(total))
    return f'''<div class="stage">
  <div class="sl"><span class="sn">STAGE {i}</span><span class="sname">{esc(s["label"])}</span></div>
  <div class="segs">{segs}</div>
  <div class="sc">{done}/{total}</div>
  <div class="light" style="color:{color};border-color:{color}"><b style="background:{color};box-shadow:0 0 10px {color}"></b>{state}</div>
</div>'''


def countdown(days):
    if days > 0:
        return "T-MINUS", f"{days}", "DAYS TO LAUNCH" if days != 1 else "DAY TO LAUNCH"
    if days == 0:
        return "T-ZERO", "LIFTOFF", "LAUNCH DAY"
    return "T-PLUS", f"{-days}", "DAYS SINCE LAUNCH"


def title_size(name, port):
    avail = 964 if port else 560
    n = max(len(name), 1)
    if port:
        return max(40, min(72, int(avail * 2 / (0.8 * n)))) if n > 18 else 72
    return max(24, min(44, int(avail / (0.9 * n))))


def build_html(spec, size, sample):
    W, H = SIZES[size]
    port = size == "portrait"
    P = (lambda p, l: p if port else l)
    pct = round(100 * spec["done"] / spec["total"]) if spec["total"] else 0
    lab, num, sub = countdown(spec["days_to_launch"])
    status = "LIFTOFF" if pct >= 100 else ("ALL SYSTEMS GO" if pct >= 75 else ("IGNITION" if pct >= 40 else ("FUELING" if pct > 0 else "ON THE PAD")))
    rows = "".join(stage_row(i + 1, s) for i, s in enumerate(spec["stages"]))
    nxt = "".join(f'<li><span class="k">{k + 1:02d}</span>{esc(t)}</li>' for k, t in enumerate(spec["next"][:3])) \
        or '<li><span class="k">--</span>All burns complete. We have liftoff.</li>'
    stamp = '<div class="stamp">SAMPLE · DEMO DATA</div>' if sample else ""
    tfs = title_size(spec["mission"], port)
    M = P(58, 44)
    css = f"""
{font_css()}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:'Grot',sans-serif;color:#e8ecf8;
 background:radial-gradient(120% 90% at 70% 110%,#1e2a63 0%,#0b1233 45%,#050816 100%);position:relative}}
.stars{{position:absolute;inset:0}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(#ffffff07 1px,transparent 1px),linear-gradient(90deg,#ffffff07 1px,transparent 1px);background-size:40px 40px}}
.glow{{position:absolute;left:-20%;width:{P(900, 700)}px;bottom:-{P(200, 150)}px;height:{P(360, 260)}px;background:radial-gradient(50% 50% at 50% 50%,#ff8a3d44,transparent 70%)}}
.frame{{position:absolute;inset:{P(22, 18)}px;border:1.5px solid #2b3a6e;border-radius:18px;box-shadow:inset 0 0 40px #0008}}
.frame:before,.frame:after{{content:"";position:absolute;width:26px;height:26px;border:3px solid {CYAN}}}
.frame:before{{top:-3px;left:-3px;border-right:0;border-bottom:0;border-radius:14px 0 0 0}}
.frame:after{{bottom:-3px;right:-3px;border-left:0;border-top:0;border-radius:0 0 14px 0}}
.top{{position:absolute;left:{M}px;right:{M}px;top:{P(50, 36)}px;display:flex;justify-content:space-between;font-family:'Mono';font-size:{P(17, 13)}px;letter-spacing:.18em;color:{CYAN}}}
.top .dot{{display:inline-block;width:10px;height:10px;border-radius:50%;background:{RED};box-shadow:0 0 10px {RED};margin-right:10px;vertical-align:1px}}
.title{{position:absolute;left:{M}px;top:{P(94, 64)}px;width:{P(964, 600)}px}}
.eyebrow{{font-family:'Orb';font-weight:600;font-size:{P(20, 14)}px;letter-spacing:.34em;color:#9fb0dc}}
h1{{font-family:'Orb';font-weight:900;font-size:{tfs}px;line-height:1.04;margin-top:{P(8, 4)}px;text-transform:uppercase;
 background:linear-gradient(180deg,#fff,#b9c6ee);-webkit-background-clip:text;color:transparent;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;{'' if port else 'white-space:nowrap;text-overflow:ellipsis;display:block'}}}
.count{{position:absolute;{'left:58px;top:306px;display:flex;align-items:center;gap:26px' if port else 'right:44px;top:60px;width:280px;text-align:right'}}}
.count .lab{{font-family:'Mono';letter-spacing:.3em;color:{AMBER};font-size:{P(20, 13)}px}}
.count .num{{font-family:'Orb';font-weight:900;font-size:{P(150, 92)}px;line-height:.95;color:{AMBER};text-shadow:0 0 24px {AMBER}66}}
.count .num.word{{font-size:{P(84, 50)}px;letter-spacing:.02em;padding:{P(0, 6)}px 0}}
.count .sub{{font-family:'Mono';font-size:{P(18, 12)}px;letter-spacing:.16em;line-height:1.5;color:#c7d0ea}}
.rocketwrap{{position:absolute;left:{P(40, 26)}px;top:{P(480, 150)}px}}
.pct{{position:absolute;left:{P(330, 262)}px;top:{P(500, 136)}px;display:flex;align-items:baseline;gap:{P(24, 18)}px}}
.pct .big{{font-family:'Orb';font-weight:900;font-size:{P(116, 68)}px;line-height:1;color:{GREEN};text-shadow:0 0 26px {GREEN}66}}
.pct .st{{font-family:'Mono';letter-spacing:.2em;font-size:{P(19, 13)}px;color:#dfe6fb;line-height:1.6}}
.pct .st b{{color:{GREEN};display:block;font-size:{P(24, 16)}px}}
.stages{{position:absolute;left:{P(330, 262)}px;right:{M}px;top:{P(660, 226)}px;display:flex;flex-direction:column;gap:{P(20, 9)}px}}
.stage{{display:flex;align-items:center;gap:{P(16, 12)}px;height:{P(50, 38)}px}}
.sl{{width:{P(176, 146)}px;flex-shrink:0;display:flex;flex-direction:column}}
.sn{{font-family:'Mono';font-size:{P(13, 10)}px;letter-spacing:.2em;color:#7f8db6}}
.sname{{font-family:'Orb';font-weight:700;font-size:{P(22, 17)}px;letter-spacing:.05em}}
.segs{{flex:1;display:flex;gap:4px;height:{P(26, 20)}px}}
.segs i{{flex:1;border-radius:3px}}
.sc{{font-family:'Mono';font-size:{P(20, 15)}px;width:{P(64, 50)}px;flex-shrink:0;text-align:right;color:#dfe6fb}}
.light{{flex-shrink:0;font-family:'Mono';font-weight:700;font-size:{P(15, 12)}px;letter-spacing:.14em;border:1.5px solid;border-radius:999px;padding:{P(6, 4)}px {P(12, 10)}px;width:{P(130, 106)}px;display:flex;align-items:center;gap:8px}}
.light b{{width:9px;height:9px;border-radius:50%}}
.burns{{position:absolute;left:{P(58, 262)}px;right:{M}px;top:{P(1070, 478)}px;height:{P(170, 118)}px;display:flex;gap:{P(24, 16)}px}}
.panel{{background:#0c1433cc;border:1.5px solid #2b3a6e;border-radius:12px;padding:{P(18, 11)}px {P(22, 16)}px}}
.panel h3{{font-family:'Mono';font-size:{P(14, 11)}px;letter-spacing:.26em;color:{CYAN};font-weight:700;margin-bottom:{P(10, 6)}px}}
.next{{flex:1;min-width:0}}
.next ul{{list-style:none}}
.next li{{font-size:{P(23, 16)}px;line-height:1.42;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.next .k{{font-family:'Mono';color:{AMBER};margin-right:12px}}
.wins{{width:{P(220, 150)}px;flex-shrink:0;display:flex;flex-direction:column;justify-content:center;align-items:center}}
.wins .n{{font-family:'Orb';font-weight:900;font-size:{P(70, 46)}px;color:{GREEN};line-height:1.05;text-shadow:0 0 18px {GREEN}55}}
.wins .t{{font-family:'Mono';font-size:{P(13, 10)}px;letter-spacing:.2em;color:#c7d0ea;text-align:center}}
.foot{{position:absolute;left:{M}px;right:{M}px;bottom:{P(46, 30)}px;display:flex;justify-content:space-between;font-family:'Mono';font-size:{P(15, 11)}px;letter-spacing:.14em;color:#7f8db6}}
.stamp{{position:absolute;{'right:64px;top:436px' if port else 'left:640px;top:150px'};transform:rotate(-7deg);font-family:'Mono';font-weight:800;font-size:{P(22, 15)}px;letter-spacing:.2em;color:{RED};border:3px solid {RED};border-radius:8px;padding:6px 14px;opacity:.9;background:#05081699}}
"""
    body = f"""
{stars(W, H, sum(map(ord, spec['mission'])), P(170, 130))}
<div class="grid"></div><div class="glow"></div><div class="frame"></div>
<div class="top"><span><span class="dot"></span>FOUNDER BOT // LAUNCH BOARD</span><span>{esc(spec['week_label']).upper()}</span></div>
<div class="title"><div class="eyebrow">MISSION</div><h1>{esc(spec['mission'])}</h1></div>
<div class="count"><div class="lab">{lab}</div><div class="num{' word' if not num.isdigit() else ''}">{num}</div><div class="sub">{sub}<br>{esc(spec['launch_label']).upper()}</div></div>
<div class="rocketwrap">{rocket_svg(pct, P(620, 490), P(1.3, 1.0))}</div>
<div class="pct"><div class="big">{pct}%</div><div class="st">STATUS<b>{status}</b></div></div>
<div class="stages">{rows}</div>
<div class="burns"><div class="panel next"><h3>NEXT BURNS</h3><ul>{nxt}</ul></div>
<div class="panel wins"><div class="n">{spec['wins_week']}</div><div class="t">WINS<br>THIS WEEK</div></div></div>
<div class="foot"><span>{spec['done']}/{spec['total']} CHECKLIST ITEMS GO</span><span>BUILT WITH FOUNDER BOT · A GROK BOT TEMPLATE</span></div>
{stamp}"""
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"


async def shoot(html_path, png_path, W, H):
    from playwright.async_api import async_playwright
    exe = os.environ.get("CHROME_PATH") or next((p for p in ["/usr/bin/google-chrome", "/usr/bin/chromium",
                                                             "/usr/bin/chromium-browser"] if os.path.exists(p)), None)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=exe, args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        await pg.goto(Path(html_path).resolve().as_uri())
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(150)
        await pg.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": W, "height": H})
        await b.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("--out", default="out")
    ap.add_argument("--sizes", default="landscape,portrait"); ap.add_argument("--sample", action="store_true")
    ap.add_argument("--deny", default="", help="comma list of names that must never appear")
    ap.add_argument("--html", action="store_true", help="also keep the HTML")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    deny = [x for x in a.deny.split(",") if x.strip()] + spec.get("deny_names", [])
    probs = privacy.lint(privacy.spec_text(spec), deny)
    if probs:
        print("privacy gate: refusing to render: " + ", ".join(probs), file=sys.stderr)
        sys.exit(2)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.spec).stem
    for size in a.sizes.split(","):
        W, H = SIZES[size]
        hp = out / f"{stem}-{W}x{H}.html"
        hp.write_text(build_html(spec, size, a.sample or spec.get("sample", False)))
        png = out / f"{stem}-{W}x{H}.png"
        asyncio.run(shoot(hp, png, W, H))
        if not a.html:
            hp.unlink()
        print(png)


if __name__ == "__main__":
    main()
