#!/usr/bin/env node
/**
 * render_pdf.js — minimal HTML → PDF renderer (primary path)
 *
 * Usage:  node render_pdf.js input.html [--output out.pdf] [--title "Book Title"]
 *
 * Design goals: portability over features. Only dependency: the `playwright` npm
 * package + a Chromium it can find. Resolution chain (first hit wins):
 *   playwright module : require('playwright') → $PLAYWRIGHT_PATH → npm root -g
 *   chromium binary   : playwright's bundled → $PLAYWRIGHT_CHROMIUM_PATH
 *                       → /usr/bin/google-chrome{,-stable} → chromium{,-browser}
 * PDF settings match the skill template: printBackground on, CSS page size
 * honored (@page A4 / margin 0 in template), tagged PDF.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const url = require('url');
const { execSync } = require('child_process');

function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--output' || t === '-o') a.output = argv[++i];
    else if (t === '--title') a.title = argv[++i];
    else if (t === '--help' || t === '-h') a.help = true;
    else a._.push(t);
  }
  return a;
}

function loadPlaywright() {
  // 1) plain require (cwd node_modules walk-up)
  try { return require('playwright'); } catch (e) { /* keep trying */ }
  // 2) explicit path
  if (process.env.PLAYWRIGHT_PATH) {
    try { return require(process.env.PLAYWRIGHT_PATH); } catch (e) { /* next */ }
  }
  // 3) global npm root
  try {
    const root = execSync('npm root -g', { encoding: 'utf8' }).trim();
    const req = require('module').createRequire(path.join(root, 'x.js'));
    return req('playwright');
  } catch (e) { /* next */ }
  // 4) NODE_PATH entries
  if (process.env.NODE_PATH) {
    for (const p of process.env.NODE_PATH.split(path.delimiter)) {
      try { return require(path.join(p, 'playwright')); } catch (e) { /* keep trying */ }
    }
  }
  return null;
}

function resolveChromium(pw) {
  try { const p = pw.chromium.executablePath(); if (p && fs.existsSync(p)) return p; } catch (e) {}
  if (process.env.PLAYWRIGHT_CHROMIUM_PATH && fs.existsSync(process.env.PLAYWRIGHT_CHROMIUM_PATH))
    return process.env.PLAYWRIGHT_CHROMIUM_PATH;
  const candidates = [
    // Linux
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/opt/google/chrome/chrome', '/opt/microsoft/msedge/msedge',
    // macOS
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
  ];
  if (process.platform === 'win32') {
    const expand = p => path.join(...p.split('\\').map(seg => seg.match(/%.+%/)
      ? (process.env[seg.slice(1, -1)] || seg) : seg));
    candidates.length = 0;
    candidates.push(
      expand('%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe'),
      expand('%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe'),
      expand('%PROGRAMFILES(X86)%\\Google\\Chrome\\Application\\chrome.exe'),
      expand('%PROGRAMFILES(X86)%\\Microsoft\\Edge\\Application\\msedge.exe'),
      expand('%PROGRAMFILES%\\Microsoft\\Edge\\Application\\msedge.exe'));
  }
  for (const c of candidates) if (c && fs.existsSync(c)) return c;
  return null;
}

(async () => {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args._.length === 0) {
    console.log('Usage: node render_pdf.js input.html [--output out.pdf] [--title "Title"]');
    process.exit(args.help ? 0 : 1);
  }
  const input = path.resolve(args._[0]);
  if (!fs.existsSync(input)) { console.error('Input not found: ' + input); process.exit(1); }
  const output = path.resolve(args.output || input.replace(/\.html?$/i, '') + '.pdf');
  const htmlTitle = args.title || (function () {
    try { const m = fs.readFileSync(input, 'utf8').match(/<title>([^<]*)<\/title>/i); return m ? m[1].trim() : ''; }
    catch (e) { return ''; }
  })();

  const pw = loadPlaywright();
  if (!pw) {
    console.error('[render_pdf] playwright not found. Install it (npm i -g playwright; npx playwright install chromium),\n' +
                  '               or use the fallback:  bash render_chrome.sh input.html output.pdf');
    process.exit(2);
  }
  const exe = resolveChromium(pw);
  if (!exe) {
    console.error('[render_pdf] no Chromium found. Run: npx playwright install chromium\n' +
                  '               (or set PLAYWRIGHT_CHROMIUM_PATH, or use render_chrome.sh with a system Chrome)');
    process.exit(2);
  }

  const browser = await pw.chromium.launch({ headless: true, executablePath: exe,
    args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  try {
    const page = await browser.newPage();
    // pathToFileURL: correct file URL on every platform ('file:///C:/...' on Windows;
    // plain string concat produces the malformed 'file://C:\...' there)
    await page.goto(url.pathToFileURL(input).href, { waitUntil: 'networkidle', timeout: 60000 });
    // Wait for webfonts (system fonts resolve instantly; harmless if none)
    await page.evaluate(() => document.fonts ? document.fonts.ready : Promise.resolve());
    await page.waitForTimeout(150); // settle layout

    await page.pdf({
      path: output,
      printBackground: true,
      preferCSSPageSize: true,   // template's @page { size: A4; margin: 0 }
      tagged: true,
      displayHeaderFooter: false,
    });
    const kb = (fs.statSync(output).size / 1024).toFixed(1);
    console.log('[render_pdf] wrote ' + output + ' (' + kb + ' KB)' + (htmlTitle ? ' — ' + htmlTitle : ''));
  } finally {
    await browser.close();
  }
})().catch(e => { console.error('[render_pdf] ' + (e && e.message ? e.message : e)); process.exit(1); });
