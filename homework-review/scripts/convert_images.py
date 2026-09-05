#!/usr/bin/env python3
"""convert_images.py — cross-platform homework photo ingestion (HEIC/JPG → normalized JPG).

Pipeline: decode (pillow-heif for HEIC/HEIF, Pillow otherwise) → resize long edge
to ≤2000px (thumbnail, preserves aspect) → save JPEG quality 85. If Pillow /
pillow-heif are missing, falls back to ImageMagick (`magick`/`convert`) when
installed; otherwise prints install hints and exits 1.

Usage:
    python3 scripts/convert_images.py -o work photo1.HEIC photo2.HEIC ...
    python3 scripts/convert_images.py -o work *.jpg          # already-JPG: resize only
"""
import os
import shutil
import subprocess
import sys

MAX_EDGE = 2000
QUALITY = 85


def pillow_route(src, dst):
    from PIL import Image
    low = src.lower()
    if low.endswith((".heic", ".heif", ".hif")):
        try:
            from pillow_heif import register_heif_opener
        except ImportError:
            return "no-pillow-heif"
        register_heif_opener()
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE))  # never upscales, keeps aspect
        im.save(dst, "JPEG", quality=QUALITY)
    return "ok"


def magick_route(src, dst):
    exe = shutil.which("magick") or shutil.which("convert")
    if not exe:
        return "no-magick"
    cmd = [exe, src]
    if exe.endswith("magick"):
        cmd.append("convert")
    cmd += ["-resize", f"{MAX_EDGE}x{MAX_EDGE}>", "-quality", str(QUALITY), dst]
    subprocess.run(cmd, check=True, capture_output=True)
    return "ok"


def main():
    args = sys.argv[1:]
    outdir = "work"
    files = []
    it = iter(args)
    for a in it:
        if a in ("-o", "--outdir"):
            outdir = next(it, "work")
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            files.append(a)
    if not files:
        print(__doc__)
        return 1

    os.makedirs(outdir, exist_ok=True)
    ok_count, skipped = 0, 0
    for src in files:
        if not os.path.exists(src):
            print(f"  skip (not found): {src}")
            skipped += 1
            continue
        stem = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(outdir, stem + ".jpg")
        try:
            res = pillow_route(src, dst)
            if res == "no-pillow-heif" and src.lower().endswith((".heic", ".heif", ".hif")):
                res = magick_route(src, dst)
                if res == "no-magick":
                    print(f"  FAIL {src}: HEIC needs pillow-heif or ImageMagick.\n"
                          f"        pip install pillow pillow-heif   (prebuilt wheels: Win/mac/Linux)")
                    skipped += 1
                    continue
            elif res not in ("ok",):
                print(f"  FAIL {src}: {res}")
                skipped += 1
                continue
            print(f"  ok: {src} -> {dst} ({os.path.getsize(dst)//1024} KB)")
            ok_count += 1
        except Exception as e:
            print(f"  FAIL {src}: {e}")
            skipped += 1
    print(f"done: {ok_count} converted, {skipped} skipped/failed -> {outdir}/")
    return 0 if ok_count else 1


if __name__ == "__main__":
    sys.exit(main())
