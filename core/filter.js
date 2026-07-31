// Shared filtering logic for both web and local app

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}

function lvlKey(spell, year) {
  if (year === "2014") {
    const lv = (spell.level||"").toString().toLowerCase();
    return lv === "cantrip" ? "cantrip" : lv;
  }
  const lv = spell.level ?? 0;
  return lv === 0 ? "cantrip" : String(lv);
}

function applyFilter(allSpells, criteria) {
  const {source, level, school, dndClass, searchText} = criteria;
  const lvl = (level || "all").toLowerCase();
  const sch = (school || "all").toLowerCase();
  const cls = (dndClass || "all").toLowerCase();
  const q = (searchText || "").toLowerCase();

  return allSpells.filter(({spell, year}) => {
    if (source !== "All" && year !== source) return false;
    if (lvl !== "all") {
      const lk = lvlKey(spell, year);
      if (lk !== lvl) return false;
    }
    if (sch !== "all" && (spell.school||"").toLowerCase() !== sch) return false;
    if (cls !== "all" && !(spell.classes||[]).map(c=>c.toLowerCase()).includes(cls)) return false;
    if (q && !(spell.name||"").toLowerCase().includes(q)) return false;
    return true;
  });
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    capitalize,
    lvlKey,
    applyFilter,
  };
}
