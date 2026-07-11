import html as _html
import re


def esc(s):
    return _html.escape(str(s)) if s is not None else ""

def to_html(text):
    s = esc(text)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s.replace("\n\n", "<br><br>").replace("\n", "<br>")


def normalise_spell(spell, edition="2024"):
    """Convert any spell format to a standard internal format."""
    if edition == "2014":
        return {
            "name": spell.get("name", ""),
            "type": spell.get("type", ""),
            "level": None,  # 2014 doesn't have explicit levels
            "school": None,
            "action": spell.get("casting_time", ""),
            "concentration": False,
            "ritual": spell.get("ritual", False),
            "range": spell.get("range", ""),
            "duration": spell.get("duration", ""),
            "components": spell.get("components", {}).get("raw", ""),
            "description": spell.get("description", ""),
            "extra_text": spell.get("higher_levels", ""),
            "extra_label": "At Higher Levels",
        }
    else:  # 2024
        comps = spell.get("components", [])
        material = spell.get("material", "")
        comp_str = ", ".join(c.upper() for c in comps)
        if material:
            comp_str += f" ({material})"

        level = spell.get("level", 0)
        return {
            "name": spell.get("name", ""),
            "type": f"{'Cantrip' if level == 0 else f'Level {level}'} · {spell.get('school', '').capitalize()}",
            "level": level,
            "school": spell.get("school", ""),
            "action": spell.get("actionType", ""),
            "concentration": spell.get("concentration", False),
            "ritual": spell.get("ritual", False),
            "range": spell.get("range", ""),
            "duration": spell.get("duration", ""),
            "components": comp_str,
            "description": spell.get("description", ""),
            "extra_text": spell.get("cantripUpgrade", ""),
            "extra_label": "Upgrade",
        }
import base64

def load_border_image(image_path):
    """Convert image file to base64."""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def render_card(normalized_spell, border_image):
    """Single rendering function with optional custom border."""
    name = esc(normalized_spell["name"])
    type_ = esc(normalized_spell["type"])
    action = esc(normalized_spell["action"])
    range_ = esc(normalized_spell["range"])
    duration = esc(normalized_spell["duration"])
    components = esc(normalized_spell["components"])
    desc = to_html(normalized_spell["description"])

    badges = (
            ('<span class="badge">Conc.</span>' if normalized_spell["concentration"] else "") +
            ('<span class="badge">Ritual</span>' if normalized_spell["ritual"] else "")
    )

    extra_html = ""
    if normalized_spell["extra_text"]:
        extra_label = normalized_spell["extra_label"]
        extra_html = f'<div class="extra"><em>{extra_label}:</em> {esc(normalized_spell["extra_text"])}</div>'

    border_style = f'style="background-image: url(data:image/png;base64,{border_image})"' if border_image else ''

    return (
        f'<div class="card" {border_style}>'
        f'<div class="card-content">'
        f'<div class="hdr"><span class="name">{name}</span>{badges}</div>'
        f'<div class="sub">{type_}</div>'
        f'<div class="meta">'
        f'<span><b>Action:</b> {action}</span><span><b>Range:</b> {range_}</span>'
        f'<span><b>Duration:</b> {duration}</span><span><b>Components:</b> {components}</span>'
        f'</div>'
        f'<div class="desc">{desc}</div>{extra_html}'
        f'</div>'
        f'</div>'
    )


# Usage:
def card_html(border_image_path: str, spell, edition="2024"):
    normalised = normalise_spell(spell, edition)
    return render_card(normalised, load_border_image(border_image_path))


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
  border: none;
  border-radius: 0;  /* if using PNG with sharp corners */
  padding: 0;
  background-size: 100% 100%;
  background-position: 0 0;
  background-repeat: no-repeat;
  display: flex;
  flex-direction: column;
  gap: 1mm;
  overflow: hidden;
}

.card-content {
  padding: 2mm;  /* space inside the border frame */
  flex: 1;
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


def build_html(selected_spells, border_image_path: str):
    pages = [selected_spells[i:i + 9] for i in range(0, len(selected_spells), 9)]
    body = ""
    for page in pages:
        cards = "".join(
            card_html(border_image_path, s, src)
            for s, src in page
        )
        cards += '<div class="card card-empty"></div>' * (9 - len(page))
        body += f'<div class="page">{cards}</div>\n'
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<title>Spell Cards</title><style>{CSS}</style></head>'
        f'<body>{body}</body></html>'
    )
