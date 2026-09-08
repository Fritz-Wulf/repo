const text = value => String(value ?? '').toLocaleLowerCase('de-DE');

export function getPackageDate(pkg) {
  return pkg.release_date || pkg.upstream_date || pkg.build_date || pkg.date || '';
}

function packageSource(pkg) {
  return pkg.source || pkg.source_repository || pkg.source_ref || '';
}

function packageSearchText(pkg) {
  return [
    pkg.name,
    pkg.version,
    pkg.description,
    pkg.source,
    pkg.source_repository,
    pkg.source_ref,
    pkg.compatibility,
    pkg.license,
    ...(Array.isArray(pkg.devices) ? pkg.devices : []),
  ].map(text).join(' ');
}

export function filterPackages(packages, filters = {}) {
  const query = text(filters.query).trim();
  const architecture = text(filters.architecture).trim();
  const source = text(filters.source).trim();
  const installable = text(filters.installable).trim();
  return packages.filter(pkg => {
    if (query && !packageSearchText(pkg).includes(query)) return false;
    if (architecture && text(pkg.architecture) !== architecture) return false;
    if (source && !text(packageSource(pkg)).includes(source)) return false;
    if (installable === 'yes' && pkg.installable !== true) return false;
    if (installable === 'no' && pkg.installable === true) return false;
    return true;
  });
}

function valueForSort(pkg, key) {
  if (key === 'date') return getPackageDate(pkg);
  if (key === 'source') return packageSource(pkg);
  if (key === 'installable') return pkg.installable === true ? 1 : 0;
  if (key === 'size') return Number(pkg.size || 0);
  return pkg[key] ?? '';
}

export function sortPackages(packages, key = 'name', direction = 'asc') {
  const factor = direction === 'desc' ? -1 : 1;
  return packages.map((pkg, index) => ({pkg, index})).sort((a, b) => {
    const av = valueForSort(a.pkg, key);
    const bv = valueForSort(b.pkg, key);
    let cmp = 0;
    if (typeof av === 'number' && typeof bv === 'number') cmp = av - bv;
    else cmp = String(av).localeCompare(String(bv), 'de-DE', {numeric:true, sensitivity:'base'});
    if (cmp === 0) cmp = text(a.pkg.name).localeCompare(text(b.pkg.name), 'de-DE');
    if (cmp === 0) cmp = a.index - b.index;
    return cmp * factor;
  }).map(entry => entry.pkg);
}