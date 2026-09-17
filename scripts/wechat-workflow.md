# 微信正文最小流程

1. 让 AI 生成或修改一份 Markdown 源稿，例如 `article.md`。
2. 让 AI 运行 `node scripts/render-wechat.mjs article.md`；脚本在同目录生成 `article.html`。
3. 打开对应的 `.html`，复制正文并粘贴到公众号编辑器。
4. 单独填写标题；检查 HTML 中的图片是否被公众号保留，必要时按图注位置替换。

源稿是唯一需要维护的文章文件，HTML 是可重复生成的交付文件。Markdown 中的图片会保留为图片标签和图注，因此图片不会因为进入“正文复制”流程而被丢弃。

## 公众号发布资料

需要发布公众号时，在文章自己的输出目录中另外准备：

- `summary.txt`：摘要字段的纯文本内容。
- `cover.png`：符合公众号发布尺寸要求的题图；题图属于发布资料，不放进 Markdown 正文。
- `填写资料.txt`：汇总标题、摘要、题图和正文文件，方便复制到草稿编辑器。

这些资料和 `.html` 一样都是可重新生成的交付物，不进入文章正式文档；正式文档只维护 Markdown 源稿。

详细命令和样式说明见 [wechat-layout.md](wechat-layout.md)。
