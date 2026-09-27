import { readFile, writeFile, mkdir, readdir, copyFile, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import MarkdownIt from 'markdown-it';

const root = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(root, '../methodology');
const out = path.join(root, 'dist');
const origin = new URL(process.env.SITE_URL || 'https://blog.e10t.net/red/');
if (!origin.pathname.endsWith('/')) origin.pathname += '/';
const md = new MarkdownIt({ html: false, linkify: true });
const esc = md.utils.escapeHtml;
// Each page's `date` is its editorial publication date, not a build timestamp.
const publication = {
  author: { name: 'exoticknight', url: 'https://github.com/exoticknight' },
};
const pageUrl = page => new URL(page.url === 'index.html' ? './' : page.url, origin).href;
const pages = [
  { file: 'introducing-red.md', url: 'index.html', lang: 'zh-CN', label: '中文', group: 'methodology', category: 'what-is-red', kind: 'RED 是什么', date: '2026-09-12', description: 'Research、Evolve、Document：按知识状态组织项目内容，让 AI 持续理解项目，并把讨论、实施与接受的共识连接起来。', socialImage: 'assets/red-states.zh.png', socialImageAlt: 'RED：Research、Evolve、Document 的内容与用途' },
  { file: 'introducing-red.en.md', url: 'introducing-red.en.html', lang: 'en', label: 'English', group: 'methodology', category: 'what-is-red', kind: 'WHAT IS RED', date: '2026-09-12', description: 'Research, Evolve, Document: a methodology for helping AI sustain an accurate understanding of a project as it changes.', socialImage: 'assets/red-states.en.png', socialImageAlt: 'RED: Research, Evolve and Document — their content and uses' },
  { file: 'try-red.md', url: 'try-red.html', lang: 'zh-CN', label: '中文', group: 'introduction', category: 'getting-started', kind: '上手', date: '2026-09-12', description: '和 AI 把想法做成项目：从一次报表改动开始，认识 Research、Evolve、Document 如何让协作接得上。', socialImage: 'assets/red-states.zh.png', socialImageAlt: 'RED：Research、Evolve、Document 的内容与用途' },
  { file: 'try-red.en.md', url: 'try-red.en.html', lang: 'en', label: 'English', group: 'introduction', category: 'getting-started', kind: 'GETTING STARTED', date: '2026-09-12', description: 'Turn an idea into a project with AI while keeping research, changes, and accepted understanding distinct.', socialImage: 'assets/red-states.en.png', socialImageAlt: 'RED: Research, Evolve and Document — their content and uses' },
  { file: 'dsh-just-chat.md', url: 'dsh-just-chat.html', lang: 'zh-CN', label: '中文', group: 'practical', category: 'in-practice', kind: '实战', date: '2026-09-17', description: '用 AI 把一个想法做成能用的 DSH 插件：两轮开发中，RED 怎样让研究、推进和确认接得起来。', socialImage: 'https://raw.githubusercontent.com/exoticknight/dsh-just-chat/v0.1.4/docs/images/quick-chat-head.jpg', socialImageAlt: 'DSH 快速对话插件的首页和侧栏入口' },
  { file: 'dsh-just-chat.en.md', url: 'dsh-just-chat.en.html', lang: 'en', label: 'English', group: 'practical', category: 'in-practice', kind: 'IN PRACTICE', date: '2026-09-17', description: 'From a rough idea to a usable DSH plugin: two development rounds shaped by Research, Evolve, and Document.', socialImage: 'https://raw.githubusercontent.com/exoticknight/dsh-just-chat/v0.1.4/docs/images/quick-chat-head.jpg', socialImageAlt: 'Quick-chat entries on the DSH home page and in the sidebar' },
  { file: 'frontier-and-budget-models.md', url: 'frontier-and-budget-models.html', lang: 'zh-CN', label: '中文', group: 'frontier-and-budget-models', category: 'in-practice', kind: '实战', date: '2026-09-27', description: '七个项目、一个多月：顶级模型负责开局、重大功能和审查，低价模型负责日常开发，RED 让便宜模型长期接得住，开发成本省了八成。', socialImage: 'assets/frontier-and-budget-models-cost.zh.png', socialImageAlt: '全用顶级模型与高低搭配的成本对比' },
  { file: 'frontier-and-budget-models.en.md', url: 'frontier-and-budget-models.en.html', lang: 'en', label: 'English', group: 'frontier-and-budget-models', category: 'in-practice', kind: 'IN PRACTICE', date: '2026-09-27', description: 'Seven projects over a month: frontier models for kickoff, major features and review, budget models for everyday work, with RED keeping the handoff intact. Costs fell 80%.', socialImage: 'assets/frontier-and-budget-models-cost.en.png', socialImageAlt: 'Cost of running everything on frontier models versus mixing in budget models' },
];
const languagePages = page => pages.filter(candidate => candidate.group === page.group);
// Read every title first so each page can link to the others by their article titles.
for (const page of pages) {
  const heading = (await readFile(path.join(source, page.file), 'utf8')).match(/^#\s+(.+)$/m);
  if (!heading) throw new Error(`Missing h1 in ${page.file}`);
  page.title = heading[1].trim();
}
const categories = [...new Set(pages.map(p => p.category))];
// Read next lists the other articles under their category, keeping each article's language versions together.
const readNext = page => categories.map(category => {
  const groups = [...new Set(pages.filter(p => p.category === category && p.group !== page.group).map(p => p.group))];
  if (!groups.length) return '';
  const heading = (pages.find(p => p.category === category && p.lang === page.lang) || pages.find(p => p.category === category)).kind;
  const articles = groups.map(group => {
    const members = pages.filter(p => p.group === group).sort((x, y) => (y.lang === page.lang) - (x.lang === page.lang));
    return `<div class="next-article">${members.map(p => `<a href="${p.url}" lang="${p.lang}"><span class="lang-tag">${p.lang === 'en' ? 'EN' : '中文'}</span><span class="next-title">${esc(p.title)}</span><span aria-hidden="true">↗</span></a>`).join('')}</div>`;
  }).join('');
  return `<div class="next-group"><p class="next-kind">${esc(heading)}</p>${articles}</div>`;
}).join('');
// This dedicated generated directory must not retain pages or assets removed from the site.
if (out !== path.resolve(root, 'dist')) throw new Error('Unexpected output directory');
await rm(out, { recursive: true, force: true });
await mkdir(path.join(out, 'assets'), { recursive: true });
for (const file of await readdir(path.join(source, 'assets'))) {
  if (/\.(zh|en|wechat)\.(svg|png)$/.test(file)) await copyFile(path.join(source, 'assets', file), path.join(out, 'assets', file));
}
await copyFile(path.join(root, 'style.css'), path.join(out, 'style.css'));
for (const file of ['favicon.svg', 'favicon.png']) {
  await copyFile(path.join(root, 'assets', file), path.join(out, file));
}
await writeFile(path.join(out, '.nojekyll'), '');

for (const page of pages) {
  const english = page.lang === 'en';
  const content = (await readFile(path.join(source, page.file), 'utf8')).replace(/<!--[\s\S]*?-->/g, '').trimStart();
  const tokens = md.parse(content, {});
  const titleIndex = tokens.findIndex(token => token.type === 'heading_open' && token.tag === 'h1');
  if (titleIndex < 0) throw new Error(`Missing h1 in ${page.file}`);
  const title = tokens[titleIndex + 1].content;
  tokens.splice(titleIndex, 3);
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
  const canonical = pageUrl(page);
  const imageUrl = /^https?:\/\//.test(page.socialImage) ? page.socialImage : new URL(page.socialImage, origin).href;
  const imageAlt = page.socialImageAlt;
  const publishedLabel = new Intl.DateTimeFormat(page.lang, { dateStyle: 'long', timeZone: 'UTC' }).format(new Date(page.date));
  const minutes = english ? Math.ceil(content.split(/\s+/).length / 220) : Math.ceil(content.replace(/\s/g, '').length / 450);
  const pair = languagePages(page);
  const defaultPage = pair.find(p => p.lang === 'zh-CN') || pair[0];
  const alternatePage = pair.find(p => p.lang !== page.lang);
  const alternates = pair.map(p => `<link rel="alternate" hreflang="${p.lang}" href="${esc(pageUrl(p))}">`).join('');
  const articleData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    '@id': `${canonical}#article`,
    headline: title,
    description: page.description,
    inLanguage: page.lang,
    url: canonical,
    mainEntityOfPage: canonical,
    author: { '@type': 'Person', ...publication.author },
    datePublished: page.date,
    image: [imageUrl],
    isPartOf: { '@type': 'WebSite', name: 'RED', url: origin.href },
  };
  const html = `<!doctype html>
<html lang="${page.lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · RED</title><meta name="description" content="${esc(page.description)}">
<meta name="author" content="${esc(publication.author.name)}">
<link rel="canonical" href="${esc(canonical)}">${alternates}<link rel="alternate" hreflang="x-default" href="${esc(pageUrl(defaultPage))}">
<meta property="og:type" content="article"><meta property="og:site_name" content="RED"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(page.description)}"><meta property="og:url" content="${esc(canonical)}"><meta property="og:image" content="${esc(imageUrl)}"><meta property="og:image:alt" content="${esc(imageAlt)}"><meta property="og:locale" content="${english ? 'en_US' : 'zh_CN'}"><meta property="og:locale:alternate" content="${alternatePage ? (alternatePage.lang === 'en' ? 'en_US' : 'zh_CN') : (english ? 'zh_CN' : 'en_US')}"><meta property="article:published_time" content="${page.date}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(title)}"><meta name="twitter:description" content="${esc(page.description)}"><meta name="twitter:image" content="${esc(imageUrl)}"><meta name="twitter:image:alt" content="${esc(imageAlt)}">
<script type="application/ld+json">${JSON.stringify(articleData).replace(/</g, '\\u003c')}</script>
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#f8f7f3" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#181c1a" media="(prefers-color-scheme: dark)"><link rel="icon" href="favicon.png" type="image/png" sizes="64x64"><link rel="icon" href="favicon.svg" type="image/svg+xml" sizes="any"><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#article">${english ? 'Skip to article' : '跳到正文'}</a>
<header class="site-header"><a class="brand" href="index.html" aria-label="${english ? 'RED home' : 'RED 首页'}">RED<span class="brand-dot">.</span></a><nav aria-label="${english ? 'Language' : '语言'}">${pair.map(p => `<a href="${p.url}" lang="${p.lang}"${p.url === page.url ? ' aria-current="page"' : ''}>${p.label}</a>`).join('')}<a class="repo" href="https://github.com/exoticknight/red">GitHub <span aria-hidden="true">↗</span></a></nav></header>
<main id="article"><div class="article-heading"><div class="eyebrow"><span>${/RED/.test(page.kind) ? page.kind : `RED / ${page.kind}`}</span><span>${minutes} ${english ? 'MIN READ' : '分钟阅读'}</span></div><h1>${esc(title)}</h1><p class="dek">${esc(page.description)}</p><p class="byline"><a rel="author" href="${esc(publication.author.url)}">${esc(publication.author.name)}</a><span>${english ? 'Published' : '发布于'} <time datetime="${page.date}">${esc(publishedLabel)}</time></span></p><div class="principles"><span><b>R</b> Research</span><span><b>E</b> Evolve</span><span><b>D</b> Document</span></div></div>
<div class="reading-layout"><aside><details open><summary>${english ? 'IN THIS ARTICLE' : '本文目录'}</summary><nav aria-label="${english ? 'Table of contents' : '目录'}"><ol>${toc.join('')}</ol></nav></details></aside><div><article>${body}</article><section class="read-next"><p class="eyebrow">${english ? 'CONTINUE EXPLORING' : '继续阅读与实践'}</p>${readNext(page)}<a href="https://github.com/exoticknight/red">${english ? 'Try RED on your project' : '在你的项目里试试 RED'} <span aria-hidden="true">↗</span></a></section></div></div></main>
<footer><a class="brand" href="index.html">RED<span class="brand-dot">.</span></a><span>Research · Evolve · Document</span><a href="https://github.com/exoticknight/red">${english ? 'Open-source project' : '开源项目'} ↗</a></footer></body></html>`;
  await writeFile(path.join(out, page.url), html);
  console.log(`Built ${page.url} (${toc.length} sections)`);
}
await writeFile(path.join(out, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${pages.map(p => `<url><loc>${esc(pageUrl(p))}</loc></url>`).join('')}</urlset>`);
