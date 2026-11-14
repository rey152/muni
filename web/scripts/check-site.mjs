// Checks the built site in real Chrome: every page type at 390px and 1280px in light and
// dark, sideways scrolling at 320px and 768px too, console errors, axe-core, and the main
// flows (number search, Show without AI, window dates, Ward Match privacy and offline map,
// Exposure Preview, no-JavaScript use).
// Run after `npm run build`:  node scripts/check-site.mjs
import { createServer } from 'node:http';
import { readFile, mkdir, stat } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { booleanPointInPolygon } from '@turf/boolean-point-in-polygon';

const require = createRequire(import.meta.url);
const webDir = fileURLToPath(new URL('..', import.meta.url));
const distDir = join(webDir, 'dist');
const screenDir = join(webDir, 'test-screens');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.geojson': 'application/geo+json', '.svg': 'image/svg+xml',
  '.csv': 'text/csv; charset=utf-8', '.png': 'image/png',
};

async function serveFile(path, res, status = 200) {
  const body = await readFile(path);
  res.writeHead(status, { 'Content-Type': TYPES[extname(path)] ?? 'application/octet-stream' });
  res.end(body);
}

function startServer() {
  const server = createServer(async (req, res) => {
    const urlPath = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    let filePath = normalize(join(distDir, urlPath));
    if (!filePath.startsWith(distDir)) {
      res.writeHead(403).end();
      return;
    }
    try {
      if ((await stat(filePath)).isDirectory()) filePath = join(filePath, 'index.html');
      await serveFile(filePath, res);
    } catch {
      await serveFile(join(distDir, '404.html'), res, 404);
    }
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

const PAGES = [
  ['home', '/'],
  ['topics', '/topics/'],
  ['topic', '/topic/taxes-fees-and-city-spending/'],
  ['topic-empty', '/topic/parks-recreation-and-public-spaces/'],
  ['q-decided', '/questions/decided/'],
  ['q-have-a-say', '/questions/have-a-say/'],
  ['q-undecided', '/questions/undecided/'],
  ['matter-fees', '/matter/fees-2026/'],
  ['matter-debt', '/matter/debt-limit-2026/'],
  ['matter-131-william', '/matter/heritage-131-william/'],
  ['matter-15-king', '/matter/heritage-15-king/'],
  ['easy-read', '/matter/fees-2026/easy-read/'],
  ['near-me', '/near-me/'],
  ['search', '/search/?q=heritage'],
  ['comment', '/comment/'],
  ['staff', '/staff/'],
  ['about', '/about/'],
  ['sources', '/sources/'],
  ['not-found', '/no-such-page/'],
];

const failures = [];
const notes = [];
function check(ok, message) {
  if (!ok) failures.push(message);
  return ok;
}

function watchConsole(page, label) {
  const errors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(`${label}: console error: ${msg.text()}`);
  });
  page.on('pageerror', (err) => errors.push(`${label}: page error: ${err.message}`));
  return errors;
}

async function checkPageTypes(browser, base) {
  for (const width of [390, 1280]) {
    for (const scheme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, colorScheme: scheme });
      for (const [name, path] of PAGES) {
        const page = await context.newPage();
        const errors = watchConsole(page, `${name} ${width} ${scheme}`);
        // MapLibre's worker keeps the near-me page from ever going network-idle, so wait on load there.
        const response = await page.goto(base + path, { waitUntil: name === 'near-me' ? 'load' : 'networkidle' });
        if (name === 'not-found') check(response.status() === 404, `${name}: expected HTTP 404, got ${response.status()}`);
        else check(response.ok(), `${name}: HTTP ${response.status()}`);
        if (name === 'near-me') await page.waitForTimeout(2500);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        check(overflow <= 0, `${name} ${width} ${scheme}: page scrolls sideways by ${overflow}px`);
        await page.screenshot({ path: join(screenDir, `${name}-${width}-${scheme}.png`), fullPage: true });
        // The 404 response itself is logged by Chrome as a console error; that one is expected.
        const real = errors.filter((e) => !(name === 'not-found' && e.includes('404')));
        failures.push(...real);
        await page.close();
      }
      await context.close();
    }
  }
}

// 320 is the narrowest reflow width; 768 is a tablet, where the left rail first meets
// a narrow content column.
async function checkNarrowReflow(browser, base) {
  for (const [width, height] of [[320, 640], [768, 1024]]) {
    const context = await browser.newContext({ viewport: { width, height } });
    const page = await context.newPage();
    for (const [name, path] of PAGES) {
      await page.goto(base + path, { waitUntil: name === 'near-me' ? 'load' : 'networkidle' });
      if (name === 'near-me') await page.waitForTimeout(2000);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      check(overflow <= 0, `${name} ${width}: page scrolls sideways by ${overflow}px`);
    }
    await page.goto(base + '/matter/fees-2026/', { waitUntil: 'networkidle' });
    await page.screenshot({ path: join(screenDir, `matter-fees-${width}-light.png`), fullPage: false });
    await context.close();
  }
}

async function checkAxe(browser, base) {
  const axePath = require.resolve('axe-core/axe.min.js');
  for (const scheme of ['light', 'dark']) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, colorScheme: scheme });
    const page = await context.newPage();
    for (const [name, path] of PAGES) {
      await page.goto(base + path, { waitUntil: name === 'near-me' ? 'load' : 'networkidle' });
      if (name === 'near-me') await page.waitForTimeout(2000);
      await page.addScriptTag({ path: axePath });
      const result = await page.evaluate(async () => {
        // Open every source box so axe checks what's inside them too.
        for (const d of document.querySelectorAll('details')) d.open = true;
        // eslint-disable-next-line no-undef
        const r = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] });
        return r.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.length} node(s): ${v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(' | ')}`);
      });
      for (const v of result) failures.push(`axe ${name} ${scheme}: ${v}`);
    }
    await context.close();
  }
}

async function checkSearchFlow(browser, base) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = watchConsole(page, 'search flow');

  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await page.fill('#home-q', 'By-law 2025-086');
  await page.press('#home-q', 'Enter');
  await page.waitForURL('**/matter/fees-2026/', { timeout: 10000 });
  check(new URL(page.url()).pathname === '/matter/fees-2026/', `home search for By-law 2025-086 landed on ${page.url()}`);
  notes.push(`Home search "By-law 2025-086" + Enter landed on ${new URL(page.url()).pathname}`);

  for (const [query, expected] of [
    ['bylaw 2025 086', '/matter/fees-2026/'],
    ['BYLAW2025087', '/matter/fees-2026/'],
    ['COM2025-034', '/matter/fees-2026/'],
    ['By-law 2026-080', '/matter/heritage-15-king/'],
    ['131 William St W', '/matter/heritage-131-william/'],
    ['CORP2024-046', '/matter/debt-limit-2026/'],
  ]) {
    await page.goto(base + '/search/?q=' + encodeURIComponent(query));
    await page.waitForURL('**' + expected, { timeout: 10000 }).catch(() => {});
    check(new URL(page.url()).pathname === expected, `search "${query}" landed on ${page.url()}, expected ${expected}`);
  }

  await page.goto(base + '/search/?q=' + encodeURIComponent('By-law 2099-001'), { waitUntil: 'networkidle' });
  const unknown = await page.textContent('#results');
  check(unknown.includes('No match'), `unknown by-law number should say No match, got: ${unknown}`);

  await page.goto(base + '/search/?q=heritage', { waitUntil: 'networkidle' });
  const heritageRows = await page.locator('#results .lrow').count();
  check(heritageRows === 2, `search "heritage" should find 2 matters, found ${heritageRows}`);

  await page.goto(base + '/search/?q=' + encodeURIComponent('zzzz nothing'), { waitUntil: 'networkidle' });
  check((await page.textContent('#results')).includes('No match'), 'nonsense search should say No match');
  failures.push(...errors);
  await context.close();
}

async function checkMatterPage(browser, base) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  await page.goto(base + '/matter/fees-2026/', { waitUntil: 'networkidle' });

  const headings = await page.locator('.facts > section > h2').allTextContents();
  const expected = ['Applies to', 'What it would do and why', 'Who decides', 'Conditions', 'Not decided yet', 'How to have a say', 'Records'];
  check(JSON.stringify(headings) === JSON.stringify(expected), `matter headings out of order: ${headings.join(' | ')}`);

  const aiText = page.locator('#claim-C-f2 .ai-only');
  const fallback = page.locator('#claim-C-f2 .noai-only');
  check(await aiText.isVisible(), 'AI paraphrase should be visible by default');
  check(!(await fallback.isVisible()), 'fallback should be hidden by default');
  await page.check('#no-ai');
  check(!(await aiText.isVisible()), 'Show without AI should hide the AI paraphrase');
  check(await fallback.isVisible(), 'Show without AI should show the fallback wording');
  await page.uncheck('#no-ai');

  const source = page.locator('#claim-C-f1 details.src').first();
  await source.locator('summary').click();
  check((await source.textContent()).includes('Research note'), 'source box should label a research note as such');

  // The heritage objection date was November 6, 2026. Pretend today is November 1: it should read Open.
  const early = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const earlyPage = await early.newPage();
  await earlyPage.clock.setFixedTime(new Date('2026-11-01T12:00:00'));
  await earlyPage.goto(base + '/matter/heritage-131-william/', { waitUntil: 'networkidle' });
  const earlyTag = await earlyPage.locator('.window [data-window-tag]').first().textContent();
  check(earlyTag === 'Open', `window on Nov 1 should be Open, got ${earlyTag}`);
  await earlyPage.clock.setFixedTime(new Date('2026-11-06T23:00:00'));
  await earlyPage.reload({ waitUntil: 'networkidle' });
  check((await earlyPage.locator('.window [data-window-tag]').first().textContent()) === 'Open', 'the quoted day itself should still count as open');
  await earlyPage.clock.setFixedTime(new Date('2026-11-07T08:00:00'));
  await earlyPage.reload({ waitUntil: 'networkidle' });
  check((await earlyPage.locator('.window [data-window-tag]').first().textContent()) === 'Closed', 'the day after should be Closed');
  await early.close();

  const fees = await page.locator('.window [data-window-tag]').first().textContent();
  check(fees === 'General rule', `a rule-based window should stay "General rule", got ${fees}`);
  await context.close();
}

async function checkNoJavaScript(browser, base) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(base + '/matter/heritage-15-king/');
  check((await page.locator('.facts > section > h2').count()) === 7, 'no-JS matter page should have seven sections');
  const tag = await page.locator('.window [data-window-tag]').first().textContent();
  const when = await page.locator('[data-window-when]').first().textContent();
  check(tag === 'Closed' && when.includes('when this page was built'), `no-JS window should show the build-time state, got ${tag} / ${when}`);
  await page.check('#no-ai');
  check(!(await page.locator('#claim-C-k2 .ai-only').isVisible()), 'Show without AI should work without JavaScript');
  await page.screenshot({ path: join(screenDir, 'nojs-matter-390.png'), fullPage: false });

  await page.goto(base + '/near-me/#ward-7');
  check(await page.locator('#ward-7').isVisible(), 'no-JS ward list should show Ward 7 through #ward-7');
  check(!(await page.locator('#ward-2').isVisible()), 'no-JS should show only the chosen ward');
  await page.screenshot({ path: join(screenDir, 'nojs-near-me-390.png'), fullPage: true });

  await page.goto(base + '/search/');
  check(await page.locator('table').isVisible(), 'no-JS search should still list every number');
  await context.close();
}

async function checkNearMe(browser, base) {
  const wards = JSON.parse(await readFile(join(distDir, 'data', 'wards.geojson'), 'utf8')).features;
  const point = [-80.5225, 43.4668]; // Uptown Waterloo
  const expectedWard = wards.find((w) => booleanPointInPolygon(point, w))?.properties.WARD_NO;
  notes.push(`Test point ${point.join(', ')} is in Ward ${expectedWard} by Turf in Node`);

  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.grantPermissions(['geolocation']);
  await context.setGeolocation({ longitude: point[0], latitude: point[1] });
  const page = await context.newPage();
  const errors = watchConsole(page, 'near-me flow');
  const requests = [];
  page.on('request', (request) => requests.push(request.url() + ' ' + (request.postData() ?? '')));
  await page.goto(base + '/near-me/', { waitUntil: 'load' });
  await page.waitForTimeout(4000);

  const mapWorks = await page.locator('#ward-map canvas').count();
  notes.push(`Map canvas present: ${mapWorks > 0}; map status: "${await page.textContent('#map-status')}"`);

  const before = requests.length;
  await page.click('#geo-btn');
  await page.waitForFunction(() => document.getElementById('geo-status').textContent.includes('Ward') || document.getElementById('geo-status').textContent.includes('outside'));
  const geoText = await page.textContent('#geo-status');
  check(geoText.includes(`Ward ${expectedWard}`), `geolocation should find Ward ${expectedWard}, got "${geoText}"`);
  check(await page.locator(`#ward-${expectedWard}`).isVisible(), 'the geolocated ward block should be visible');

  // Tap the middle of the map. Whatever ward that is, the status must name one, and no request may carry the point.
  const box = await page.locator('#ward-map').boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForTimeout(1500);
  const tapText = await page.textContent('#map-status');
  check(/Ward \d|outside/.test(tapText), `map tap should report a ward, got "${tapText}"`);
  notes.push(`Map tap at the map centre: "${tapText}"`);

  await page.click('.ward-list a[data-ward="3"]');
  check(await page.locator('#ward-3').isVisible(), 'list pick should show Ward 3');
  check(!(await page.locator(`#ward-${expectedWard}`).isVisible()) || expectedWard === 3, 'only one ward block should show');
  const stored = await page.evaluate(() => localStorage.getItem('muni-ward'));
  check(stored === null, `ward must not be stored without consent, found ${stored}`);
  await page.check('#remember');
  const storedAfter = await page.evaluate(() => localStorage.getItem('muni-ward'));
  check(storedAfter === '3', `ward should be stored after consent, found ${storedAfter}`);
  await page.uncheck('#remember');
  check((await page.evaluate(() => localStorage.getItem('muni-ward'))) === null, 'unticking should forget the ward');

  const after = requests.slice(before);
  const coordsPattern = /-?80\.5[0-9]{2}|43\.4[0-9]{2}/;
  const leaking = after.filter((r) => coordsPattern.test(r) && !r.includes('tiles.openfreemap.org'));
  check(leaking.length === 0, `requests after locating carried coordinates: ${leaking.join('\n')}`);
  const hosts = [...new Set(requests.map((r) => new URL(r.split(' ')[0]).host))];
  notes.push(`Near me page contacted: ${hosts.join(', ')}`);
  check(!requests.some((r) => r.includes('tile.openstreetmap.org')), 'must never use tile.openstreetmap.org');
  const tileRequestsAfter = after.filter((r) => r.includes('openfreemap')).length;
  notes.push(`OpenFreeMap requests after locating and tapping (should be none, the map isn't moved): ${tileRequestsAfter}`);
  check(tileRequestsAfter === 0, `locating or tapping made ${tileRequestsAfter} map tile requests`);
  failures.push(...errors);
  await page.screenshot({ path: join(screenDir, 'near-me-flow-1280.png'), fullPage: false });
  await context.close();
}

// With no internet the background map can't load. The page should say so, fall back to a
// plain background with the ward outlines, and a tap should still find a ward.
async function checkNearMeOffline(browser, base) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await context.route((url) => !url.href.startsWith(base), (route) => route.abort('internetdisconnected'));
  const page = await context.newPage();
  const errors = watchConsole(page, 'near-me offline');
  await page.goto(base + '/near-me/', { waitUntil: 'load' });
  await page.waitForTimeout(3000);
  const status = await page.textContent('#map-status');
  notes.push(`Near me offline: map status "${status}"`);
  check(status.includes("background map didn't load"), `offline map should explain the missing background, got "${status}"`);
  check((await page.locator('#ward-map canvas').count()) > 0, 'offline map should still draw the ward outlines');
  const box = await page.locator('#ward-map').boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForTimeout(800);
  const tapText = await page.textContent('#map-status');
  check(/Ward \d|outside/.test(tapText), `offline map tap should report a ward, got "${tapText}"`);
  // Fonts and tiles failing to load are expected offline; anything else is a real error.
  failures.push(...errors.filter((e) => !e.includes('net::ERR_INTERNET_DISCONNECTED')));
  await page.screenshot({ path: join(screenDir, 'near-me-offline-390.png'), fullPage: false });
  await context.close();
}

async function checkComment(browser, base) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const errors = watchConsole(page, 'comment flow');
  await page.goto(base + '/comment/', { waitUntil: 'networkidle' });
  const requests = [];
  page.on('request', (request) => requests.push(request.url()));
  const draft = 'My name is Jane Doe and I live at 123 King St N, Waterloo ON N2J 2Y3. Call 519-555-0142 or email jane.doe@example.com about the heritage plan.';
  await page.fill('#draft', draft);
  await page.waitForTimeout(500);
  const kinds = await page.locator('#exposure-preview mark').evaluateAll((marks) => marks.map((m) => `${m.dataset.kind}=${m.textContent}`));
  notes.push(`Exposure Preview marked: ${kinds.join(' | ')}`);
  for (const kind of ['name', 'street address', 'postal code', 'phone number', 'email']) {
    check(kinds.some((k) => k.startsWith(kind + '=')), `Exposure Preview should mark a ${kind}`);
  }
  check(requests.length === 0, `typing a draft made requests: ${requests.join(', ')}`);
  check((await page.evaluate(() => localStorage.getItem('muni-comment-draft'))) === null, 'draft must not be stored until saved');
  await page.click('#save-draft');
  check((await page.evaluate(() => localStorage.getItem('muni-comment-draft'))) === draft, 'saving should store the draft locally');
  await page.click('#forget-draft');
  check((await page.evaluate(() => localStorage.getItem('muni-comment-draft'))) === null, 'deleting should remove the saved draft');
  check(requests.length === 0, `saving or deleting made requests: ${requests.join(', ')}`);
  await page.screenshot({ path: join(screenDir, 'comment-flow-390.png'), fullPage: true });
  failures.push(...errors);
  await context.close();
}

async function checkThemeButton(browser, base) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, colorScheme: 'light' });
  const page = await context.newPage();
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await page.click('#theme-btn');
  const theme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  check(theme === 'dark', `theme button should switch to dark, got ${theme}`);
  await page.goto(base + '/about/', { waitUntil: 'networkidle' });
  check((await page.evaluate(() => document.documentElement.getAttribute('data-theme'))) === 'dark', 'chosen theme should carry to the next page');
  await context.close();
}

const server = await startServer();
const base = `http://127.0.0.1:${server.address().port}`;
await mkdir(screenDir, { recursive: true });
const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--enable-unsafe-swiftshader'] });
try {
  await checkSearchFlow(browser, base);
  await checkMatterPage(browser, base);
  await checkNoJavaScript(browser, base);
  await checkNearMe(browser, base);
  await checkNearMeOffline(browser, base);
  await checkComment(browser, base);
  await checkThemeButton(browser, base);
  await checkPageTypes(browser, base);
  await checkNarrowReflow(browser, base);
  await checkAxe(browser, base);
} finally {
  await browser.close();
  server.close();
}

for (const note of notes) console.log('note:', note);
if (failures.length) {
  console.log(`\n${failures.length} problem(s):`);
  for (const f of failures) console.log(' -', f);
  process.exit(1);
}
console.log(`\nAll checks passed. Screenshots in ${screenDir}`);
