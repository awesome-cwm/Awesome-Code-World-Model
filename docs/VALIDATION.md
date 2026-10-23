# 首版验收记录

核验时间：2026-10-21。

## README 与分类修订验收（2026-10-23）

- 本地版本确认：当前修改前的 README 与 `awesome-code-world-model-20261021-v3.zip` 一致；58 条文献与项目、21 个具名协议全部保留。
- 参考仓库通过 GitHub API 读取：README SHA `a3979dad78ed62a36ccd89d7e1f6547eeb40b856`；首图 SHA `b26385858bd3b492351aa75796b748049f1a3fb2`。借鉴视觉层次、蓝紫／青绿色和研究地图形式，使用独立绘制的 SVG。
- 保留两条主线、九个核心研究问题；收窄可执行验证，分离横向资源索引；增加 `delivery` 后共八个比较维度。迁移依据与不确定性见 TAXONOMY.md。
- README 从 54,469 bytes 精简为 28,940 bytes。正文每项主分类完整条目只出现一次，近期更新和资源索引按需重复链接；网页仍提供交叉分类。
- 20 项单元测试通过，包括所有条目完整性、导航锚点、流式交付不蕴含交互，以及原有数据与发现流程检查。构建同步和 JavaScript 语法检查通过。
- Chromium 140 浏览器回归全部 15 组通过，包含新增的 `delivery=streaming` 与 `interaction=none` 组合过滤、URL 恢复、三个折叠区展开和目录锚点存在性。390 px 页面无水平溢出，无 JavaScript 异常。
- 独立 markdown-it CommonMark 解析确认 12 个研究分类三级标题，所有显式锚点及本地资源链接有效。GitHub 风格截图为本地近似预览，未声称远程 GitHub 页面已发布。
- 桌面、手机、研究目录与首图预览在 `test-results/readme-github-*.png` 和 `test-results/banner-preview.png`。该目录不进入版本控制。
- 原文来源核验日期仍为 2026-10-21。本次没有重新核验全部论文，也没有绑定远端或发布 Pages。

## Benchmark 精修版验收

- 保留原有全部 44 条，新增 14 条，共 58 条：36 条核心、16 条前序、6 条相邻／支撑工作；53 篇 arXiv、5 项官方报告／项目。
- 21 个具名基准／评测协议按五组索引，另设代码语料、构建验证 harness、流式系统三组入口。研究主类共 12 个，其中两条核心方向仍保留 9 类。
- README 保留居中入口、Classic／Open Source 图例、News、Recent Paper Updates 与分类逐篇清单。新增 Benchmark 及基础组件入口；CommonMark 正确解析 20 个研究／横向分类三级标题。
- `python3 -m unittest discover -s tests -v`：18 项通过；新增检查基准协议与索引不能脱节，具名别名可导出但不增加重复论文。
- `node --check site/app.js`、`python3 scripts/build.py --check` 通过。JSON／CSV 导出包含基准名称及协议。
- 真实 Chromium 验收 15 组检查通过：58 条加载、基准入口、别名搜索、URL 状态恢复、版本差异说明、数据／流式组件入口，以及原有筛选、比较、引用和离线浏览功能。
- 390 px 手机端基准表格在容器内横向滚动，页面自身无横向溢出。修正了单列 grid 的最小宽度约束。
- README、Benchmark Atlas、Taxonomy 静态页的本地链接均存在。新增检索查询未冒充已在线跑过的完整每日任务。

以下是首版和上一轮参考排版修订的历史验收记录。

## 数据与维护流程

- 44 条正式记录：26 条核心、13 条前序、5 条相邻／支撑工作。
- 41 篇 arXiv 论文与 3 项官方项目／技术报告；后者保留未知发布日期。
- `python3 -m unittest discover -s tests -v`：16 项通过。
- 校验主线归属、维度枚举、交叉类别、唯一标题和 arXiv ID、URL 类型、日期、阅读路径与导出完整性。
- 爬虫测试包括 Atom 实体解析、版本后缀去重、重复运行幂等性、保留人工驳回、跨源同名项目不覆盖论文身份、限流重试和全源失败保留队列。
- `python3 scripts/build.py --check` 检查正式数据和生成文件一致。
- `node --check site/app.js` 通过。

## 真实浏览器

使用本机 Chromium 140.0.7339.16、Playwright，桌面 1440×1100 与移动端 390×844。

- 所有条目加载，搜索与 URL 刷新恢复。
- 主类别和交叉类别、scope、机制组合筛选、无匹配状态与重置。
- 矩阵、时间线、未知日期筛选。
- 详情弹窗、性能条件、来源与引用展示、Escape 关闭。
- 最多四篇比较与超出上限提示。
- 阅读路径及其顺序。
- 移动端无横向溢出，筛选面板可折叠。
- 使用 file:// 直接打开网页，无后端仍可浏览与筛选。
- 无浏览器 JavaScript 异常。

## 参考排版修订验收

- 使用 GitHub Contents API 重新读取参考 README，核对内容 SHA `c5267acf7fb5499398dc216d9efe98e45f185343`。
- README 顺序对齐为：居中标题与网页入口 → 徽标图例 → News & Updates → Recent Paper Updates → Overview → 各分类论文 → 阅读指引与引用。
- 代表作在分类内置顶、整条加粗，并保留贡献注释；普通论文使用月份、徽标、标题链接的清单形式。交叉类别包含对应论文。
- 使用独立的 CommonMark 解析器确认 11 个分类标题和 18 个目录锚点均有效，避免 HTML 锚点吞掉 Markdown 标题。
- 网页增加三种徽标筛选、新闻／近期论文栏目和 Categories 视图。真实浏览器验证三种过滤结果、代表作排序、加粗链接、移动端和原有交互。
- 新增校验确保公开资源徽标有匹配证据，并验证 README 排版 HTML 不接受事件属性或不安全 URL。

可复跑脚本：`tests/browser_smoke.py`。默认连接 `http://127.0.0.1:8000`，可通过 `CWM_TEST_URL` 指定端口，通过 `CWM_BROWSER_PATH` 指定 Chromium。运行前安装可选测试依赖 `playwright` 和对应浏览器；项目运行本身不依赖它们。截图与机器可读报告保存在被 gitignore 排除的 `test-results/`。

## 真实在线发现

最近 3 天窗口、4 组 arXiv 查询全部成功，返回共 8 条，未报告截断。3 条命中已收录论文，5 条跨领域候选经范围审核后驳回。真实运行报告见 `data/discovery-report.json`，决定保存在 `data/inbox.json`。这次验收未运行每日 GitHub 分支查询；该来源的公开 API 可访问性已在研究阶段检查。

## 尚未验证的外部环节

- 目标 GitHub 仓库尚未指定，远程 push、GitHub Pages 上线和 Actions 定时执行尚未验证。
- 未声称逐篇全文审阅、外部代码可复现性验证或论文性能复现。
- 定时任务和 PR 创建需要目标仓库的 Actions / Pages / PR 权限；配置已经提供。
