import fs from 'fs';
import osmtogeojson from 'osmtogeojson';

const osm = JSON.parse(fs.readFileSync('./data/raw-wards.json', 'utf8'));
const gj = osmtogeojson(osm);

// keep polygonal admin units only
const feats = gj.features.filter(f =>
  f.geometry && /Polygon/.test(f.geometry.type) && f.properties?.admin_level === '6');

const norm = feats.map(f => {
  const p = f.properties;
  const name = p['name:vi'] || p.name || '';
  let type = 'Phường';
  if (/^Đặc khu/i.test(name)) type = 'Đặc khu';
  else if (/^Xã/i.test(name)) type = 'Xã';
  return {
    type: 'Feature',
    geometry: f.geometry,
    properties: {
      name,
      short_name: name.replace(/^(Phường|Xã|Đặc khu)\s+/i, ''),
      unit_type: type,
      osm_id: (p.id || f.id || '').toString(),
      population: p.population ? Number(p.population) : null,
      ref: p.ref || null
    }
  };
});

const counts = norm.reduce((a, f) => (a[f.properties.unit_type] = (a[f.properties.unit_type] || 0) + 1, a), {});
console.log('features:', norm.length, counts);

fs.writeFileSync('./data/hcmc-wards.full.geojson',
  JSON.stringify({ type: 'FeatureCollection', features: norm }));
console.log('size MB:', (fs.statSync('./data/hcmc-wards.full.geojson').size / 1e6).toFixed(2));
