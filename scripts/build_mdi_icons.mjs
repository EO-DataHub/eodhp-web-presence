#!/usr/bin/env node
// Extract each MDI icon's path-`d` attribute into a single JSON lookup
// consumed by the template-time renderer (eodhp_web_presence/home/icons.py).

import { readdirSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const svgDir = join(repoRoot, "node_modules", "@mdi", "svg", "svg");
const pkgPath = join(repoRoot, "node_modules", "@mdi", "svg", "package.json");

const outPath = process.argv[2];
if (!outPath) {
  console.error("Usage: build_mdi_icons.mjs <output.json>");
  process.exit(1);
}

const SHAPE = /^<svg[^>]*viewBox="0 0 24 24"[^>]*><path d="([^"]+)"\s*\/><\/svg>\s*$/;
const NAME = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const { version } = JSON.parse(readFileSync(pkgPath, "utf8"));

const icons = {};
let skipped = 0;
for (const file of readdirSync(svgDir)) {
  if (!file.endsWith(".svg")) continue;
  const name = file.slice(0, -4);
  if (!NAME.test(name)) {
    skipped++;
    continue;
  }
  const body = readFileSync(join(svgDir, file), "utf8").trim();
  const m = body.match(SHAPE);
  if (!m) {
    skipped++;
    continue;
  }
  icons[name] = m[1];
}

mkdirSync(dirname(resolve(outPath)), { recursive: true });
writeFileSync(outPath, JSON.stringify({ _version: version, _viewBox: "0 0 24 24", icons }) + "\n");

console.log(
  `build_mdi_icons: wrote ${Object.keys(icons).length} icons to ${outPath}` +
    (skipped ? ` (skipped ${skipped})` : ""),
);