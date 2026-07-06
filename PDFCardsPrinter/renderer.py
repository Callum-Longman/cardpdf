import html as _html
import re


def esc(s):
    return _html.escape(str(s)) if s is not None else ""

def to_html(text):
    s = esc(text)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s.replace("\n\n", "<br><br>").replace("\n", "<br>")


def card_2014(spell):
    name      = esc(spell.get("name", ""))
    type_     = esc(spell.get("type", ""))
    cast_time = esc(spell.get("casting_time", ""))
    duration  = esc(spell.get("duration", ""))
    range_    = esc(spell.get("range", ""))
    ritual    = spell.get("ritual", False)
    comp      = spell.get("components", {})
    comp_raw  = esc(comp.get("raw", ""))
    desc      = to_html(spell.get("description", ""))
    higher    = spell.get("higher_levels", "")

    ritual_badge = '<span class="badge">Ritual</span>' if ritual else ""
    higher_html  = (f'<div class="extra"><em>At Higher Levels:</em> {esc(higher)}</div>'
                    if higher else "")
    return (
        f'<div class="card">'
        f'<div class="hdr"><span class="name">{name}</span>{ritual_badge}</div>'
        f'<div class="sub">{type_}</div>'
        f'<div class="meta">'
        f'<span><b>Cast:</b> {cast_time}</span><span><b>Range:</b> {range_}</span>'
        f'<span><b>Duration:</b> {duration}</span><span><b>Components:</b> {comp_raw}</span>'
        f'</div>'
        f'<div class="desc">{desc}</div>{higher_html}'
        f'</div>'
    )


def card_2024(spell):
    name     = esc(spell.get("name", ""))
    level    = spell.get("level", 0)
    lvl_str  = "Cantrip" if level == 0 else f"Level {level}"
    school   = esc(spell.get("school", "").capitalize())
    action   = esc(spell.get("actionType", ""))
    conc     = spell.get("concentration", False)
    ritual   = spell.get("ritual", False)
    range_   = esc(spell.get("range", ""))
    duration = esc(spell.get("duration", ""))
    comps    = spell.get("components", [])
    material = spell.get("material", "")
    comp_str = ", ".join(c.upper() for c in comps)
    if material:
        comp_str += f" ({material})"
    comp_str = esc(comp_str)
    desc     = to_html(spell.get("description", ""))
    upgrade  = spell.get("cantripUpgrade", "")

    badges = (
        ('<span class="badge">Conc.</span>' if conc else "") +
        ('<span class="badge">Ritual</span>' if ritual else "")
    )
    upgrade_html = (f'<div class="extra"><em>Upgrade:</em> {esc(upgrade)}</div>'
                    if upgrade else "")
    return (
        f'<div class="card">'
        f'<div class="hdr"><span class="name">{name}</span>{badges}</div>'
        f'<div class="sub">{lvl_str} · {school}</div>'
        f'<div class="meta">'
        f'<span><b>Action:</b> {action}</span><span><b>Range:</b> {range_}</span>'
        f'<span><b>Duration:</b> {duration}</span><span><b>Components:</b> {comp_str}</span>'
        f'</div>'
        f'<div class="desc">{desc}</div>{upgrade_html}'
        f'</div>'
    )


CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, serif; background: #bbb; }

@media print {
  @page { size: A4; margin: 8mm; }
  body  { background: white; }
  .page {
    box-shadow: none !important;
    margin: 0 !important;
    width: 194mm;
    height: 281mm;
    padding: 0;
    page-break-after: always;
  }
  .page:last-child { page-break-after: avoid; }
}

.page {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 2mm;
  width: 210mm;
  height: 297mm;
  padding: 8mm;
  margin: 14px auto;
  background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,.35);
}

.card {
  border: 0.5pt solid #444;
  border-radius: 2pt;
  padding: 2mm;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 1mm;
}
.card-empty { border: 0.5pt dashed #bbb; }

.hdr {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1mm;
  border-bottom: 0.5pt solid #555;
  padding-bottom: 1mm;
}
.name  { font-size: 7.5pt; font-weight: bold; line-height: 1.2; }
.badge {
  font-size: 5pt;
  background: #333;
  color: #fff;
  padding: .4mm 1mm;
  border-radius: 1pt;
  white-space: nowrap;
  flex-shrink: 0;
  align-self: center;
}
.sub  { font-size: 5.5pt; font-style: italic; color: #555; }
.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .3mm 2mm;
  font-size: 6pt;
}
.desc  { font-size: 5.5pt; line-height: 1.35; flex: 1; overflow: hidden; }
.extra {
  font-size: 5.5pt;
  font-style: italic;
  color: #444;
  border-top: .5pt solid #ccc;
  padding-top: 1mm;
  overflow: hidden;
}
"""


def build_html(selected):
    pages = [selected[i:i + 9] for i in range(0, len(selected), 9)]
    body = ""
    for page in pages:
        cards = "".join(
            card_2014(s) if src == "2014" else card_2024(s)
            for s, src in page
        )
        cards += '<div class="card card-empty"></div>' * (9 - len(page))
        body += f'<div class="page">{cards}</div>\n'
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<title>Spell Cards</title><style>{CSS}</style></head>'
        f'<body>{body}</body></html>'
    )
