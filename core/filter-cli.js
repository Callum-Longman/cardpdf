#!/usr/bin/env node
// CLI entry point for local app to filter spells
// Usage: node filter-cli.js <spells-json> <criteria-json>

const fs = require('fs');
const { applyFilter } = require('./filter.js');

const spellsJson = process.argv[2];
const criteriaJson = process.argv[3];

try {
  const allSpells = JSON.parse(fs.readFileSync(spellsJson, 'utf-8'));
  const criteria = JSON.parse(criteriaJson);
  const filtered = applyFilter(allSpells, criteria);
  console.log(JSON.stringify(filtered));
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
