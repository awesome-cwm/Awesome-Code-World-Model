# 本地预览与 GitHub 发布

项目使用 Python 标准库生成数据与文档；前端是静态 HTML、CSS 和 JavaScript。没有 npm 构建、数据库或必须配置的模型 API。

## 本地预览

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

打开 http://localhost:8000 查看项目首页，进入 `/papers.html` 搜索和浏览论文。也可以直接打开 `site/index.html` 或 `site/papers.html`；搜索与对比使用本地 `catalog.js`，不依赖 fetch。前端结构与验证步骤见 `docs/FRONTEND.md`。

## 发布

1. 在目标 GitHub 账号或组织创建 `awesome-code-world-model`，并将此目录推送到 `main` 分支。
2. 打开仓库 Settings → Pages → Build and deployment，选择 **GitHub Actions**。
3. 执行 `Deploy research website` 工作流。站点地址通常是 `https://OWNER.github.io/awesome-code-world-model/`，实际以 deployment 输出为准。
4. 网页构建会从 `github.repository` 自动生成正确的 GitHub 链接；未配置仓库的本地版本显示 Repository guide。
5. Pages 上线后，将 `docs/README.template.md` 中的 `{{SITE_URL}}` 替换为实际 Pages 地址，再运行 `python3 scripts/build.py` 并提交生成结果，让仓库 README 的按钮直达网页。不要在 README 中手改自动生成的论文条目。

Actions 中的 `--repository OWNER/REPO` 只用于生成部署产物；提交到仓库的文件使用默认 `python3 scripts/build.py` 生成，与 CI 的 `--check` 保持一致。

仓库尚未绑定远端时不要声称网页已经上线。GitHub Actions 的远程运行需要完成推送与 Pages 设置后才能验证。

## 每日更新

`Daily research discovery` 在 **02:17 UTC / 10:17 Asia/Shanghai** 触发，也可手动执行。GitHub 可能延迟 scheduled jobs，且长期不活跃的公开仓库可能被暂停定时任务。

若需要自动建立审核 PR，在 Settings → Actions → General 中允许 GitHub Actions 创建 pull requests。组织策略可能限制此权限；即使创建 PR 失败，已上传的 discovery artifact 仍可用于审核。流程只提交候选，不直接修改正式目录。

项目不需要 personal access token；默认使用该仓库的 `GITHUB_TOKEN`。不应把任何私钥、个人 token 或模型密钥提交进代码。

## 持续维护

正式论文元数据在 `data/papers.json`；分类定义在 `data/taxonomy.json`；新闻公告在 `data/updates.json`。运行 `build.py` 会同步 README、网页和导出文件。CI 用 `--check` 检查是否忘记提交生成结果。

公开发布版本不会包含 `research/sources/` 的本地原文抓取缓存。可审计的来源 URL 与核验日期已经保存在数据记录中。
