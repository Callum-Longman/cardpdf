// Shared rendering logic for both web and CLI
// This is the single source of truth for card rendering

function esc(s) {
  if (s == null) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function toHTML(text) {
  let s = esc(text);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  return s.replace(/\n\n/g,"<br><br>").replace(/\n/g,"<br>");
}

function capitalise(s) {
  if (!s) return "";
  return s.split(' ').map(word =>
    word ? word.charAt(0).toUpperCase() + word.slice(1).toLowerCase() : ""
  ).join(' ');
}

function normaliseSpell(spell, edition) {
  if (edition === "2014") {
    return {
      name: spell.name||"",
      type: spell.type||"",
      level: null,
      school: null,
      action: spell.casting_time||"",
      concentration: false,
      ritual: spell.ritual||false,
      range: spell.range||"",
      duration: spell.duration||"",
      components: (spell.components||{}).raw||"",
      description: spell.description||"",
      extra_text: spell.higher_levels||"",
      extra_label: "At Higher Levels",
    };
  }
  // 2024
  const comps   = spell.components||[];
  const material= spell.material||"";
  let comp_str  = comps.map(c=>c.toUpperCase()).join(", ");
  if (material) comp_str += ` (${material})`;
  const level   = spell.level??0;
  const isCantrip = level === 0;
  return {
    name: spell.name||"",
    type: `${isCantrip?"Cantrip":`Level ${level}`} · ${capitalise(spell.school||"")}`,
    level,
    school: spell.school||"",
    action: spell.actionType||"",
    concentration: spell.concentration||false,
    ritual: spell.ritual||false,
    range: spell.range||"",
    duration: spell.duration||"",
    components: comp_str,
    description: spell.description||"",
    extra_text: isCantrip ? (spell.cantripUpgrade||"") : (spell.higherLevelSlot||""),
    extra_label: isCantrip ? "Upgrade" : "At Higher Levels",
  };
}

function renderCard(n, borderDataUrl) {
  const badges = (n.concentration ? '<span class="badge">Conc.</span>' : "")
               + (n.ritual        ? '<span class="badge">Ritual</span>' : "");
  const extraHTML = n.extra_text
    ? `<div class="extra"><em>${esc(n.extra_label)}:</em> ${esc(n.extra_text)}</div>`
    : "";
  const borderStyle = borderDataUrl
    ? `style="background-image:url(${borderDataUrl})"` : "";
  return `<div class="card" ${borderStyle}>`
    + `<div class="card-content">`
    + `<div class="hdr"><span class="name">${esc(n.name)}</span>${badges}</div>`
    + `<div class="sub">${esc(n.type)}</div>`
    + `<div class="meta">`
    + `<span><b>Action:</b> ${esc((n.action || "").trim() ? capitalise(n.action.trim()) : n.action)}</span><span><b>Range:</b> ${esc(n.range)}</span>`
    + `<span><b>Duration:</b> ${esc(n.duration)}</span><span><b>Components:</b> ${esc(n.components)}</span>`
    + `</div>`
    + `<div class="desc">${toHTML(n.description)}</div>${extraHTML}`
    + `</div></div>`;
}

const DEFAULT_PADDING_MM = 6;
const DEFAULT_FONT_SIZE_PT = 5.5;

function buildCardCSS(paddingMm, fontSizePt) {
  const pad = (paddingMm != null && paddingMm !== "") ? `${paddingMm}mm` : `${DEFAULT_PADDING_MM}mm`;
  const fs  = (fontSizePt != null && fontSizePt !== "") ? `${fontSizePt}pt` : `${DEFAULT_FONT_SIZE_PT}pt`;
  return `
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, serif; background: #bbb; }
@media print {
  @page { size: A4; margin: 8mm; }
  body { background: white; }
  .page { box-shadow: none !important; margin: 0 !important; width: 194mm; height: 281mm; padding: 0; page-break-after: always; }
  .page:last-child { page-break-after: avoid; }
}
.page { display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, 1fr); gap: 2mm; width: 210mm; height: 297mm; padding: 8mm; margin: 14px auto; background: white; box-shadow: 0 2px 12px rgba(0,0,0,.35); }
.card { border: none; border-radius: 0; padding: 0; background-size: 100% 100%; background-position: 0 0; background-repeat: no-repeat; display: flex; flex-direction: column; gap: 1mm; overflow: hidden; }
.card-content { padding: ${pad}; flex: 1; overflow: hidden; display: flex; flex-direction: column; gap: 1mm; }
.card-empty { border: 0.5pt dashed #bbb; }
.hdr { display: flex; justify-content: space-between; align-items: flex-start; gap: 1mm; border-bottom: 0.5pt solid #555; padding-bottom: 1mm; }
.name { font-size: 10pt; font-weight: bold; line-height: 1.2; }
.badge { font-size: ${fs}; background: #333; color: #fff; padding: .4mm 1mm; border-radius: 1pt; white-space: nowrap; flex-shrink: 0; align-self: center; }
.sub { font-size: ${fs}; font-style: italic; color: #555; }
.meta { display: grid; grid-template-columns: 1fr 1fr; gap: .3mm 2mm; font-size: ${fs}; }
.desc { font-size: ${fs}; line-height: 1.35; flex: 1; overflow: hidden; }
.extra { font-size: ${fs}; font-style: italic; color: #444; border-top: .5pt solid #ccc; padding-top: 1mm; overflow: hidden; }
`;
}

const CARD_CSS = buildCardCSS();

function buildHTML(selected, borderDataUrl, paddingMm, fontSizePt) {
  const pages = [];
  for (let i=0; i<selected.length; i+=9) pages.push(selected.slice(i,i+9));
  let body = "";
  for (const page of pages) {
    let cards = page.map(({spell,year}) => renderCard(normaliseSpell(spell,year), borderDataUrl)).join("");
    cards += '<div class="card card-empty"></div>'.repeat(9 - page.length);
    body += `<div class="page">${cards}</div>\n`;
  }
  return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Spell Cards</title>`
    + `<style>${buildCardCSS(paddingMm, fontSizePt)}</style></head><body>${body}</body></html>`;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    esc,
    toHTML,
    capitalise,
    normaliseSpell,
    renderCard,
    CARD_CSS,
    buildCardCSS,
    buildHTML,
  };
}
