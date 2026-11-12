#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SKIP_SCHEMES = /^(?:https?:|mailto:|tel:|javascript:|data:|blob:|#)/i;

function walk(dir, results = []) {
  if (!fs.existsSync(dir)) return results;
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (item.name === '.git' || item.name === 'node_modules' || item.name === 'drafts') continue;
    const full = path.join(dir, item.name);
    if (item.isDirectory()) walk(full, results);
    else if (item.isFile() && /\.html?$/i.test(item.name)) results.push(full);
  }
  return results;
}

function extractLocalTargets(html) {
  const targets = [];
  const attr = /\b(?:href|src|poster)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>\x60]+))/gi;
  for (const match of html.matchAll(attr)) {
    const value = (match[1] ?? match[2] ?? match[3] ?? '').trim();
    if (!value || SKIP_SCHEMES.test(value) || value.startsWith('//')) continue;
    targets.push(value);
  }
  return targets;
}

function targetExists(sourceFile, rawTarget, rootDir = process.cwd()) {
  let pathname = rawTarget.split('#', 1)[0].split('?', 1)[0];
  if (!pathname) return true;
  try { pathname = decodeURIComponent(pathname); } catch { return false; }
  const candidate = pathname.startsWith('/')
    ? path.resolve(rootDir, `.${pathname}`)
    : path.resolve(path.dirname(sourceFile), pathname);
  if (!candidate.startsWith(path.resolve(rootDir) + path.sep) &&
      candidate !== path.resolve(rootDir)) return false;
  try {
    const stat = fs.statSync(candidate);
    return stat.isFile() || (stat.isDirectory() && fs.existsSync(path.join(candidate, 'index.html')));
  } catch {
    return false;
  }
}

export function findBrokenLinks(rootDir, boundaryDir = rootDir) {
  const root = path.resolve(rootDir);
  const boundary = path.resolve(boundaryDir);
  const broken = [];
  for (const file of walk(root)) {
    const html = fs.readFileSync(file, 'utf8');
    for (const target of extractLocalTargets(html)) {
      if (!targetExists(file, target, boundary)) broken.push({ file, target });
    }
  }
  return broken;
}

function run() {
  const args = process.argv.slice(2);
  const strict = args.includes('--strict');
  const paths = args.filter(arg => arg !== '--strict');
  const root = process.cwd();
  const targets = paths.length ? paths : ['manuals'];
  const broken = targets.flatMap(target => {
    const absolute = path.resolve(root, target);
    if (!absolute.startsWith(root + path.sep) && absolute !== root) {
      console.error(`Skipping path outside repository: ${target}`);
      return [];
    }
    if (!fs.existsSync(absolute)) {
      console.error(`Missing scan path: ${target}`);
      return [{ file: absolute, target: '(scan path does not exist)' }];
    }
    const stat = fs.statSync(absolute);
    if (stat.isFile()) {
      const html = fs.readFileSync(absolute, 'utf8');
      return extractLocalTargets(html).filter(t => !targetExists(absolute, t, root)).map(t => ({file:absolute,target:t}));
    }
    return findBrokenLinks(absolute, root);
  });

  if (broken.length) {
    console.log(`Found ${broken.length} broken local link/asset reference(s):`);
    for (const item of broken) console.log(`- ${path.relative(root, item.file)} -> ${item.target}`);
    if (strict) process.exitCode = 1;
    else console.log('Report-only mode: use --strict to make these findings fail the command.');
  } else {
    console.log('No broken local links/assets found in the scanned HTML.');
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) run();
