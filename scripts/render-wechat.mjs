import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { styles } from './wechat-theme.mjs';

const require = createRequire(new URL('../website/package.json', import.meta.url));
const MarkdownIt = require('markdown-it');

export function renderWechat(source) {
  const md = new MarkdownIt({ html: false, linkify: false });
  const escape = md.utils.escapeHtml;
  const tokens = md.parse(source, {});
  const titleIndex = tokens.findIndex(token => token.type === 'heading_open' && token.tag === 'h1');
  const title = titleIndex >= 0 ? tokens[titleIndex + 1].content : '文章';

  if (titleIndex >= 0) tokens.splice(titleIndex, 3);

  const references = [];
  const images = [];
  let quoteDepth = 0;

  const addStyle = (token, style) => {
    const existing = token.attrGet('style');
    token.attrSet('style', existing ? `${existing};${style}` : style);
  };

  for (const token of tokens) {
    if (token.type === 'blockquote_open') quoteDepth++;
    if (token.nesting === 1 && styles[token.tag]) {
      addStyle(token, styles[token.tag]);
    }
    if (token.type === 'paragraph_open' && quoteDepth) {
      addStyle(token, styles.p.replace('margin:0 0 20px', 'margin:0 0 12px'));
    }
    if (token.type === 'blockquote_close') quoteDepth--;

    for (const child of token.children ?? []) {
      if (child.nesting === 1 && styles[child.tag]) {
        addStyle(child, styles[child.tag]);
      }
    }
  }

  const linkStack = [];
  md.renderer.rules.link_open = (tokens, index) => {
    const url = tokens[index].attrGet('href');
    let reference = references.indexOf(url);
    if (reference < 0) reference = references.push(url) - 1;
    linkStack.push(reference + 1);
    return '<span>';
  };
  md.renderer.rules.link_close = () => `</span><sup style="${styles.sup}">${linkStack.pop()}</sup>`;
  md.renderer.rules.code_inline = (tokens, index) => `<code style="${styles.code}">${escape(tokens[index].content)}</code>`;

  const codeBlock = (tokens, index) => (
    `<pre style="${styles.pre}"><code style="font-family:monospace;">${escape(tokens[index].content)}</code></pre>\n`
  );
  md.renderer.rules.fence = codeBlock;
  md.renderer.rules.code_block = codeBlock;

  md.renderer.rules.image = (tokens, index) => {
    const token = tokens[index];
    const src = token.attrGet('src');
    const alt = token.content;
    if (!images.some(image => image.src === src)) images.push({ src, alt });
    return `<img src="${escape(src)}" alt="${escape(alt)}" style="${styles.img}"><span style="${styles.caption}">${escape(alt)}</span>`;
  };

  const content = md.renderer.render(tokens, md.options, {});
  const refs = references
    .map((url, index) => `<p style="${styles.reference}">[${index + 1}] ${escape(url)}</p>`)
    .join('\n');
  const section = `<section style="${styles.section}">${content}${refs}</section>`;
  const body = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title></head><body style="margin:0;background:#fff;"><main style="box-sizing:border-box;max-width:680px;margin:0 auto;padding:28px 22px;">${section}</main></body></html>\n`;

  return { title, images, references, body };
}

const imageTypes = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml' };

// Local figures are embedded so the HTML still shows them when opened elsewhere or copied into an editor.
async function embedLocalImages(body, baseDir) {
  const sources = [...new Set([...body.matchAll(/<img src="([^"]+)"/g)].map(match => match[1]))]
    .filter(src => !/^(?:[a-z]+:|\/\/)/i.test(src));
  for (const src of sources) {
    const file = path.resolve(baseDir, src.replaceAll('&amp;', '&'));
    const type = imageTypes[path.extname(file).toLowerCase()];
    if (!type) continue;
    const data = (await readFile(file)).toString('base64');
    body = body.replaceAll(`<img src="${src}"`, `<img src="data:${type};base64,${data}"`);
  }
  return body;
}

export function outputPathFor(input) {
  const inputPath = path.resolve(input);
  const extension = path.extname(inputPath);
  return path.join(path.dirname(inputPath), `${path.basename(inputPath, extension)}.html`);
}

export async function writeWechat(input, outputFile = outputPathFor(input)) {
  const inputPath = path.resolve(input);
  const outputPath = path.resolve(outputFile);
  const result = renderWechat(await readFile(inputPath, 'utf8'));
  result.body = await embedLocalImages(result.body, path.dirname(inputPath));
  await mkdir(path.dirname(outputPath), { recursive: true });
  await writeFile(outputPath, result.body);
  console.log(JSON.stringify({ title: result.title, images: result.images.length, references: result.references.length, output: outputPath }));
  return { ...result, output: outputPath };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  if (!process.argv[2]) {
    throw new Error('Usage: node scripts/render-wechat.mjs <source.md> [output.html]');
  }
  await writeWechat(process.argv[2], process.argv[3]);
}
