# 本地预览与 GitHub 发布

项目使用 Python 标准库生成数据与文档；前端是静态 HTML、CSS 和 JavaScript。没有 npm 构建、数据库或必须配置的模型 API。

## 本地预览

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

打开 http://localhost:8000。也可以直接打开 `site/index.html`，搜索与对比使用本地 `catalog.js`，不依赖 fetch。

## 复合标签网站与预览入口

网站采用简洁论文清单，按 World Models Taxonomy V2 提供主分类单选、细方向单选与八个维度的辅助标签多选，并保留月份、标题／作者检索和徽标筛选。辅助标签取交集，条件保存在网址中。`data/taxonomy.json` 的 `research_areas`、`tag_dimensions` 定义词表；每篇论文的 `classification` 保存唯一主分类与辅助标签。完整 BibTeX、JSON、CSV 导出继续保留在静态目录和 README 链接中。

`data/site.json` 的 `repository` 保存目标 GitHub 仓库，当前为 `awesome-cwm/Awesome-Code-World-Model`；默认构建与 `--check` 都使用此配置，使提交的 README 与 CI 校验一致。网站地址为 `https://awesome-cwm.github.io/Awesome-Code-World-Model/`，上线结果以 Pages deployment 为准。

同一配置文件的 `preview_url` 保存之前的独立托管预览入口。未配置仓库且没有指定 `--repository` 时，README 才使用此入口；两者均为空则回退为本地 `site/index.html`。该预览通过 Sites 发布，初始为账号私有访问，公开 GitHub Pages 是独立的发布渠道。

指定 `python3 scripts/build.py --repository OWNER/REPOSITORY` 后，README 自动使用目标仓库的 GitHub Pages 地址，优先于预览配置。GitHub Actions 的 Pages 工作流已传入当前仓库名，无需手工替换生成文件中的 URL。

## 发布

1. 在目标 GitHub 账号或组织创建 `awesome-code-world-model`，并将此目录推送到 `main` 分支。
2. 打开仓库 Settings → Pages → Build and deployment，选择 **GitHub Actions**。
3. 执行 `Deploy research website` 工作流。站点地址通常是 `https://OWNER.github.io/awesome-code-world-model/`，实际以 deployment 输出为准。
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
