import { readFile, writeFile, mkdir, readdir, copyFile, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import MarkdownIt from 'markdown-it';

const root = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(root, '../methodology');
const out = path.join(root, 'dist');
const origin = new URL(process.env.SITE_URL || 'https://exoticknight.github.io/red/');
if (!origin.pathname.endsWith('/')) origin.pathname += '/';
const md = new MarkdownIt({ html: false, linkify: true });
const esc = md.utils.escapeHtml;
const pages = [
  { file: 'introducing-red.md', url: 'index.html', lang: 'zh-CN', label: '中文', kind: '方法论', description: 'Research、Evolve、Document：按知识状态组织项目内容，让 AI 持续理解项目，并把讨论、实施与接受的共识连接起来。' },
  { file: 'introducing-red.en.md', url: 'introducing-red.en.html', lang: 'en', label: 'English', kind: 'METHODOLOGY', description: 'Research, Evolve, Document: a methodology for helping AI sustain an accurate understanding of a project as it changes.' },
];
// This dedicated generated directory must not retain pages or assets removed from the site.
if (out !== path.resolve(root, 'dist')) throw new Error('Unexpected output directory');
await rm(out, { recursive: true, force: true });
await mkdir(path.join(out, 'assets'), { recursive: true });
for (const file of await readdir(path.join(source, 'assets'))) {
  if (/\.(zh|en)\.(svg|png)$/.test(file)) await copyFile(path.join(source, 'assets', file), path.join(out, 'assets', file));
}
await copyFile(path.join(root, 'style.css'), path.join(out, 'style.css'));
await writeFile(path.join(out, '.nojekyll'), '');

for (const page of pages) {
  const english = page.lang === 'en';
  const content = await readFile(path.join(source, page.file), 'utf8');
  const tokens = md.parse(content, {});
  const title = tokens[1].content;
  tokens.splice(0, 3);
  const toc = [];
  const used = new Map();
  tokens.forEach((token, i) => {
    if (token.type !== 'heading_open') return;
    const label = tokens[i + 1].content;
    const slug = label.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '');
    const count = (used.get(slug) || 0) + 1;
    used.set(slug, count);
    const id = `${slug}${count > 1 ? `-${count}` : ''}`;
    token.attrSet('id', id);
    if (token.tag === 'h2') toc.push(`<li><a href="#${esc(id)}">${esc(label.replace(/^(?:\d+\.\s*|[一二三四五六七八九十]+、)/, ''))}</a></li>`);
  });
  const originalImage = md.renderer.rules.image;
  md.renderer.rules.image = (t, i, options, env, self) => {
    t[i].attrSet('loading', 'lazy');
    t[i].attrSet('decoding', 'async');
    return `<a class="figure-link" href="${esc(t[i].attrGet('src'))}" aria-label="${english ? 'Open full-size figure' : '查看完整尺寸图片'}">${originalImage(t, i, options, env, self)}</a>`;
  };
  const body = md.renderer.render(tokens, md.options, {});
  md.renderer.rules.image = originalImage;
  const canonical = new URL(page.url === 'index.html' ? './' : page.url, origin).href;
  const minutes = english ? Math.ceil(content.split(/\s+/).length / 220) : Math.ceil(content.replace(/\s/g, '').length / 450);
  const alternates = pages.map(p => `<link rel="alternate" hreflang="${p.lang}" href="${new URL(p.url === 'index.html' ? './' : p.url, origin).href}">`).join('');
  const html = `<!doctype html>
<html lang="${page.lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · RED</title><meta name="description" content="${esc(page.description)}">
<link rel="canonical" href="${canonical}">${alternates}<meta property="og:type" content="article"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(page.description)}"><meta property="og:url" content="${canonical}"><meta property="og:image" content="${new URL('assets/red-states.' + (english ? 'en' : 'zh') + '.png', origin).href}">
<meta name="theme-color" content="#f8f7f3"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#article">${english ? 'Skip to article' : '跳到正文'}</a>
<header class="site-header"><a class="brand" href="index.html" aria-label="${english ? 'RED home' : 'RED 首页'}">RED<span class="brand-dot">.</span></a><nav aria-label="${english ? 'Language' : '语言'}">${pages.map(p => `<a href="${p.url}" lang="${p.lang}"${p.url === page.url ? ' aria-current="page"' : ''}>${p.label}</a>`).join('')}<a class="repo" href="https://github.com/exoticknight/red">GitHub <span aria-hidden="true">↗</span></a></nav></header>
<main id="article"><div class="article-heading"><div class="eyebrow"><span>RED / ${page.kind}</span><span>${minutes} ${english ? 'MIN READ' : '分钟阅读'}</span></div><h1>${esc(title)}</h1><p class="dek">${esc(page.description)}</p><div class="principles"><span><b>R</b> Research</span><span><b>E</b> Evolve</span><span><b>D</b> Document</span></div></div>
<div class="reading-layout"><aside><details open><summary>${english ? 'IN THIS ARTICLE' : '本文目录'}</summary><nav aria-label="${english ? 'Table of contents' : '目录'}"><ol>${toc.join('')}</ol></nav></details></aside><div><article>${body}</article><section class="read-next"><p class="eyebrow">${english ? 'CONTINUE EXPLORING' : '继续阅读与实践'}</p>${pages.filter(p => p !== page).map(p => `<a href="${p.url}">${p.label} <span aria-hidden="true">↗</span></a>`).join('')}<a href="https://github.com/exoticknight/red">${english ? 'Try RED on your project' : '在你的项目里试试 RED'} <span aria-hidden="true">↗</span></a></section></div></div></main>
<footer><a class="brand" href="index.html">RED<span class="brand-dot">.</span></a><span>Research · Evolve · Document</span><a href="https://github.com/exoticknight/red">${english ? 'Open-source project' : '开源项目'} ↗</a></footer></body></html>`;
  await writeFile(path.join(out, page.url), html);
  console.log(`Built ${page.url} (${toc.length} sections)`);
}
await writeFile(path.join(out, 'favicon.svg'), '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#ac302b"/><text x="32" y="46" text-anchor="middle" fill="white" font-family="sans-serif" font-size="46" font-weight="700">R</text></svg>');
await writeFile(path.join(out, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${pages.map(p => `<url><loc>${esc(new URL(p.url === 'index.html' ? './' : p.url, origin).href)}</loc></url>`).join('')}</urlset>`);
