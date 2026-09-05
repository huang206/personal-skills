#!/usr/bin/env python3
"""render_browser.py — system-browser fallback renderer (no Node needed).

Works on Windows (Chrome, or Edge which ships with 10/11), macOS (Chrome/Edge/
Chromium), and Linux. Finds a Chromium-family browser, prints to PDF headlessly.

Edge/Chrome quirks handled (verified):
  - dedicated --user-data-dir in a temp dir (Edge fails outright if a UI instance
    is running; also avoids profile locks)
  - forward slashes in the output path (Windows CLI parsing)
  - --headless (new mode; old headless removed in Chrome/Edge 132+)
  - --no-pdf-header-footer for clean margins

Usage:  python3 scripts/render_browser.py input.html [output.pdf]
"""
import os
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = {
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
PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium",
              "chromium-browser", "chrome", "msedge"]


def find_browser():
    for tmpl in CANDIDATES.get(sys.platform, CANDIDATES["linux"]):
        p = os.path.expandvars(tmpl)
        if os.path.isfile(p):
            return p
    for name in PATH_NAMES:
        p = shutil.which(name)
        if p:
            return p
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = os.path.abspath(sys.argv[1])
    if not os.path.isfile(src):
        print(f"[render_browser] input not found: {src}")
        return 1
    out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2
                          else os.path.splitext(src)[0] + ".pdf")

    exe = find_browser()
    if not exe:
        print("[render_browser] no Chromium-family browser found "
              "(Chrome / Edge / Chromium). Install one, or use Node+playwright.")
        return 2

    with tempfile.TemporaryDirectory(prefix="her_browser_") as profile:
        cmd = [
            exe,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--user-data-dir={profile}",          # mandatory for Edge; harmless for Chrome
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=10000",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out.replace(os.sep, '/')}",  # forward slashes (Windows)
            "file:///" + src.replace(os.sep, "/").lstrip("/"),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if os.path.isfile(out) and os.path.getsize(out) > 0:
            print(f"[render_browser] wrote {out} ({os.path.getsize(out)//1024} KB) via {exe}")
            return 0
        print(f"[render_browser] failed via {exe}\n  stderr: {r.stderr[:500]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
