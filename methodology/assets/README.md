# Publication figures

The [Chinese formal paper](../introducing-red.md) and [English formal paper](../introducing-red.en.md) use the same three figures with localized labels. The [Chinese public-account article](../introducing-red.wechat.md) uses the vertically arranged knowledge-state figure for mobile reading. A mobile case illustration is also available for expanded editions.

| Figure | Formal-paper files | Public-account files |
|---|---|---|
| Knowledge states | `red-states.zh.*`, `red-states.en.*` (Figure 1) | `red-states.wechat.*` (Figure 1) |
| Routing and decision checkpoints | `red-transitions.zh.*`, `red-transitions.en.*` (Figure 2) | `red-transitions.wechat.*` (Figure 2) |
| CSV date-export example | `red-example.zh.*`, `red-example.en.*` (Figure 3) | `red-example.wechat.*` (optional case illustration) |

Each name has an SVG and a PNG file. SVG provides scalable text and geometry; PNG is the portable delivery copy. Formal papers embed SVG and link to PNG fallbacks. The public-account draft marks its image position with an editorial HTML comment; insert the PNG using the platform editor. Surrounding prose explains the same relationships for readers unable to load images.

## Editing and export

Edit the public-account transitions drawing in [red-transitions.wechat.svg](../../scripts/assets/red-transitions.wechat.svg); edit the other drawings in [render_methodology_figures.py](../../scripts/render_methodology_figures.py). Regenerate both formats from the repository root:

```sh
python scripts/render_methodology_figures.py
```

The script uses Python's standard library to author explicit SVG elements and the installed ImageMagick SVG renderer to export PNGs at 144 DPI (1.5 times the SVG pixel dimensions) for the generated drawings. The public-account transitions template exports at its native 1080 × 1500 dimensions. It requires `magick` on PATH and Microsoft YaHei for Chinese and Latin labels. An alternative installed font can be selected with `--font "Font Name"`; inspect wrapping and text fit after changing it. The SVG viewer also needs a suitable font; the exported PNG preserves the rendered text independently of the reader's fonts.

Keep labels and layout synchronized between the two formal-paper languages. Check arrows against Protocol 1, and visually inspect the exported images after editing. R, E, and D have textual labels as well as distinct colors. Arrowheads are explicit geometry, and the SVGs contain titles and descriptions.

## Preparing the public-account article

Use `red-states.wechat.png` at full article width. It is 1080 pixels wide and arranged vertically for phone reading. Upload it through the publishing editor at the image position in the article. `red-transitions.wechat.png` follows the paragraph explaining how the documents drive the next action; it is 1080 × 1500 pixels, with vertically arranged question-led cards and two highlighted decision checkpoints. The optional `red-example.wechat.png` has the same width. Preview the finished article on a phone, since the editor may resize images or change spacing.

The public-account draft uses absolute HTTPS URLs for all reader-facing links. Its full-article link points to the Chinese methodology article at `https://blog.e10t.net/red/`, with an English language switch. Before publishing, deploy the reviewed website and check that the desired revision is available at that public URL; local branch edits do not update it. The project homepage link points to `https://github.com/exoticknight/red`.

At the editorial image comment, upload `red-states.wechat.png` from this asset directory through the WeChat public-account editor and insert the uploaded image there. Use the platform-provided image address if preparing HTML. Remove the editorial comment when the image is in place. The author or an authorized assistant can do this during platform layout. No platform upload has been performed and no hosted image URL is assigned yet.

Check the finished draft for leftover upload comments, local paths, and relative links before publication. Open its links and preview the inserted image in the platform draft.
