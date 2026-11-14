/* Muni: static, hash-routed. No network calls except loading data/ files. */
(function () {
  'use strict';
  var D = null, WARDS = null, state = { noAI: false, easy: false, ward: null };
  var main = document.getElementById('main');

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s || '').toLowerCase().replace(/by-?law/g, 'bylaw').replace(/[\s\-_.]/g, ''); }
  function byId(list, id) { return (list || []).filter(function (x) { return x.id === id; })[0]; }
  function passage(id) { return byId(D.passages, id); }
  function snapshot(id) { return byId(D.snapshots, id); }
  function matter(id) { return byId(D.matters, id); }
  function asOf() { return D.checked_on || 'unknown date'; }
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} }

  /* Theme */
  var themeBtn = document.getElementById('theme-btn');
  function applyTheme(t) {
    if (t) document.documentElement.setAttribute('data-theme', t); else document.documentElement.removeAttribute('data-theme');
    var dark = t ? t === 'dark' : (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    var lbl = dark ? 'Light theme' : 'Dark theme';
    themeBtn.innerHTML = dark ? '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>' : '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" fill="currentColor"/></svg>';
    themeBtn.setAttribute('aria-label', lbl); themeBtn.title = lbl;
    themeBtn.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }
  applyTheme(lsGet('muni-theme'));
  themeBtn.addEventListener('click', function () {
    var cur = document.documentElement.getAttribute('data-theme') || ((window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light');
    var next = cur === 'dark' ? 'light' : 'dark'; lsSet('muni-theme', next); applyTheme(next);
  });

  /* Labels */
  var PROV = { quote: 'Quote', extraction: 'Extracted', extracted: 'Extracted', ai_paraphrase: 'AI paraphrase', human: 'Written by a person' };
  var SECTIONS = [['applies_to', 'Applies to'], ['what_and_why', 'What it would do and why'], ['who_decides', 'Who decides'], ['conditions', 'Conditions'], ['not_decided', 'Not decided yet'], ['have_a_say', 'How to have a say'], ['records', 'Records']];
  var KIND = { proposed: 'Proposed', staff_recommendation: 'Staff recommendation', council_decision: 'Council decision', in_force: 'In force', appeal_window: 'Appeal window', repealed: 'Repealed', done: 'Done' };
  function statusOf(m) {
    var k = (m.events || []).slice().sort(function (a, b) { return String(a.date).localeCompare(String(b.date)); }).map(function (e) { return e.kind; });
    var last = k[k.length - 1];
    if (k.indexOf('repealed') >= 0) return ['Repealed or replaced', 'st--muted'];
    if (last === 'appeal_window') return ['Waiting on appeal window', 'st--wait'];
    if (k.indexOf('in_force') >= 0 || k.indexOf('done') >= 0) return ['In force', 'st--ok'];
    if (k.indexOf('council_decision') >= 0) return ['Decided', 'st--ok'];
    if (k.indexOf('staff_recommendation') >= 0) return ['Recommended', 'st--wait'];
    if (k.length) return ['Proposed', 'st--wait'];
    return ['No status record', 'st--muted'];
  }
  function statusChip(m) { var s = statusOf(m); return '<span class="status ' + s[1] + '">' + esc(s[0]) + '</span>'; }
  function matterCard(m) {
    return '<li><a class="mcard" href="#/matter/' + encodeURIComponent(m.id) + '"><span class="mu-overline">' + esc((m.topics || [])[0] || 'Council matter') + '</span>' +
      '<span class="mcard__title">' + esc(m.title) + '</span><span class="mcard__foot">' + statusChip(m) + '<span class="mu-meta">' + esc(m.location || '') + '</span></span></a></li>';
  }
  var HERO_ART = '<svg class="hero-art" viewBox="0 0 320 200" aria-hidden="true"><rect class="mu-art-ground" width="320" height="200" fill="#e5d3b3"/><circle cx="246" cy="58" r="30" fill="#d97757"/>' +
    '<rect x="34" y="62" width="44" height="122" fill="#1aa7e0"/><rect x="42" y="74" width="28" height="6" fill="#faf9f5"/><rect x="42" y="90" width="28" height="6" fill="#faf9f5"/><rect x="42" y="106" width="28" height="6" fill="#faf9f5"/>' +
    '<rect class="mu-art-deep" x="88" y="96" width="60" height="88" fill="#2d5a9e"/><path d="M84 96 L118 66 L152 96 Z" fill="#2d5a9e" class="mu-art-deep"/><rect x="110" y="146" width="16" height="38" fill="#f2b950"/>' +
    '<path d="M162 184 V122 L194 98 L226 122 V184 Z" fill="#66cdc8"/><rect x="186" y="150" width="16" height="34" fill="#faf9f5"/>' +
    '<circle cx="262" cy="148" r="22" fill="#7cc142"/><rect x="259" y="160" width="6" height="24" fill="#0b7a3d"/>' +
    '<path class="mu-art-line" d="M10 186 C 70 178, 120 192, 170 184 S 270 178, 312 188" fill="none" stroke="#1f2733" stroke-width="3" stroke-linecap="round"/></svg>';
  function chip(p) { return '<span class="chip' + (p === 'ai_paraphrase' ? ' chip--ai' : '') + '">' + esc(PROV[p] || p) + '</span>'; }

  function sourceDetails(pid, label) {
    var p = passage(pid);
    if (!p) return '<details class="src"><summary>' + esc(label || 'Source') + '</summary><p>Source passage not found in the records checked.</p></details>';
    var s = snapshot(p.snapshot_id) || {};
    var lab = p.kind === 'research_note' ? 'Research note' : 'Verbatim text';
    return '<details class="src"><summary>' + esc(label || 'Source') + '</summary>' +
      '<p><strong>' + lab + ':</strong></p><blockquote>' + esc(p.text) + '</blockquote>' +
      '<p>Where: ' + esc(p.locator || 'not stated') + '<br>Record: ' + esc(s.title || p.snapshot_id) +
      '<br>Publisher: ' + esc(s.publisher || 'not stated') + '<br>Checked on: ' + esc(s.fetched_at || asOf()) +
      (s.availability && s.availability !== 'ok' ? '<br>Availability: ' + esc(s.availability) + (s.reason ? ' (' + esc(s.reason) + ')' : '') : '') +
      (s.url ? '<br><a href="' + esc(s.url) + '" rel="noopener" target="_blank">Open the record</a>' : '') + '</p></details>';
  }

  function claimHTML(c) {
    var prov = c.provenance, text = c.text;
    if (state.noAI && prov === 'ai_paraphrase') {
      if (c.fallback) { prov = 'quote'; text = c.fallback; }
      else { var p0 = passage((c.passage_ids || [])[0]); prov = 'quote'; text = p0 ? p0.text : 'No source text available.'; }
    }
    return '<div class="claim" id="claim-' + esc(c.id) + '"><p>' + chip(prov) + esc(text) + '</p>' +
      (c.passage_ids || []).map(function (pid, i) { return sourceDetails(pid, (c.passage_ids.length > 1 ? 'Source ' + (i + 1) : 'Source')); }).join('') + '</div>';
  }

  /* Routing */
  function setNav(r) {
    document.querySelectorAll('.site-nav a').forEach(function (a) {
      if (a.getAttribute('data-route') === r) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  function route() {
    if (!D) return;
    var h = location.hash.replace(/^#\/?/, ''), parts = h.split('/');
    var r = parts[0] || 'home';
    setNav(r === 'matter' ? '' : r);
    if (r === 'matter') renderMatter(decodeURIComponent(parts.slice(1).join('/')));
    else if (r === 'comment') renderComment();
    else if (r === 'staff') renderStaff();
    else if (r === 'about') renderAbout();
    else renderHome();
    window.scrollTo(0, 0);
  }
  function focusMain(title) { document.title = title ? title + ' · Muni' : 'Muni'; main.focus({ preventScroll: true }); }

  /* Home */
  function renderHome() {
    var topics = {};
    D.matters.forEach(function (m) { (m.topics || []).forEach(function (t) { (topics[t] = topics[t] || []).push(m); }); });
    var wardOpts = (WARDS ? WARDS.features : []).map(function (f) {
      var n = f.properties.WARD_NO; return '<option value="' + esc(n) + '">' + esc(wardLabel(f)) + '</option>';
    }).join('');
    var tkeys = Object.keys(topics).sort();
    main.innerHTML =
      '<section class="hero"><div class="hero__text"><p class="mu-overline">City of Waterloo · checked ' + esc(asOf()) + '</p><h1>What\'s happening at City Hall, in plain words</h1>' +
      '<p class="hero__lede">Look up a council matter by report number, by-law, street or topic. Every sentence links to the record it came from. This is not the official notice.</p>' +
      '<form id="pp-form" class="search-row" role="search"><div class="mu-field"><label for="pp-q">Search by report number, by-law number, street or topic</label>' +
      '<div class="search-inline"><input id="pp-q" type="search" aria-describedby="pp-help" autocomplete="off" placeholder="By-law 2025-087, COM2025-034, William St">' +
      '<button class="mu-btn mu-btn--primary" type="submit">Search</button></div><span class="mu-field__help" id="pp-help">Item Passport finds a matter by any number it has had.</span></div></form>' +
      '<div id="pp-out" role="status" aria-live="polite"></div></div>' + HERO_ART + '</section>' +
      '<section aria-labelledby="tp-h"><h2 id="tp-h">Council matters</h2><div class="filters" role="group" aria-label="Filter by topic"><button type="button" class="fchip" aria-pressed="true" data-t="">All</button>' +
      tkeys.map(function (t) { return '<button type="button" class="fchip" aria-pressed="false" data-t="' + esc(t) + '">' + esc(t) + '</button>'; }).join('') + '</div>' +
      '<ul class="mgrid" id="mgrid">' + D.matters.map(matterCard).join('') + '</ul></section>' +
      '<section class="panel" aria-labelledby="wm-h"><h2 id="wm-h">Matters in your ward</h2>' +
      '<p class="mu-meta">A ward is an administrative area, not how far effects reach. Your location stays on this device; Muni sends it nowhere.</p>' +
      '<div class="grid2"><div>' +
      '<div class="mu-field"><label for="ward-sel">Choose your ward</label><select id="ward-sel"><option value="">Choose a ward</option>' + wardOpts + '</select></div>' +
      '<p><button type="button" class="mu-btn mu-btn--secondary" id="geo-btn">Use my location</button></p>' +
      '<p><label><input type="checkbox" id="remember"> Remember my ward on this device</label></p>' +
      '<div id="ward-out" role="status" aria-live="polite"></div></div>' +
      '<div>' + mapSVG() + '<p class="mu-meta">Click or tap the map to find the ward at that spot. You can also use the list.</p></div></div></section>';
    document.querySelectorAll('.fchip').forEach(function (b) {
      b.addEventListener('click', function () {
        var t = b.getAttribute('data-t');
        document.querySelectorAll('.fchip').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        document.getElementById('mgrid').innerHTML = D.matters.filter(function (m) { return !t || (m.topics || []).indexOf(t) >= 0; }).map(matterCard).join('');
      });
    });
    document.getElementById('pp-form').addEventListener('submit', function (e) { e.preventDefault(); passportSearch(document.getElementById('pp-q').value); });
    var sel = document.getElementById('ward-sel');
    sel.addEventListener('change', function () { pickWard(sel.value || null); });
    document.getElementById('geo-btn').addEventListener('click', useLocation);
    var rem = document.getElementById('remember');
    rem.checked = !!lsGet('muni-ward');
    rem.addEventListener('change', function () { lsSet('muni-ward', rem.checked && state.ward ? state.ward : null); });
    var svg = document.getElementById('wardmap');
    if (svg) svg.addEventListener('click', mapClick);
    var saved = lsGet('muni-ward');
    if (saved) pickWard(saved); else if (state.ward) pickWard(state.ward); else showWardMatters(null);
    focusMain('');
  }
  function matterLink(m) { return '<li><a href="#/matter/' + encodeURIComponent(m.id) + '">' + esc(m.title) + '</a> <span class="mu-meta">· ' + esc(m.location || '') + '</span></li>'; }

  function passportSearch(q) {
    var out = document.getElementById('pp-out'), n = norm(q);
    if (!n) { out.innerHTML = '<p>Type something to search.</p>'; return; }
    var alias = D.alias || {};
    if (!D.alias) D.matters.forEach(function (m) { (m.identifiers || []).forEach(function (i) { alias[norm(i.value)] = m.id; }); });
    if (alias[n]) { location.hash = '#/matter/' + encodeURIComponent(alias[n]); return; }
    var ql = q.trim().toLowerCase();
    var hits = D.matters.filter(function (m) {
      var hay = [m.title, m.location].concat(m.topics || [], (m.identifiers || []).map(function (i) { return i.value; })).join(' | ').toLowerCase();
      return hay.indexOf(ql) >= 0 || norm(hay).indexOf(n) >= 0;
    });
    out.innerHTML = hits.length ? '<p>' + hits.length + ' match' + (hits.length > 1 ? 'es' : '') + ':</p><ul class="result-list">' + hits.map(matterLink).join('') + '</ul>'
      : '<div class="mu-alert mu-alert--info"><span class="mu-alert__dot" aria-hidden="true"></span><div><p class="mu-alert__title">No matching matter</p><p class="mu-alert__text">Check the number, or browse the matters below.</p></div></div>';
  }

  /* Map */
  var BOX = null, W = 460, H = 400;
  function eachRing(geom, fn) {
    if (!geom) return;
    if (geom.type === 'Polygon') geom.coordinates.forEach(function (r) { fn(r); });
    else if (geom.type === 'MultiPolygon') geom.coordinates.forEach(function (p) { p.forEach(function (r) { fn(r); }); });
  }
  function bbox() {
    var b = [Infinity, Infinity, -Infinity, -Infinity];
    WARDS.features.forEach(function (f) { eachRing(f.geometry, function (r) { r.forEach(function (c) { b[0] = Math.min(b[0], c[0]); b[1] = Math.min(b[1], c[1]); b[2] = Math.max(b[2], c[0]); b[3] = Math.max(b[3], c[1]); }); }); });
    var k = Math.cos((b[1] + b[3]) / 2 * Math.PI / 180);
    var sx = (W - 20) / ((b[2] - b[0]) * k), sy = (H - 20) / (b[3] - b[1]), s = Math.min(sx, sy);
    return { b: b, k: k, s: s };
  }
  function proj(c) { return [10 + (c[0] - BOX.b[0]) * BOX.k * BOX.s, 10 + (BOX.b[3] - c[1]) * BOX.s]; }
  function unproj(x, y) { return [(x - 10) / (BOX.k * BOX.s) + BOX.b[0], BOX.b[3] - (y - 10) / BOX.s]; }
  function wardLabel(f) { var p = f.properties; return 'Ward ' + p.WARD_NO + (p.WARD_NAME ? ' – ' + p.WARD_NAME : ''); }
  function mapSVG() {
    if (!WARDS || !WARDS.features.length) return '<p class="empty">Ward map not available.</p>';
    BOX = bbox();
    var paths = WARDS.features.map(function (f) {
      var d = '', cx = 0, cy = 0, n = 0;
      eachRing(f.geometry, function (r) { d += r.map(function (c, i) { var p = proj(c); cx += p[0]; cy += p[1]; n++; return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join('') + 'Z'; });
      return '<path data-ward="' + esc(f.properties.WARD_NO) + '" d="' + d + '"><title>' + esc(wardLabel(f)) + '</title></path>' +
        '<text x="' + (cx / n).toFixed(0) + '" y="' + (cy / n).toFixed(0) + '" text-anchor="middle">' + esc(f.properties.WARD_NO) + '</text>';
    }).join('');
    return '<svg id="wardmap" class="wardmap" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Map of City of Waterloo wards. Click a spot to find its ward.">' + paths + '</svg>';
  }
  function inRing(pt, r) {
    var inside = false;
    for (var i = 0, j = r.length - 1; i < r.length; j = i++) {
      var xi = r[i][0], yi = r[i][1], xj = r[j][0], yj = r[j][1];
      if (((yi > pt[1]) !== (yj > pt[1])) && (pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }
  function inGeom(pt, g) {
    var polys = g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : [];
    return polys.some(function (p) { return inRing(pt, p[0]) && !p.slice(1).some(function (h) { return inRing(pt, h); }); });
  }
  function wardAt(lonlat) {
    var f = WARDS.features.filter(function (f) { return inGeom(lonlat, f.geometry); })[0];
    return f ? String(f.properties.WARD_NO) : null;
  }
  function mapClick(e) {
    var svg = e.currentTarget, pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    var loc = pt.matrixTransform(svg.getScreenCTM().inverse());
    var w = wardAt(unproj(loc.x, loc.y));
    if (w) pickWard(w); else document.getElementById('ward-out').innerHTML = '<p>That spot is outside the City of Waterloo wards.</p>';
  }
  function useLocation() {
    var out = document.getElementById('ward-out');
    if (!navigator.geolocation) { out.innerHTML = '<p>Location is not available in this browser. Choose your ward from the list.</p>'; return; }
    out.innerHTML = '<p>Finding your location on this device…</p>';
    navigator.geolocation.getCurrentPosition(function (pos) {
      var w = wardAt([pos.coords.longitude, pos.coords.latitude]);
      if (w) pickWard(w); else out.innerHTML = '<p>Your location is outside the City of Waterloo wards.</p>';
    }, function () { out.innerHTML = '<p>We could not get your location. Choose your ward from the list.</p>'; }, { timeout: 10000 });
  }
  function pickWard(w) {
    state.ward = w;
    var sel = document.getElementById('ward-sel'); if (sel) sel.value = w || '';
    document.querySelectorAll('#wardmap path').forEach(function (p) { p.classList.toggle('sel', p.getAttribute('data-ward') === String(w)); });
    var rem = document.getElementById('remember'); if (rem && rem.checked) lsSet('muni-ward', w);
    showWardMatters(w);
  }
  function showWardMatters(w) {
    var out = document.getElementById('ward-out'); if (!out) return;
    var f = w && WARDS ? WARDS.features.filter(function (f) { return String(f.properties.WARD_NO) === String(w); })[0] : null;
    var inWard = w ? D.matters.filter(function (m) { return (m.wards || []).map(String).indexOf(String(w)) >= 0; }) : [];
    var city = D.matters.filter(function (m) { return !(m.wards || []).length && String(m.location).toLowerCase() === 'citywide'; });
    var unmatched = D.matters.filter(function (m) { return !(m.wards || []).length && String(m.location).toLowerCase() !== 'citywide'; });
    out.innerHTML = (f ? '<p><strong>Your ward: ' + esc(wardLabel(f)) + '</strong></p>' : '<p>No ward chosen yet.</p>') +
      (w ? '<h3>Matters in this ward</h3>' + (inWard.length ? '<ul class="result-list">' + inWard.map(matterLink).join('') + '</ul>' : '<p class="empty">None matched to this ward in the records checked.</p>') : '') +
      '<h3>Citywide matters</h3><ul class="result-list">' + city.map(matterLink).join('') + '</ul>' +
      (unmatched.length ? '<h3>Ward not matched yet</h3><ul class="result-list">' + unmatched.map(function (m) { return matterLink(m).replace('</li>', ' <span class="chip">Ward not matched yet</span></li>'); }).join('') + '</ul>' : '');
  }

  /* Matter */
  function renderMatter(id) {
    var m = matter(id);
    if (!m) { main.innerHTML = '<h1>Matter not found</h1><p>No matter has that identifier in the records checked. <a href="#/">Back to search</a></p>'; focusMain('Not found'); return; }
    var claims = m.claims || [];
    var html = '<p class="crumb"><a href="#/">Matters</a> / ' + esc((m.topics || [])[0] || 'Council matter') + '</p>' +
      '<header class="mhead"><p class="mu-overline">' + esc((m.topics || [])[0] || 'Council matter') + '</p><h1>' + esc(m.title) + '</h1>' + statusChip(m) +
      '<dl class="mfacts"><div><dt>Authority</dt><dd>' + esc(m.authority || 'Not stated') + '</dd></div><div><dt>Location</dt><dd>' + esc(m.location || 'Not stated') + '</dd></div><div><dt>Checked</dt><dd>' + esc(asOf()) + '</dd></div></dl>' +
      '<p class="notice">This is not the official notice.</p></header>' +
      '<div class="toggles no-print"><label><input type="checkbox" id="t-noai"' + (state.noAI ? ' checked' : '') + '> Show without AI</label>' +
      '<label><input type="checkbox" id="t-easy"' + (state.easy ? ' checked' : '') + '> Easy Read</label>' +
      '<button type="button" class="mu-btn mu-btn--ghost" onclick="window.print()">Print</button></div>';
    if (state.easy) html += easyRead(m);
    html += '<div class="mlayout"><nav class="toc no-print" aria-label="On this page"><p class="mu-overline">On this page</p>' + SECTIONS.map(function (s) { return '<a href="#sec-' + s[0] + '" data-jump="sec-' + s[0] + '">' + s[1] + '</a>'; }).join('') + '<a href="#ids-h" data-jump="ids-h">Item Passport</a><a href="#life-h" data-jump="life-h">Life of a decision</a></nav><div class="mbody">';
    SECTIONS.forEach(function (s) {
      var key = s[0], hid = 'sec-' + key;
      html += '<section aria-labelledby="' + hid + '"><h2 id="' + hid + '">' + s[1] + '</h2>';
      if (key === 'records') { html += records(m) + '</section>'; return; }
      var cs = claims.filter(function (c) { return c.section === key; });
      html += cs.length ? cs.map(claimHTML).join('') : '<p class="empty">Not established in the records checked (as of ' + esc(asOf()) + ').</p>';
      if (key === 'conditions') {
        if ((m.conditions || []).length) html += '<h3>Conditions in the records</h3><ul>' + m.conditions.map(function (c) { return '<li>' + esc(c.text) + (c.imposed_by ? ' <span class="mu-meta">(imposed by ' + esc(c.imposed_by) + ')</span>' : '') + (c.passage_id ? sourceDetails(c.passage_id) : '') + '</li>'; }).join('') + '</ul>';
        var q = []; claims.forEach(function (c) { (c.qualifiers_required || []).forEach(function (x) { if (q.indexOf(x) < 0) q.push(x); }); });
        if (q.length) html += '<div class="mu-alert mu-alert--info" role="status"><span class="mu-alert__dot" aria-hidden="true"></span><div><p class="mu-alert__title">Conditions kept</p><p class="mu-alert__text">Every sentence here had to keep these qualifiers: ' + q.map(esc).join('; ') + '.</p></div></div>';
      }
      if (key === 'have_a_say') html += windowsWall(m);
      html += '</section>';
    });
    html += '<section class="panel" aria-labelledby="ids-h"><h2 id="ids-h">Item Passport</h2><p class="mu-meta">Numbers this matter has used.</p><ul class="idlist">' +
      (m.identifiers || []).map(function (i) {
        return '<li><span class="idchip">' + esc(i.value) + '</span> <span class="mu-meta">' + esc(i.kind) + '</span>' +
          (i.valid_from ? ' · used from ' + esc(i.valid_from) : '') + (i.valid_to ? ' · used until ' + esc(i.valid_to) : '') +
          (i.note ? ' · ' + esc(i.note) : '') + (i.passage_id ? sourceDetails(i.passage_id) : '') + '</li>';
      }).join('') + '</ul></section>';
    html += lifeOfDecision(m) + '</div></div>';
    main.innerHTML = html;
    main.querySelectorAll('[data-jump]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); var t = document.getElementById(a.getAttribute('data-jump')); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }); });
    document.getElementById('t-noai').addEventListener('change', function (e) { state.noAI = e.target.checked; renderMatter(id); document.getElementById('t-noai').focus(); });
    document.getElementById('t-easy').addEventListener('change', function (e) { state.easy = e.target.checked; renderMatter(id); document.getElementById('t-easy').focus(); });
    focusMain(m.title);
  }
  function records(m) {
    var pids = [];
    (m.claims || []).forEach(function (c) { pids = pids.concat(c.passage_ids || []); });
    (m.events || []).concat(m.windows || [], m.conditions || [], m.identifiers || []).forEach(function (x) { if (x.passage_id) pids.push(x.passage_id); });
    var sids = [];
    pids.forEach(function (pid) { var p = passage(pid); if (p && sids.indexOf(p.snapshot_id) < 0) sids.push(p.snapshot_id); });
    if (!sids.length) return '<p class="empty">Not established in the records checked (as of ' + esc(asOf()) + ').</p>';
    return '<ul>' + sids.map(function (sid) {
      var s = snapshot(sid) || { title: sid };
      return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" rel="noopener" target="_blank">' + esc(s.title) + '</a>' : esc(s.title)) +
        ' <span class="mu-meta">· ' + esc(s.publisher || '') + ' · checked ' + esc(s.fetched_at || asOf()) + (s.availability && s.availability !== 'ok' ? ' · ' + esc(s.availability) : '') + '</span></li>';
    }).join('') + '</ul>';
  }
  function easyRead(m) {
    var kinds = (m.events || []).map(function (e) { return e.kind; });
    var steps = [['proposed', 'Proposed', ['proposed']], ['rec', 'Staff recommendation', ['staff_recommendation']], ['decided', 'Decided', ['council_decision']], ['force', 'In force', ['in_force']], ['done', 'Done', ['done', 'repealed']]];
    return '<section class="panel" aria-labelledby="er-h"><h2 id="er-h">Easy Read</h2>' +
      ((m.easy_read || []).length ? '<ul>' + m.easy_read.map(function (l) { return '<li>' + esc(l.text) + (l.claim_id ? ' <a href="#claim-' + esc(l.claim_id) + '" onclick="document.getElementById(\'claim-' + esc(l.claim_id) + '\').scrollIntoView();return false;">Where this comes from</a>' : '') + '</li>'; }).join('') + '</ul>' : '<p class="empty">No Easy Read lines yet.</p>') +
      '<h3>Where this is now</h3><ol class="strip">' + steps.map(function (s) {
        var hit = s[2].some(function (k) { return kinds.indexOf(k) >= 0; });
        return '<li class="' + (hit ? 'done' : '') + '">' + s[1] + '<br><span class="mu-meta">' + (hit ? 'Yes, in the records' : 'Not in the records yet') + '</span></li>';
      }).join('') + '</ol></section>';
  }
  function today() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function windowsWall(m) {
    var ws = m.windows || [];
    if (!ws.length) return '';
    return '<h3>Windows to have a say</h3><div class="windows">' + ws.map(function (w) {
      var status, quote = w.deadline_quote;
      if (w.state === 'dated' && w.deadline_date && quote) status = w.deadline_date >= today() ? '<span class="chip chip--open">Open</span> Closes ' + esc(w.deadline_date) : '<span class="chip chip--closed">Closed</span> Closed ' + esc(w.deadline_date);
      else if (w.state === 'dated') status = '<span class="chip">Date not shown</span> A date is shown only with its source quote.';
      else if (w.state === 'rule_based') status = '<span class="chip">General rule</span> General rule. Confirm on the item page.';
      else if (w.state === 'not_published') status = '<span class="chip">No deadline stated</span> Source checked, no deadline stated';
      else if (w.state === 'source_unavailable') status = '<span class="chip">Source unavailable</span> The source could not be read.';
      else status = '<span class="chip">Not checked</span> No source checked yet.';
      return '<div class="window"><div><p><strong>' + esc(w.action) + '</strong></p><p class="mu-meta">' + esc(w.channel || '') + '</p><p>' + status + '</p></div>' +
        '<div>' + (quote ? '<blockquote>' + esc(quote) + '</blockquote>' : '<p class="empty">No quote stated.</p>') + (w.passage_id ? sourceDetails(w.passage_id) : '') + '</div></div>';
    }).join('') + '</div>';
  }
  function lifeOfDecision(m) {
    var ev = (m.events || []).slice().sort(function (a, b) { return String(a.date).localeCompare(String(b.date)); });
    var cards = ev.map(function (e) {
      var p = passage(e.passage_id), s = p ? snapshot(p.snapshot_id) : null;
      return '<article class="tcard" tabindex="0" aria-label="' + esc((KIND[e.kind] || e.kind) + ', ' + e.date) + '"><p class="mu-overline">' + esc(e.date) + ' · ' + esc(KIND[e.kind] || e.kind) + '</p>' +
        '<p><strong>' + esc(e.actor) + '</strong></p><blockquote>' + esc(e.outcome_text) + '</blockquote><dl>' +
        '<dt>What this record establishes</dt><dd>' + esc(e.establishes || 'Not stated') + '</dd>' +
        '<dt>What it does not establish</dt><dd>' + esc(e.not_establishes || 'Not stated') + '</dd></dl>' +
        (s && s.url ? '<p><a href="' + esc(s.url) + '" rel="noopener" target="_blank">Source: ' + esc(s.title) + '</a></p>' : '') + '</article>';
    });
    if (!ev.some(function (e) { return e.kind === 'council_decision'; }))
      cards.push('<article class="tcard tcard--missing" tabindex="0"><p class="mu-overline">Council decision</p><p><strong>No decision record found (as of ' + esc(asOf()) + ')</strong></p></article>');
    return '<section aria-labelledby="life-h"><h2 id="life-h">Life of a decision</h2><p class="mu-meta">Each step comes from a dated record.</p><div class="timeline">' + cards.join('') + '</div></section>';
  }

  /* Comment */
  var PATTERNS = [
    ['email', /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi],
    ['phone', /(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g],
    ['postal code', /\b[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d\b/gi],
    ['address', /\b\d{1,5}\s+(?:[A-Z][\w'-]*\s+){1,4}(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Boulevard|Cres|Crescent|Ct|Court|Pl|Place|Way|Lane|Ln|Line|Trail|Pkwy|Terr|Terrace)\b\.?(?:\s+[NSEW]\b)?/gi],
    ['name', /(?:my name is|i am|i'm)\s+([A-Z][a-z'-]+(?:\s+[A-Z][a-z'-]+){0,2})/g]
  ];
  function highlight(text) {
    var spans = [];
    PATTERNS.forEach(function (p) {
      var re = new RegExp(p[1].source, p[1].flags), mm;
      while ((mm = re.exec(text))) {
        var start = mm.index, str = mm[0];
        if (p[0] === 'name') { if (!/^my name is/i.test(str)) continue; start = mm.index + str.indexOf(mm[1]); str = mm[1]; }
        spans.push([start, start + str.length, p[0]]);
        if (!mm[0].length) re.lastIndex++;
      }
    });
    spans.sort(function (a, b) { return a[0] - b[0]; });
    var out = '', pos = 0, kinds = {};
    spans.forEach(function (s) {
      if (s[0] < pos) return;
      out += esc(text.slice(pos, s[0])) + '<mark data-kind="' + s[2] + '">' + esc(text.slice(s[0], s[1])) + '</mark>';
      pos = s[1]; kinds[s[2]] = (kinds[s[2]] || 0) + 1;
    });
    return { html: out + esc(text.slice(pos)), kinds: kinds };
  }
  function renderComment() {
    main.innerHTML = '<h1>Have your say: draft check</h1>' +
      '<div class="mu-alert mu-alert--info" role="status"><span class="mu-alert__dot" aria-hidden="true"></span><div><p class="mu-alert__title">Your draft never leaves this device. Muni does not submit anything.</p><p class="mu-alert__text">This check runs in your browser. It can miss things, so read your draft yourself too.</p></div></div>' +
      '<div class="mu-field" style="margin-top:16px"><label for="draft">Your comment draft</label><textarea id="draft" aria-describedby="draft-help"></textarea>' +
      '<span class="mu-field__help" id="draft-help">The check highlights email addresses, phone numbers, postal codes, street addresses and names after “my name is”.</span></div>' +
      '<h2>What could become public</h2><p id="exp-sum" role="status" aria-live="polite">Nothing found yet.</p><div class="preview" id="exp-prev" aria-label="Highlighted preview"></div>' +
      '<h2>What the City says about publication</h2>' +
      ((D.channels || []).length ? D.channels.map(function (c) { return '<div class="claim"><p><strong>' + esc(c.channel) + ':</strong> ' + esc(c.statement) + '</p>' + (c.passage_id ? sourceDetails(c.passage_id) : '') + '</div>'; }).join('') : '<p class="empty">Not established in the records checked (as of ' + esc(asOf()) + ').</p>');
    var ta = document.getElementById('draft');
    ta.addEventListener('input', function () {
      var r = highlight(ta.value), ks = Object.keys(r.kinds);
      document.getElementById('exp-prev').innerHTML = r.html;
      document.getElementById('exp-sum').textContent = ks.length ? 'Found: ' + ks.map(function (k) { return r.kinds[k] + ' ' + k + (r.kinds[k] > 1 ? 's' : ''); }).join(', ') + '. These are marked below.' : 'Nothing found yet.';
    });
    focusMain('Draft check');
  }

  /* Staff */
  function csvCell(v) { v = String(v == null ? '' : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function renderStaff() {
    var dis = D.discrepancies || [], bl = D.blocked_claims || [];
    var bad = (D.snapshots || []).filter(function (s) { return s.availability && s.availability !== 'ok'; });
    main.innerHTML = '<h1>Drift Sentinel</h1><p>For staff. Checked on ' + esc(asOf()) + '.</p>' +
      '<p><button type="button" class="mu-btn mu-btn--primary" id="csv-btn">Download CSV</button></p>' +
      '<h2>Differences between guides and rules</h2><p class="mu-meta">A difference alone doesn\'t establish which source is right.</p>' +
      (dis.length ? '<div class="table-wrap"><table><caption class="mu-meta" style="text-align:left">Each row compares a public guide with the rule it describes.</caption><thead><tr><th scope="col">Topic</th><th scope="col">Guide says</th><th scope="col">Rule says</th><th scope="col">Difference</th><th scope="col">Suggested fix</th></tr></thead><tbody>' +
        dis.map(function (d) {
          return '<tr><td>' + esc(d.topic) + '<br><span class="mu-meta">' + esc(d.kind || '') + '</span></td><td><blockquote>' + esc(d.guide && d.guide.text) + '</blockquote>' + sourceDetails(d.guide && d.guide.passage_id) + '</td>' +
            '<td><blockquote>' + esc(d.rule && d.rule.text) + '</blockquote>' + sourceDetails(d.rule && d.rule.passage_id) + '</td><td>' + esc(d.difference) + '</td><td>' + esc(d.suggested_fix) + '</td></tr>';
        }).join('') + '</tbody></table></div>' : '<p class="empty">No differences recorded in this export.</p>') +
      '<h2>Held back by Qualifier Keeper</h2><p class="mu-meta">These sentences were not published because they dropped a required qualifier.</p>' +
      (bl.length ? '<ul>' + bl.map(function (b) { return '<li><strong>' + esc(b.text) + '</strong><br><span class="mu-meta">Matter: ' + esc(b.matter_id) + ' · Missing: ' + (b.missing || []).map(esc).join('; ') + '</span></li>'; }).join('') + '</ul>' : '<p class="empty">No held-back sentences in this export.</p>') +
      '<h2>Sources we could not read</h2>' +
      (bad.length ? '<ul>' + bad.map(function (s) { return '<li><strong>' + esc(s.title) + '</strong> · ' + esc(s.availability) + (s.reason ? ': ' + esc(s.reason) : '') + (s.url ? ' · <a href="' + esc(s.url) + '" rel="noopener" target="_blank">Link</a>' : '') + '</li>'; }).join('') + '</ul>' : '<p class="empty">All sources were readable.</p>');
    document.getElementById('csv-btn').addEventListener('click', function () {
      var rows = [['type', 'topic_or_matter', 'guide_or_text', 'rule_or_missing', 'difference_or_reason', 'suggested_fix']];
      dis.forEach(function (d) { rows.push(['discrepancy', d.topic, d.guide && d.guide.text, d.rule && d.rule.text, d.difference, d.suggested_fix]); });
      bl.forEach(function (b) { rows.push(['blocked_claim', b.matter_id, b.text, (b.missing || []).join('; '), '', '']); });
      bad.forEach(function (s) { rows.push(['source_unavailable', s.title, s.url, s.availability, s.reason, '']); });
      var blob = new Blob([rows.map(function (r) { return r.map(csvCell).join(','); }).join('\n')], { type: 'text/csv' });
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'muni-drift-' + asOf() + '.csv';
      document.body.appendChild(a); a.click(); a.remove();
    });
    focusMain('Staff');
  }

  /* About */
  function renderAbout() {
    main.innerHTML = '<h1>How this works</h1>' +
      '<section class="panel"><h2>What AI drafts</h2><p>AI drafts some plain-language sentences from the City\'s own records. Each one is labelled “AI paraphrase” and links to the passage it came from. Use “Show without AI” on any matter page to see the source text instead.</p></section>' +
      '<section class="panel"><h2>What AI never does</h2><ul><li>It never decides the status of a matter. Status comes only from dated records such as minutes and by-laws.</li><li>It never writes numbers. Numbers are copied from the records.</li><li>It never computes deadlines. Your browser compares a quoted deadline date with today, and we always show the quote.</li></ul></section>' +
      '<section class="panel"><h2>How drafts are checked</h2><ul><li>Every sentence must point to a passage in a saved copy of a City or Region record.</li><li>Qualifier Keeper holds back any sentence that drops a required qualifier, such as “not a borrowing approval”.</li><li>A person approves sentences before they are published.</li><li>Drift Sentinel compares public guides with the rules they describe and flags differences for staff.</li><li>When a record is missing we say so: “Not established in the records checked”.</li></ul></section>' +
      '<section class="panel"><h2>What labels mean</h2><p><span class="chip">Quote</span> copied word for word. <span class="chip">Extracted</span> a fact pulled from a record. <span class="chip chip--ai">AI paraphrase</span> drafted by AI, checked by a person. <span class="chip">Written by a person</span> written by a person from the record.</p></section>' +
      '<p>This is not the official notice. Records checked on ' + esc(asOf()) + '.</p>';
    focusMain('How this works');
  }

  /* Boot */
  Promise.all([
    fetch('data/muni.json').then(function (r) { if (!r.ok) throw new Error('muni.json ' + r.status); return r.json(); }),
    fetch('data/wards.geojson').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
  ]).then(function (res) {
    D = res[0]; WARDS = res[1] && res[1].features ? res[1] : null;
    var fc = document.getElementById('foot-checked'); if (fc) fc.textContent = 'Checked against official records on ' + (D.checked_on || 'unknown date') + '. Muni is independent and is not the official notice.';
    D.matters = D.matters || []; D.passages = D.passages || []; D.snapshots = D.snapshots || [];
    window.addEventListener('hashchange', route);
    route();
  }).catch(function (e) {
    main.innerHTML = '<h1>We could not load the records</h1><p>' + esc(e.message) + '</p>';
  });
})();
