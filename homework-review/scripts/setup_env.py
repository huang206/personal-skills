#!/usr/bin/env python3
"""setup_env.py — cross-platform first-use setup for homework-review.

Windows / macOS / Ubuntu. Checks and prepares:
  1. Fonts: downloads Noto Sans SC 400/700/900 TTFs into <skill>/assets/fonts/
     (NOT installed into the OS — make_pdf.py embeds them per-build as base64).
  2. Python deps: pillow, pillow-heif, pymupdf (optional, QA degrades without).
  3. Renderer: Node+playwright OR a system Chromium browser (Chrome/Edge/Chromium;
     Edge ships with Windows 10/11).
Prints per-OS install hints. Safe to re-run. Exit 0 always (informational).

Run:  python3 scripts/setup_env.py     (Windows: python / py)
"""
import os
import sys
import urllib.request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(SKILL_DIR, "assets", "fonts")

FONT_URLS = {
    # Static TTF instances (TrueType outlines — required; CFF/OTF "Noto Sans CJK"
    # variants embed badly in some pipelines). Verified Google Fonts direct links.
    400: "https://fonts.gstatic.com/s/notosanssc/v40/k3kCo84MPvpLmixcA63oeAL7Iqp5IZJF9bmaG9_FnYw.ttf",
    700: "https://fonts.gstatic.com/s/notosanssc/v40/k3kCo84MPvpLmixcA63oeAL7Iqp5IZJF9bmaGzjCnYw.ttf",
    900: "https://fonts.gstatic.com/s/notosanssc/v40/k3kCo84MPvpLmixcA63oeAL7Iqp5IZJF9bmaG3bCnYw.ttf",
}
# Google Fonts occasionally rotates URLs; this variable font is a stable fallback.
FONT_FALLBACK = ("https://github.com/google/fonts/raw/main/ofl/notosanssc/"
                 "NotoSansSC%5Bwght%5D.ttf")

BROWSERS = {
    "win32": [
        r"{LOCALAPPDATA}\Google\Chrome\Application\chrome.exe",
        r"{PROGRAMFILES}\Google\Chrome\Application\chrome.exe",
        r"{PROGRAMFILES(X86)}\Google\Chrome\Application\chrome.exe",
        r"{PROGRAMFILES(X86)}\Microsoft\Edge\Application\msedge.exe",
        r"{PROGRAMFILES}\Microsoft\Edge\Application\msedge.exe",
    ],
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ],
    "linux": [
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/opt/google/chrome/chrome", "/opt/microsoft/msedge/msedge",
    ],
}
BROWSER_NAMES = ["google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "chrome", "msedge"]

PY_HINTS = {
    "win32": "py -m pip install pillow pillow-heif pymupdf",
    "darwin": "python3 -m pip install pillow pillow-heif pymupdf",
    "linux": "python3 -m pip install pillow pillow-heif pymupdf",
}
BROWSER_HINTS = {
    "win32": "Nothing to do — Edge ships with Windows 10/11 (or: winget install Google.Chrome)",
    "darwin": "brew install --cask google-chrome   (or install Edge/Chrome from the web)",
    "linux": "sudo apt install chromium-browser   # or google-chrome-stable / microsoft-edge",
}


def ok(msg):
    print(f"  [OK]   {msg}")


def warn(msg):
    print(f"  [WARN] {msg}")


def download_font(weight, dest):
    url = FONT_URLS[weight]
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        raise IOError(f"static weight {weight} URL failed")
    with open(dest, "rb") as f:
        if f.read(4) != b"\x00\x01\x00\x00":
            raise IOError("not a TTF (bad magic bytes)")


def download_variable_font():
    """One-time fallback: the variable TTF covers weights 100–900."""
    dest = os.path.join(FONTS_DIR, "NotoSansSC-VF.ttf")
    urllib.request.urlretrieve(FONT_FALLBACK, dest)
    with open(dest, "rb") as f:
        if f.read(4) != b"\x00\x01\x00\x00":
            os.remove(dest)
            raise IOError("variable font download failed validation")


def setup_fonts():
    print("== Fonts (Noto Sans SC -> assets/fonts/, no OS install) ==")
    os.makedirs(FONTS_DIR, exist_ok=True)
    missing = [w for w in FONT_URLS
               if not (os.path.exists(path := os.path.join(FONTS_DIR, f"NotoSansSC-{w}.ttf"))
                       and os.path.getsize(path) > 1_000_000)]
    vf = os.path.join(FONTS_DIR, "NotoSansSC-VF.ttf")
    if not missing and not (os.path.isfile(vf) and os.path.getsize(vf) > 1_000_000):
        ok("fonts present in assets/fonts/")
        return
    if missing:
        print(f"  downloading weights {missing} (needs network, once)...")
        failed = []
        for w in missing:
            dest = os.path.join(FONTS_DIR, f"NotoSansSC-{w}.ttf")
            try:
                download_font(w, dest)
                ok(f"NotoSansSC-{w}.ttf downloaded")
            except Exception as e:
                failed.append(w)
                if os.path.isfile(dest):
                    os.remove(dest)
                warn(f"NotoSansSC-{w}.ttf: {e}")
        if failed and not (os.path.isfile(vf) and os.path.getsize(vf) > 1_000_000):
            try:
                download_variable_font()
                ok("variable font NotoSansSC-VF.ttf downloaded (covers all weights)")
                failed = []
            except Exception as e:
                warn(f"variable font fallback failed: {e}")
        if failed:
            warn(f"manual fallback: download static TTFs from "
                 f"https://fonts.google.com/noto/specimen/Noto+Sans+SC into {FONTS_DIR}")


def check_python_deps():
    print("== Python dependencies ==")
    for mod, pip_name, optional in (("PIL", "pillow", False),
                                    ("pillow_heif", "pillow-heif", False),
                                    ("pymupdf", "pymupdf", True)):
        try:
            __import__(mod)
            ok(f"{pip_name} available")
        except ImportError:
            try:
                import fitz  # pymupdf legacy import name
                if mod == "pymupdf":
                    ok("pymupdf available (via fitz)")
                    continue
            except ImportError:
                pass
            msg = f"{pip_name} missing — {PY_HINTS.get(sys.platform, PY_HINTS['linux'])}"
            (warn(msg + "  (QA degrades gracefully)") if optional
             else warn(msg))


def find_browsers():
    import shutil
    found = []
    for tmpl in BROWSERS.get(sys.platform, BROWSERS["linux"]):
        p = os.path.expandvars(tmpl)
        if os.path.isfile(p):
            found.append(p)
    for name in BROWSER_NAMES:
        p = shutil.which(name)
        if p:
            found.append(p)
    return found


def check_renderer():
    print("== Renderer (need ONE of: Node+playwright, or a Chromium browser) ==")
    import shutil
    node = shutil.which("node")
    pw_ok = False
    if node:
        import subprocess
        try:
            subprocess.run([node, "-e", "require('playwright')"], check=True,
                           capture_output=True, timeout=30)
            pw_ok = True
        except Exception:
            pass
    if pw_ok:
        ok("Node.js + playwright resolvable")
    else:
        hint = ("npm i -g playwright && npx playwright install chromium"
                if node else "install Node.js, or rely on a system browser below")
        warn(f"playwright not available — {hint}")

    browsers = find_browsers()
    if browsers:
        ok(f"system browser: {browsers[0]}" + (" (fallback ready)" if pw_ok else " (renderer ready)"))
    elif pw_ok:
        warn("no system browser — playwright's downloaded chromium will be used "
             "(run: npx playwright install chromium)")
    else:
        warn("NO RENDERER: install playwright (above) or a browser — "
             f"{BROWSER_HINTS.get(sys.platform, BROWSER_HINTS['linux'])}")


def main():
    print(f"homework-review setup — {sys.platform}")
    setup_fonts()
    check_python_deps()
    check_renderer()
    print("\nSetup check complete. Re-run anytime; all steps are idempotent.")


if __name__ == "__main__":
    main()
