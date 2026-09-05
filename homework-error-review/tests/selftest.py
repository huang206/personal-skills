#!/usr/bin/env python3
"""selftest.py — one-command install verification for homework-error-review.

Verifies, on any platform (Windows: python/py; macOS/Linux: python3):
  1. Python dependencies present (pillow, pillow-heif; pymupdf optional)
  2. Fonts available in assets/fonts (static trio or variable fallback)
  3. A renderer exists (Node+playwright or a Chromium-family browser)
  4. Full build pipeline works: make_pdf.py on the bundled template renders a PDF
     that passes the QA gate (fill warnings on placeholder pages are expected)

Usage:  python3 tests/selftest.py
Exit 0 = environment fully working; 1 = something to fix (messages explain what).
"""
import os
import subprocess
import sys
import tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(SKILL_DIR, "scripts")

RESULTS = []


def check(name, ok, hint=""):
    RESULTS.append((name, ok, hint))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {hint}" if not ok and hint else ""))


def main():
    print("homework-error-review self-test")
    print("== 1. Python dependencies ==")
    for mod, hint in (("PIL", "pip install pillow"),
                      ("pillow_heif", "pip install pillow-heif")):
        try:
            __import__(mod)
            check(f"{hint.split()[-1]} importable", True)
        except ImportError:
            check(f"{hint.split()[-1]} importable", False, hint)
    try:
        import pymupdf  # noqa
        check("pymupdf importable", True)
    except ImportError:
        try:
            import fitz  # noqa
            check("pymupdf importable (fitz)", True)
        except ImportError:
            check("pymupdf importable", False, "pip install pymupdf (QA degrades without it)")

    print("== 2. Fonts ==")
    fonts = os.path.join(SKILL_DIR, "assets", "fonts")
    static = [w for w in (400, 700, 900)
              if os.path.isfile(os.path.join(fonts, f"NotoSansSC-{w}.ttf"))
              and os.path.getsize(os.path.join(fonts, f"NotoSansSC-{w}.ttf")) > 1_000_000]
    vf = os.path.join(fonts, "NotoSansSC-VF.ttf")
    have_fonts = len(static) == 3 or (os.path.isfile(vf) and os.path.getsize(vf) > 1_000_000)
    check("fonts in assets/fonts", have_fonts,
          f"run: python3 {os.path.join(SCRIPTS, 'setup_env.py')} (network needed once)")

    print("== 3. Renderer ==")
    import shutil
    node = shutil.which("node")
    pw = False
    if node:
        try:
            subprocess.run([node, "-e", "require('playwright')"], check=True,
                           capture_output=True, timeout=30)
            pw = True
        except Exception:
            pass
    sys.path.insert(0, SCRIPTS)
    from render_browser import find_browser  # noqa: E402
    browser = find_browser()
    check("renderer available", bool(pw or browser),
          "install playwright (npm i -g playwright && npx playwright install chromium) "
          "or a Chromium browser (Chrome/Edge)")

    print("== 4. Full build (template render + QA gate) ==")
    with tempfile.TemporaryDirectory(prefix="her_selftest_") as td:
        out = os.path.join(td, "selftest.pdf")
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "make_pdf.py"),
                            os.path.join(SKILL_DIR, "assets", "template.html"),
                            "--output", out], capture_output=True, text=True, timeout=300)
        built = os.path.isfile(out) and os.path.getsize(out) > 1024
        check("make_pdf.py produced a PDF", built, r.stdout[-400:] + r.stderr[-400:])
        if built:
            gate = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check_pdf.py"), out],
                                  capture_output=True, text=True, timeout=120)
            # exit 0 = PASS (fill warnings on placeholder template pages are expected)
            check("QA gate passed", gate.returncode in (0, 2), gate.stdout[-300:])

    fails = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} checks passed"
          + ("" if not fails else f" — fix: {', '.join(fails)}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
