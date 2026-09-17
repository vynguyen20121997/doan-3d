import fs from 'fs';

const R = 6371.0088; // km
const rad = d => d * Math.PI / 180;

// spherical excess area of a ring (km^2)
function ringArea(ring) {
  let total = 0;
  const n = ring.length;
  for (let i = 0; i < n; i++) {
    const [lon1, lat1] = ring[i];
    const [lon2, lat2] = ring[(i + 1) % n];
    total += (rad(lon2) - rad(lon1)) * (2 + Math.sin(rad(lat1)) + Math.sin(rad(lat2)));
  }
  return Math.abs(total * R * R / 2);
}
function polyArea(coords) {           // [outer, ...holes]
  return coords.reduce((a, r, i) => a + (i === 0 ? ringArea(r) : -ringArea(r)), 0);
}
function area(geom) {
  return geom.type === 'Polygon'
    ? polyArea(geom.coordinates)
    : geom.coordinates.reduce((a, p) => a + polyArea(p), 0);
}

const fc = JSON.parse(fs.readFileSync('./data/hcmc-wards.geojson', 'utf8'));
let withPop = 0;
fc.features.forEach((f, i) => {
  const p = f.properties;
  p.id = i + 1;
  p.area_km2 = Math.round(area(f.geometry) * 100) / 100;
  if (p.population) withPop++;
  p.density = p.population ? Math.round(p.population / p.area_km2) : null;
});
const tot = fc.features.reduce((a, f) => a + f.properties.area_km2, 0);
console.log('features', fc.features.length, '| total area km2', tot.toFixed(0), '| with population', withPop);
console.log(JSON.stringify(fc.features[0].properties));
fs.writeFileSync('./data/hcmc-wards.geojson', JSON.stringify(fc));
console.log('size KB', (fs.statSync('./data/hcmc-wards.geojson').size / 1024).toFixed(0));
