import fs from "fs";
import { feature } from "topojson-client";
import * as d3 from "d3-geo";
const dir = process.argv[2], out = process.argv[3];
const t50 = JSON.parse(fs.readFileSync(dir + "/world-atlas/countries-50m.json"));
const t110 = JSON.parse(fs.readFileSync(dir + "/world-atlas/land-110m.json"));
const countries = feature(t50, t50.objects.countries).features;
const byId = (id) => countries.find((f) => +f.id === id);
const svg = (w, h, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;
// 1 Iraq silhouette with Baghdad
{
  const iq = byId(368), W = 900, H = 900;
  const pr = d3.geoMercator().fitExtent([[30, 30], [W - 30, H - 30]], iq), path = d3.geoPath(pr);
  const [bx, by] = pr([44.366, 33.315]);
  fs.writeFileSync(out + "/iraq.svg", svg(W, H, `<path d="${path(iq)}" fill="#C98A2B" stroke="#8C5A12" stroke-width="3"/>
<circle cx="${bx}" cy="${by}" r="16" fill="#1E5B4F" stroke="#fff" stroke-width="5"/>
<text x="${bx + 26}" y="${by + 12}" font-family="Calibri,Carlito,Arial" font-size="44" font-weight="bold" fill="#1E5B4F">Baghdad</text>`));
}
// 2 Region map
{
  const W = 1200, H = 900;
  const box = { type: "Feature", geometry: { type: "MultiPoint", coordinates: [[24, 12], [60, 38]] } };
  const pr = d3.geoMercator().fitExtent([[0, 0], [W, H]], box), path = d3.geoPath(pr);
  const col = { 368: "#C98A2B", 682: "#1E5B4F", 422: "#7F1D3A", 818: "#0B5394" };
  let body = `<rect width="${W}" height="${H}" fill="#EAF2F5"/>`;
  countries.forEach((f) => { body += `<path d="${path(f)}" fill="${col[+f.id] || "#D9DED9"}" stroke="#fff" stroke-width="1.5"/>`; });
  const lab = [[44, 33, "Iraq", "#fff"], [44.5, 23.5, "Saudi Arabia", "#fff"], [35.9, 33.9, "Lebanon", "#7F1D3A"], [29.5, 26.5, "Egypt", "#fff"]];
  lab.forEach(([lo, la, t, c]) => { const [x, y] = pr([lo, la]); const dx = t === "Lebanon" ? -150 : -t.length * 11;
    body += `<text x="${x + dx}" y="${y + 12}" font-family="Calibri,Carlito,Arial" font-size="${t === "Lebanon" ? 34 : 40}" font-weight="bold" fill="${c}">${t}</text>`; });
  fs.writeFileSync(out + "/region.svg", svg(W, H, body));
}
// 3 Dotted world map
{
  const land = feature(t110, t110.objects.land), W = 1600, H = 800;
  const pr = d3.geoEquirectangular().fitExtent([[10, 10], [W - 10, H - 10]], { type: "Sphere" });
  let body = "";
  for (let la = 80; la > -58; la -= 2.2) for (let lo = -178; lo < 180; lo += 2.2) {
    if (d3.geoContains(land, [lo, la])) { const [x, y] = pr([lo, la]); body += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.6" fill="#3A3A3A"/>`; }
  }
  const [bx, by] = pr([44.366, 33.315]);
  body += `<circle cx="${bx}" cy="${by}" r="14" fill="#C98A2B" stroke="#fff" stroke-width="4"/>`;
  fs.writeFileSync(out + "/world.svg", svg(W, H, body));
}
console.log("ok");
