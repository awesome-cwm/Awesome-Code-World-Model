# 本地预览与 GitHub 发布

项目使用 Python 标准库生成数据与文档；前端是静态 HTML、CSS 和 JavaScript。没有 npm 构建、数据库或必须配置的模型 API。

## 本地预览

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

打开 http://localhost:8000。也可以直接打开 `site/index.html`，搜索与主题筛选使用本地 `catalog.js`，不依赖 fetch。

## 复合标签网站与预览入口

网站采用简洁论文清单，展示 `data/taxonomy.json.topics` 中的 22 个平级主题复选项，多选取交集，并保留月份、标题／作者检索和资源徽标筛选。没有主分类、细方向或辅助维度界面。条件保存在网址的 `topics`、`month`、`q`、`badge` 参数中；旧 `area`、`direction`、`tags` 参数不参与筛选。

每条记录的 `classification.readme_topic` 只决定 README 中的唯一展示位置，必须属于同一记录的 `classification.topics`。网站按 `topics` 检索，可跨主题对应；结果列表仍只显示每篇论文一次。README 全部论文条目也只列一次，不重复列近期论文或阅读路径。

分类的核对日期、逐标签英文依据、实际来源阅读范围与不确定项保存在 `classification` 中。构建生成 `docs/TOPIC_REVIEW.md` 和 `site/topic-review.html`，方便逐篇复核；来源核对不等于完整全文审查或独立复现。历史 `track`、`category`、`cross_categories`、`dimensions` 仅供旧爬虫兼容，不构成公开分类。完整 BibTeX、JSON、CSV 导出保留在静态目录和 README 链接中。

`data/site.json` 的 `repository` 保存目标 GitHub 仓库，当前为 `awesome-cwm/Awesome-Code-World-Model`；默认构建与 `--check` 都使用此配置，使提交的 README 与 CI 校验一致。网站地址为 `https://awesome-cwm.github.io/Awesome-Code-World-Model/`，上线结果以 Pages deployment 为准。

同一配置文件的 `preview_url` 保存之前的独立托管预览入口。未配置仓库且没有指定 `--repository` 时，README 才使用此入口；两者均为空则回退为本地 `site/index.html`。该预览通过 Sites 发布，初始为账号私有访问，公开 GitHub Pages 是独立的发布渠道。

指定 `python3 scripts/build.py --repository OWNER/REPOSITORY` 后，README 自动使用目标仓库的 GitHub Pages 地址，优先于预览配置。GitHub Actions 的 Pages 工作流已传入当前仓库名，无需手工替换生成文件中的 URL。

## 发布

1. 将此目录推送到目标仓库的 `main` 分支；当前仓库为 `awesome-cwm/Awesome-Code-World-Model`。
2. 打开仓库 Settings → Pages → Build and deployment，选择 **GitHub Actions**。
3. 执行 `Deploy research website` 工作流。站点地址通常是 `https://OWNER.github.io/REPOSITORY/`，实际以 deployment 输出为准。
4. 网页构建会从 `github.repository` 自动生成正确的 GitHub 链接；未配置仓库的本地版本显示 Repository guide。
5. 保留 `docs/README.template.md` 中的 `{{SITE_URL}}` 占位符；构建会自动替换实际 Pages 地址。不要在 README 中手改自动生成的论文条目。

仓库尚未绑定远端时不要声称网页已经上线。GitHub Actions 的远程运行需要完成推送与 Pages 设置后才能验证。

## 每日更新

`Daily research discovery` 在 **02:17 UTC / 10:17 Asia/Shanghai** 触发，也可手动执行。GitHub 可能延迟 scheduled jobs，且长期不活跃的公开仓库可能被暂停定时任务。

若需要自动建立审核 PR，在 Settings → Actions → General 中允许 GitHub Actions 创建 pull requests。组织策略可能限制此权限；即使创建 PR 失败，已上传的 discovery artifact 仍可用于审核。流程只提交候选，不直接修改正式目录。

项目不需要 personal access token；默认使用该仓库的 `GITHUB_TOKEN`。不应把任何私钥、个人 token 或模型密钥提交进代码。

## 持续维护

正式论文元数据在 `data/papers.json`；分类定义在 `data/taxonomy.json`；新闻公告在 `data/updates.json`。运行 `build.py` 会同步 README、网页和导出文件。CI 用 `--check` 检查是否忘记提交生成结果。

公开发布版本不会包含 `research/sources/` 的本地原文抓取缓存。可审计的来源 URL 与核验日期已经保存在数据记录中。
