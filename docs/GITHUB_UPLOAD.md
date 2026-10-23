# GitHub 上传说明

本包为 2026-10-23 README 与分类修订版：58 条论文／项目、21 个具名基准、九个核心研究问题、八个比较维度。

## 1. 放到仓库根目录

解压 ZIP，把所有内容放在目标 GitHub 仓库的根目录。根目录应直接看到 `README.md`、`data/`、`site/`、`scripts/` 和 `.github/`，不要多套一层文件夹。

**必须保留隐藏的 `.github/`、`.gitignore` 和 `site/.nojekyll`。** 本包不含 `.git`、原文缓存、环境依赖和测试截图。

已有仓库：先 clone 最新版本，将解压内容复制进去，再检查差异、commit 和 push。不要删除现有仓库的 `.git`，也不需要 force push。

新建空仓库：在解压后的目录运行下面的命令，将 `OWNER/REPO` 替换为目标地址。

```bash
git init
git checkout -b main
git add .
git commit -m "整理代码世界模型文献并更新分类与可视化"
git remote add origin https://github.com/OWNER/REPO.git
git push -u origin main
```

GitHub 网页上传文件也可以，但请确认隐藏目录和所有子目录都上传了；只上传 ZIP 本身不会展示 README 或部署网站。

## 2. 启用交互网站

1. 仓库 Settings → Pages → Build and deployment → Source，选择 **GitHub Actions**。
2. Actions → **Deploy research website** → Run workflow，选择 `main`。
3. 成功后使用 Pages 显示的实际网站地址。工作流自动识别仓库 owner 和名称，无须修改源码中的账号。
4. 将 `docs/README.template.md` 中的 `{{SITE_URL}}` 替换为实际网站地址，运行 `python3 scripts/build.py`，提交更新。这样仓库 README 的按钮才会直达已上线的网页。

默认按钮指向仓库内的 `site/index.html`，可供本地打开；GitHub 文件浏览页不会执行 HTML。未知目标仓库时，交付包没有预填一个虚构的线上地址。

## 3. 修改后检查

需要 Python 3；网站运行不需要 npm 安装或后端服务。

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

如需本地浏览：`python3 -m http.server 8000 --directory site`，打开 `http://localhost:8000`。

README 和导出文件由统一数据生成。文献修改 `data/papers.json`；分类修改 `data/taxonomy.json`；排版修改 `docs/README.template.md` 和 `scripts/build.py`。不要只修改生成结果。

`Validate collection` 工作流自动执行检查。首次推送尚未启用 Pages 时，部署工作流可能需要在步骤 2 设置后重跑。

## 4. 每日发现（可选）

随包保留 `Daily research discovery` 工作流，每天 10:17 Asia/Shanghai 运行并提交候选审核。要自动创建 PR，需在 Settings → Actions → General 允许 GitHub Actions 创建 pull requests。不需要时可在 Actions 中禁用该工作流。

原始论文来源核验日期为 2026-10-21；此次主要更新分类与展示。详细记录见 `docs/VALIDATION.md`。
