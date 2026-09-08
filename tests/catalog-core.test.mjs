import test from 'node:test';
import assert from 'node:assert/strict';
import {
  filterPackages,
  getPackageDate,
  sortPackages,
} from '../assets/js/catalog-core.mjs';

const packages = [
  {name:'fw', version:'1.2.0', description:'Fritz.Wulf package manager', architecture:'all', source:'Fritz-Wulf/fw', installable:true, release_date:'2026-09-09', size:1200},
  {name:'yourfritz-fitdump', version:'git-20220623-a', description:'Historical FIT dump source', architecture:'all', source_ref:'PeterPawn/YourFritz@abc', compatibility:'historical-source-only', installable:false, upstream_date:'2022-06-23', size:900},
  {name:'fw', version:'1.1.0', description:'Older package manager', architecture:'mips32', source:'Fritz-Wulf/fw', installable:true, release_date:'2026-09-01', size:1100},
];

test('search spans name, version, description, source and compatibility', () => {
  assert.equal(filterPackages(packages, {query:'yourfritz'}).length, 1);
  assert.equal(filterPackages(packages, {query:'1.2.0'}).length, 1);
  assert.equal(filterPackages(packages, {query:'historical-source'}).length, 1);
});

test('installable and architecture filters compose', () => {
  const out = filterPackages(packages, {installable:'yes', architecture:'mips32'});
  assert.deepEqual(out.map(p => p.version), ['1.1.0']);
});

test('package date falls back from release date to upstream date', () => {
  assert.equal(getPackageDate(packages[0]), '2026-09-09');
  assert.equal(getPackageDate(packages[1]), '2022-06-23');
});

test('sorting supports name, date, size and stable tie-breaking', () => {
  assert.deepEqual(sortPackages(packages, 'name', 'asc').map(p => p.name), ['fw','fw','yourfritz-fitdump']);
  assert.deepEqual(sortPackages(packages, 'date', 'desc').map(p => p.version), ['1.2.0','1.1.0','git-20220623-a']);
  assert.deepEqual(sortPackages(packages, 'size', 'asc').map(p => p.size), [900,1100,1200]);
  assert.deepEqual(sortPackages(packages, 'version', 'desc').slice(0,2).map(p => p.version), ['git-20220623-a','1.2.0']);
});

test('source filter accepts explicit source and source_ref fallback', () => {
  assert.equal(filterPackages(packages, {source:'Fritz-Wulf/fw'}).length, 2);
  assert.equal(filterPackages(packages, {source:'PeterPawn/YourFritz'}).length, 1);
});