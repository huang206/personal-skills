#!/usr/bin/env python3
"""check_pdf.py — QA gate for homework-error-review booklets.

Checks:
  1. Page count + per-page fill ratio (bottom-most non-white pixel; pages should
     be 40–100% — spill/overflow pages show up as <40%).
  2. Blank-page detection.
  3. Text-extraction sanity (a raster-only PDF means a screenshot pipeline ran).
  4. FONT GATE (anti-garble): CJK text must be embedded as a composite font
     (Type0/CID, Identity-H). A simple font (e.g. TrueType + WinAnsi) carrying CJK
     renders as garbage in Adobe/WPS even though lenient viewers look fine. This
     exact failure shipped once; the gate exists so it never ships again.
  5. Optional: --pngs DIR exports page previews for a visual pass.

Usage:  python3 check_pdf.py booklet.pdf [--pngs previews/]
Exit 0 = pass (warnings allowed), 1 = hard fail, 2 = degraded (pymupdf missing).
"""
import os
import re
import sys

FILL_MIN = 0.40
CJK_RE = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')


def main():
    args = sys.argv[1:]
    pngs_dir = None
    if '--pngs' in args:
        i = args.index('--pngs')
        pngs_dir = args[i + 1] if i + 1 < len(args) else 'previews'
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(1)
    pdf = args[0]
    if not os.path.exists(pdf):
        print(f'FAIL: file not found: {pdf}')
        sys.exit(1)

    try:
        import pymupdf  # modern name
    except ImportError:
        try:
            import fitz as pymupdf  # legacy name
        except ImportError:
            size = os.path.getsize(pdf)
            print(f'DEGRADED: pymupdf not installed (pip install pymupdf) — only size check possible.')
            print(f'  size: {size/1024:.1f} KB — {"looks non-empty" if size > 1024 else "SUSPICIOUSLY SMALL"}')
            sys.exit(2)

    doc = pymupdf.open(pdf)
    n = len(doc)
    print(f'file: {pdf}  pages: {n}  size: {os.path.getsize(pdf)/1024:.1f} KB')

    hard_fail = False
    fills = []
    for i, page in enumerate(doc):
        # fill ratio via pixel scan (54 dpi is enough to find content bounds)
        pix = page.get_pixmap(dpi=54)
        w, h, nch, samples = pix.width, pix.height, pix.n, pix.samples
        stride = w * nch
        last_row = 0
        for y in range(h - 1, -1, -1):
            row = samples[y * stride:(y + 1) * stride]
            if any(row[x] < 245 for x in range(0, len(row), nch * 4)):
                last_row = y
                break
        fill = last_row / h
        fills.append(fill)
        flag = '' if fill >= FILL_MIN else ('  <-- LOW FILL (spill or overstuffed section?)'
                                            if fill < 0.15 or fill >= FILL_MIN - 0.06 else '  <-- below target')
        print(f'  page {i+1}: fill {fill*100:.0f}%{flag}')
        if pngs_dir:
            os.makedirs(pngs_dir, exist_ok=True)
            hi = page.get_pixmap(dpi=100)
            hi.save(os.path.join(pngs_dir, f'page_{i+1:02d}.png'))

    low_pages = [i + 1 for i, f in enumerate(fills) if f < FILL_MIN]
    if low_pages:
        print(f'FILL: pages below {FILL_MIN*100:.0f}%: {low_pages} — move/split .page boundaries and re-render')

    # text sanity
    total_chars = sum(len(page.get_text().strip()) for page in doc)
    if total_chars < 30:
        print('TEXT FAIL: almost no extractable text — PDF is raster-only (screenshot pipeline?). Re-render with the bundled scripts.')
        hard_fail = True
    else:
        print(f'TEXT: extractable characters ≈ {total_chars} (vector text OK)')

    # font gate
    bad_fonts = []
    seen = set()
    for i, page in enumerate(doc):
        text = page.get_text()
        has_cjk = bool(CJK_RE.search(text))
        for f in page.get_fonts(full=True):
            xref, ext, ftype, basefont, name, encoding = f[0], f[1], f[2], f[3], f[4], f[5]
            key = (basefont, ftype, encoding)
            if key in seen:
                continue
            seen.add(key)
            embedded = ext != 'n/a'
            composite = ftype.startswith('Type0') or 'CID' in ftype or encoding in ('Identity-H', 'Identity-V')
            simple_cjk = has_cjk and not composite
            if simple_cjk or (has_cjk and not embedded):
                bad_fonts.append((i + 1, basefont or name, ftype, encoding, embedded))
    if bad_fonts:
        print('FONT FAIL: CJK content carried by non-composite / non-embedded fonts:')
        for pg, bf, ft, enc, emb in bad_fonts:
            print(f'  page {pg}: {bf} type={ft} encoding={enc} embedded={emb}')
        print('  -> This PDF will show garbled CJK in strict viewers (Adobe/WPS).')
        print('     Fix: run scripts/setup_env.py (downloads Noto Sans SC), then rebuild with make_pdf.py.')
        hard_fail = True
    else:
        print('FONTS: composite/CID embedding for CJK OK (no garble risk)')

    if hard_fail:
        print('RESULT: FAIL')
        sys.exit(1)
    print('RESULT: PASS' + (' (with fill warnings above)' if low_pages else ''))
    sys.exit(0)


if __name__ == '__main__':
    main()
