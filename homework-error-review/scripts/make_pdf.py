#!/usr/bin/env python3
"""make_pdf.py — one-command cross-platform build: fonts → render → QA.

Steps:
  1. Copy the booklet HTML and inject the Noto Sans SC fonts (from assets/fonts/)
     as base64 data-URI @font-face rules. Base64 embedding is the reliable way to
     load local fonts in a file:// page (Chromium CORS-blocks relative-path
     @font-face) and removes any OS-level font installation requirement.
  2. Render via Node+playwright (scripts/render_pdf.js); on any failure, fall
     back to the system browser (scripts/render_browser.py — Chrome/Edge/Chromium).
  3. Run the QA gate (scripts/check_pdf.py) and summarize.

Usage:
    python3 scripts/make_pdf.py booklet.html --output booklet.pdf
Windows: use `python` / `py` instead of `python3`.
"""
import base64
import os
import shutil
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(SKILL_DIR, "scripts")
FONTS_DIR = os.path.join(SKILL_DIR, "assets", "fonts")
STATIC_WEIGHTS = (400, 700, 900)


def build_font_css():
    """Return a <style> block embedding local fonts, or '' if unavailable."""
    faces = []
    static = {}
    for w in STATIC_WEIGHTS:
        p = os.path.join(FONTS_DIR, f"NotoSansSC-{w}.ttf")
        if os.path.isfile(p) and os.path.getsize(p) > 1_000_000:
            static[w] = p
    if len(static) == len(STATIC_WEIGHTS):
        for w, p in static.items():
            b64 = base64.b64encode(open(p, "rb").read()).decode("ascii")
            faces.append(
                f'@font-face {{ font-family: "NotoSansSC-Local"; '
                f'src: url(data:font/ttf;base64,{b64}) format("truetype"); '
                f'font-weight: {w}; font-style: normal; }}')
    else:
        vf = os.path.join(FONTS_DIR, "NotoSansSC-VF.ttf")
        if os.path.isfile(vf) and os.path.getsize(vf) > 1_000_000:
            b64 = base64.b64encode(open(vf, "rb").read()).decode("ascii")
            faces.append(
                f'@font-face {{ font-family: "NotoSansSC-Local"; '
                f'src: url(data:font/ttf;base64,{b64}) format("truetype"); '
                f'font-weight: 100 900; font-style: normal; }}')
        else:
            return "", len(static)
    return "\n".join(faces), len(static)


def inject(html_path, css):
    out_html = html_path[:-5] + ".render.html" if html_path.lower().endswith(".html") \
        else html_path + ".render.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    block = f"<style>\n{css}\n</style>\n"
    if "</head>" in html:
        html = html.replace("</head>", block + "</head>", 1)
    elif "</HEAD>" in html:
        html = html.replace("</HEAD>", block + "</HEAD>", 1)
    else:
        html = block + html
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return out_html


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)


def main():
    args = sys.argv[1:]
    out = None
    positional = []
    it = iter(args)
    for a in it:
        if a in ("--output", "-o"):
            out = next(it, None)
        else:
            positional.append(a)
    if not positional:
        print(__doc__)
        return 1
    src = os.path.abspath(positional[0])
    if not os.path.isfile(src):
        print(f"[make_pdf] input not found: {src}")
        return 1
    out = os.path.abspath(out or os.path.splitext(src)[0] + ".pdf")

    # 1) fonts
    css, n_static = build_font_css()
    if css:
        src_render = inject(src, css)
        print(f"[make_pdf] embedded {n_static if n_static == 3 else 'variable'} "
              f"Noto Sans SC font(s) as base64 @font-face")
    else:
        src_render = src
        print("[make_pdf] WARN: bundled fonts missing in assets/fonts/ — relying on "
              "system fonts. Run: python3 scripts/setup_env.py (network needed once).")

    # 2) render: Node+playwright first, system browser fallback
    rendered = False
    node = shutil.which("node")
    if node:
        r = run([node, os.path.join(SCRIPTS, "render_pdf.js"), src_render,
                 "--output", out])
        if r.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 0:
            print(r.stdout.strip())
            rendered = True
        else:
            print(f"[make_pdf] playwright path failed ({r.returncode}): "
                  f"{(r.stderr or r.stdout).strip()[:300]}")
    else:
        print("[make_pdf] node not found — using system-browser renderer")
    if not rendered:
        r = run([sys.executable, os.path.join(SCRIPTS, "render_browser.py"),
                 src_render, out])
        print(r.stdout.strip())
        if not (r.returncode == 0 and os.path.isfile(out) and os.path.getsize(out) > 0):
            print(f"[make_pdf] RENDER FAILED.\n{r.stderr.strip()[:500]}")
            return 1

    # cleanup the render copy (keep on failure path for debugging)
    if css and os.path.isfile(src_render):
        os.remove(src_render)

    # 3) QA gate
    r = run([sys.executable, os.path.join(SCRIPTS, "check_pdf.py"), out])
    print(r.stdout.strip())
    if r.returncode == 2:
        print("[make_pdf] QA ran in degraded mode (install pymupdf for full checks)")
        return 0
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
