import {filterPackages, getPackageDate, sortPackages} from './catalog-core.mjs';

const $ = selector => document.querySelector(selector);
const $$ = selector => Array.from(document.querySelectorAll(selector));
const params = new URLSearchParams(location.search);
const state = {
  query: params.get('q') || '',
  architecture: params.get('arch') || '',
  source: params.get('source') || '',
  installable: params.get('installable') || '',
  sort: params.get('sort') || 'name',
  direction: params.get('dir') === 'desc' ? 'desc' : 'asc',
};
let allPackages = [];

function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function sourceLabel(pkg) {
  if (pkg.source) return pkg.source;
  if (pkg.source_repository) return pkg.source_repository;
  const ref = pkg.source_ref || '';
  if (ref.includes('@')) return ref.split('@', 1)[0];
  return ref || 'unbekannt';
}

function formatBytes(value) {
  const bytes = Number(value || 0);
  if (!bytes) return '–';
  const units = ['B','KiB','MiB','GiB'];
  let n = bytes, i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i += 1; }
  return `${n >= 10 || i === 0 ? n.toFixed(0) : n.toFixed(1)} ${units[i]}`;
}
function badge(pkg) {
  if (pkg.installable === true) return '<span class="badge ok">INSTALLIERBAR</span>';
  return '<span class="badge history">HISTORISCH</span>';
}

function artifactLink(pkg) {
  if (!pkg.download) return '–';
  const href = new URL(pkg.download, location.href).href;
  return `<a class="download-link" href="${escapeHTML(href)}">Download ↗</a>`;
}

function populateSelect(select, values, selected) {
  for (const value of [...new Set(values.filter(Boolean))].sort((a,b) => a.localeCompare(b, 'de-DE', {numeric:true}))) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    select.append(option);
  }
  select.value = selected;
}

function syncUrl() {
  const next = new URLSearchParams();
  if (state.query) next.set('q', state.query);
  if (state.architecture) next.set('arch', state.architecture);
  if (state.source) next.set('source', state.source);
  if (state.installable) next.set('installable', state.installable);
  if (state.sort !== 'name') next.set('sort', state.sort);
  if (state.direction !== 'asc') next.set('dir', state.direction);
  history.replaceState(null, '', `${location.pathname}${next.size ? `?${next}` : ''}`);
}

function renderStats(packages) {
  $('#stat-total').textContent = packages.length.toLocaleString('de-DE');
  $('#stat-installable').textContent = packages.filter(p => p.installable === true).length.toLocaleString('de-DE');
  $('#stat-historical').textContent = packages.filter(p => p.installable !== true).length.toLocaleString('de-DE');
  $('#stat-names').textContent = new Set(packages.map(p => p.name)).size.toLocaleString('de-DE');
}
function renderDesktop(packages) {
  const body = $('#package-rows');
  if (!packages.length) {
    body.innerHTML = '<tr><td class="empty" colspan="8">Keine Pakete entsprechen den aktuellen Filtern.</td></tr>';
    return;
  }
  body.innerHTML = packages.map(pkg => `<tr>
    <td><span class="pkg-name">${escapeHTML(pkg.name)}</span><span class="pkg-description">${escapeHTML(pkg.description || '')}</span></td>
    <td class="mono">${escapeHTML(pkg.version)}</td>
    <td class="mono">${escapeHTML(getPackageDate(pkg) || '–')}</td>
    <td><span class="badge source">${escapeHTML(pkg.architecture || 'unknown')}</span></td>
    <td class="mono">${escapeHTML(sourceLabel(pkg))}</td>
    <td>${badge(pkg)}</td>
    <td class="mono">${formatBytes(pkg.size)}</td>
    <td>${artifactLink(pkg)}</td>
  </tr>`).join('');
}

function renderMobile(packages) {
  const root = $('#mobile-package-list');
  if (!packages.length) {
    root.innerHTML = '<div class="empty">Keine Pakete entsprechen den aktuellen Filtern.</div>';
    return;
  }
  root.innerHTML = packages.map(pkg => `<article class="mobile-card">
    <div class="mobile-card-head"><div><span class="pkg-name">${escapeHTML(pkg.name)}</span><span class="pkg-description">${escapeHTML(pkg.description || '')}</span></div>${badge(pkg)}</div>
    <dl><dt>Version</dt><dd class="mono">${escapeHTML(pkg.version)}</dd><dt>Datum</dt><dd class="mono">${escapeHTML(getPackageDate(pkg) || '–')}</dd><dt>Architektur</dt><dd>${escapeHTML(pkg.architecture || 'unknown')}</dd><dt>Quelle</dt><dd class="mono">${escapeHTML(sourceLabel(pkg))}</dd><dt>Größe</dt><dd class="mono">${formatBytes(pkg.size)}</dd><dt>Artefakt</dt><dd>${artifactLink(pkg)}</dd></dl>
  </article>`).join('');
}
function updateSortIndicators() {
  $$('.sort-button').forEach(button => {
    const active = button.dataset.sort === state.sort;
    const value = active ? (state.direction === 'asc' ? 'ascending' : 'descending') : 'none';
    button.setAttribute('aria-sort', value);
    button.closest('th')?.setAttribute('aria-sort', value);
  });
}

function render() {
  const filtered = filterPackages(allPackages, state);
  const sorted = sortPackages(filtered, state.sort, state.direction);
  renderDesktop(sorted);
  renderMobile(sorted);
  updateSortIndicators();
  $('#visible-count').textContent = `${sorted.length.toLocaleString('de-DE')} sichtbar`;
  const active = [];
  if (state.query) active.push(`Suche: ${state.query}`);
  if (state.architecture) active.push(`Architektur: ${state.architecture}`);
  if (state.source) active.push(`Quelle: ${state.source}`);
  if (state.installable) active.push(state.installable === 'yes' ? 'Installierbar' : 'Historisch');
  $('#active-summary').textContent = active.length ? active.join(' · ') : 'Keine Filter aktiv';
  syncUrl();
}

function bindControls() {
  const search = $('#package-search');
  const architecture = $('#architecture-filter');
  const source = $('#source-filter');
  const installable = $('#installable-filter');
  search.value = state.query;
  installable.value = state.installable;
  search.addEventListener('input', event => { state.query = event.target.value.trim(); render(); });
  architecture.addEventListener('change', event => { state.architecture = event.target.value; render(); });
  source.addEventListener('change', event => { state.source = event.target.value; render(); });
  installable.addEventListener('change', event => { state.installable = event.target.value; render(); });
  $$('.sort-button').forEach(button => button.addEventListener('click', () => {
    const key = button.dataset.sort;
    if (state.sort === key) state.direction = state.direction === 'asc' ? 'desc' : 'asc';
    else { state.sort = key; state.direction = 'asc'; }
    render();
  }));
}
async function loadIndex() {
  try {
    const response = await fetch('index.json', {cache:'no-store', headers:{Accept:'application/json'}});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    allPackages = Array.isArray(data.packages) ? data.packages : [];
    populateSelect($('#architecture-filter'), allPackages.map(p => p.architecture), state.architecture);
    populateSelect($('#source-filter'), allPackages.map(sourceLabel), state.source);
    bindControls();
    renderStats(allPackages);
    render();
    $('#repo-status').textContent = `ONLINE // ${allPackages.length.toLocaleString('de-DE')} INDEX-EINTRÄGE`;
  } catch (error) {
    $('#repo-status').textContent = `INDEX FEHLER // ${error.message}`;
    $('#package-rows').innerHTML = '<tr><td class="empty" colspan="8">index.json konnte nicht geladen werden.</td></tr>';
    $('#mobile-package-list').innerHTML = '<div class="empty">index.json konnte nicht geladen werden.</div>';
  }
}

loadIndex();