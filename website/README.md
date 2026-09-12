# RED article site

The bilingual RED methodology article for GitHub Pages. The build uses `markdown-it` to render `methodology/introducing-red.md` and `methodology/introducing-red.en.md`; edit those files to change article content. Site presentation lives in `build.mjs` and `style.css`. The separately maintained WeChat introduction links to the site's Chinese article.

## Preview

With Node.js 22.12 or newer, from `website/`:

```sh
npm ci
npm run build
npm run preview
```

Open `http://localhost:4173`. Generated files are in the ignored `website/dist/` directory; `index.html` can also be opened directly for offline review. Assets and navigation are relative so the same output works under the repository URL prefix.

## GitHub Pages

Choose **Settings → Pages → Build and deployment → GitHub Actions** in the repository. After the reviewed changes reach `main`, the Article site workflow builds and deploys the site. Pull requests build the site without deploying. A manual workflow run deploys only when run against `main`.

Default public URL: `https://exoticknight.github.io/red/`. Set repository Actions variable `RED_SITE_URL` to the full public base URL if using a different address or custom domain; this controls canonical, alternate-language, sitemap and social metadata URLs. Configure any custom domain separately in GitHub Pages settings. Locally, the equivalent environment variable is `SITE_URL`.

Routes:

- `index.html`: complete Chinese article (site homepage)
- `introducing-red.en.html`: complete English article

Figures open at full size when clicked. Readers need no JavaScript, remote fonts or external rendering service.
