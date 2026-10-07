# 微信正文生成

每篇文章只维护一份 Markdown 源稿。脚本默认在源稿旁边生成同名 HTML：
`dsh-just-chat.zh-CN.md` → `dsh-just-chat.zh-CN.html`。HTML 是可在浏览器中打开并复制的正文交付物，不是文章内容的维护入口。

```powershell
node scripts/render-wechat.mjs output/E-17-article/dsh-just-chat.zh-CN.md
```

也可以显式指定输出路径：

```powershell
node scripts/render-wechat.mjs path/to/article.md path/to/custom.html
```

打开生成的 `.html`，选中页面中的正文复制，再粘贴到公众号编辑器。源稿中的第一个一级标题用于 HTML 标题并从正文区域移除，文章标题单独填写；Markdown 图片会生成 `<img>` 和图注并保留在 HTML 中，若公众号不接受外部图片地址，再按图注位置手动上传替换。

样式集中在 [wechat-theme.mjs](wechat-theme.mjs)，正文沿用上一篇文章的 18px 字号、1.9 行距、23px 二级标题和红色引用边线。Markdown 中的链接会变成正文上标编号，网址列在文末。

脚本使用 website 已安装的 `markdown-it`，输出样式全部写在元素的 `style` 属性中。当前支持文章实际使用的段落、标题、引用、列表、代码、表格、图片图注和链接；不包含预览页、发布接口、素材上传或复杂检查。

## 给后续自动化的输入输出

后续自动化只需要让 AI 生成或修改一份 Markdown：正文用普通 Markdown，图片使用可访问的 URL，例如 `![界面截图](https://example.com/screenshot.png)`。随后让 AI 运行同一条命令，脚本按源稿文件名生成对应的 `.html`。因此流程固定为“AI 产出／修改 `.md` → AI 运行渲染脚本 → 人工打开 `.html` 复制正文”，文章内容不需要直接生成 HTML。

当前边界是图片地址处理：网络图片保留原 URL；源稿里的本地相对路径图片按源稿目录解析后以 base64 嵌入 HTML，输出文件移动到别处也能显示。脚本不会替 AI 上传图片到图床或公众号素材库；粘贴后编辑器是否保留嵌入图片，需要在公众号后台确认。后续需要全自动发布时，再单独增加图片上传和 URL 替换步骤。

源稿修改后重新运行命令即可更新同名 `.html`。同一目录可以放多篇文章，每篇只需保持自己的 `.md` 与生成的 `.html` 文件名对应。

## 公众号排版规范

样式遵循[公众号编辑器插件开发规范](https://developers.weixin.qq.com/doc/service/guide/product/plugin_spec.html)：不设置字体族（代码块只用通用的 `monospace`），行高大于字号（角标不单独设行高），宽度用百分比。正文各级元素显式写 `text-align:left`：浏览器复制时会把未设置的对齐方式写成非标准的 `text-align:start`，编辑器会因此提示。图表是带文字的图片，深色模式下不会被反色，发布前在手机深色模式里看一眼。
