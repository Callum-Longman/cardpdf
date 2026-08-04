#!/usr/bin/env node
// CLI entry point for Python to call
// Usage: node render-cli.js <spells-json> <border-base64-or-empty> [padding-mm] [font-size-pt] > output.html

const fs = require('fs');
const { buildHTML } = require('./core/render.js');

const spellsJson = process.argv[2];
const borderArg = process.argv[3] || '';
const paddingMm = process.argv[4] || '';
const fontSizePt = process.argv[5] || '';

try {
  const selected = JSON.parse(fs.readFileSync(spellsJson, 'utf-8'));
  const html = buildHTML(selected, borderArg, paddingMm, fontSizePt);
  console.log(html);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
