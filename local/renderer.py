import json
import subprocess
import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR.parent / "core"
DOCS_DIR = BASE_DIR.parent / "docs"
RENDER_CLI = DOCS_DIR / "render-cli.js"


def build_html(selected_spells, border_image_path: str):
    """
    Render HTML using the shared JavaScript render.js.
    selected_spells: list of (spell_dict, year_str) tuples
    border_image_path: file path to image, or empty string
    """
    # Convert to format expected by render-cli.js
    selected = [{"spell": spell, "year": year} for spell, year in selected_spells]

    # Prepare border as base64 data URL
    border_data = ""
    if border_image_path:
        with open(border_image_path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode()
            # Determine MIME type
            ext = Path(border_image_path).suffix.lower()
            mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}.get(ext, 'image/png')
            border_data = f"data:{mime};base64,{base64_data}"

    # Write temp file with selected spells
    temp_spells = BASE_DIR / ".temp_selected.json"
    with open(temp_spells, 'w', encoding='utf-8') as f:
        json.dump(selected, f)

    try:
        # Call render-cli.js from docs
        result = subprocess.run(
            ['node', str(RENDER_CLI), str(temp_spells), border_data],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    finally:
        temp_spells.unlink(missing_ok=True)
