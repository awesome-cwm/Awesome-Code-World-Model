# 网站与数据验收记录

## World Models Taxonomy V2（2026-10-22）

- 主分类按维护者提供的设计更新为六类、22 个细方向；辅助标签按八个维度组织。58 条记录各有一个主分类，辅助标签合计至少一个；初始迁移依据已有整理元数据，未重新逐篇全文审核。
- 主分类使用原生单选按钮；辅助标签使用复选框，多选取交集。细方向与主分类联动，已选标签在收起面板后仍显示；支持卡片标签入口与独立清空辅助标签。
- 保留右侧月份索引、移动月份栏、标题／作者搜索和资源徽标筛选。URL 支持刷新、前进后退；无效和旧版筛选条件不会产生隐藏约束。README 的六个主类章节不重复列入同一论文。
- 25 项 Python 测试、5 项 Node 逻辑检查、构建一致性检查通过。新增检查覆盖主类唯一性、细方向归属、辅助标签维度与非空约束、主类分组完整性及 CSV 导出。
- 真实 Chrome 下 9 组浏览器验收通过，包括六类逐一切换、跨维度交集、月份组合、URL 恢复、键盘与卡片操作、搜索与徽标、无匹配与安全文本、390px 手机布局、离线打开与 README 入口；无 JavaScript 异常。
- 截图位于忽略提交的 `test-results/taxonomy-v2-desktop.png`、`taxonomy-v2-intersection.png`、`taxonomy-v2-mobile.png`、`taxonomy-v2-mobile-tags.png`。复跑脚本：`node tests/browser_search.cjs`。

以下为较早版本的历史记录。

## 线上第 3 版本地同步（2026-10-22）

- 从线上源提交 `ff94a3c41d9932dff1df8b9117e675f44221400c` 同步 `site/index.html`、`site/app.js`、`site/style.css`，保留用户新增的月份索引；论文数据未改动。
- 桌面月份索引位于右侧，手机横向滚动；月份与标签、搜索和徽标组合生效，数量随其他条件更新。包含 Date TBC，重置、刷新和前进后退可恢复状态。
- 18 项 Python 测试、5 项 Node 检查与 8 组真实 Chrome 验收通过，无 JavaScript 异常。新增月份组合、动态数量、未知日期、URL 恢复与移动月份栏检查。
- Git 排除本地原文抓取缓存、测试缓存和发布辅助文件；CSV 保留构建脚本输出的 CRLF 字节。

## 简洁论文清单验收（2026-10-22）

- 按 Awesome Interactive World Model 的清单风格调整为浅灰背景、居中标题、蓝色筛选按钮与白色论文卡片。首页保留标题、搜索、徽标、十个可复选研究方向和论文清单。
- 研究标签为普通复选框，多选取交集，再次点击取消；支持 All 清空方向及 Clear filters 重置。没有 OR、排除、年份、高级筛选、对比、导出面板或大型首屏区域。
- 标题／作者检索、徽标与标签条件共同生效；网址记录查询并支持刷新及前进后退。旧版 OR、排除、高级筛选参数被忽略，避免隐藏条件影响结果。
- 18 项 Python 数据与构建测试、5 项 Node 索引检查通过。真实 Chrome 验收 7 组通过，包括 58 条记录、十个复选框、交集与取消、键盘操作、卡片标签、组合搜索、空状态、安全文本、旧网址、390px 手机布局、离线打开及 README 入口；无 JavaScript 异常。
- 截图：`test-results/simple-desktop.png`、`simple-intersection.png`、`simple-mobile.png`；可复跑脚本仍为 `node tests/browser_search.cjs`。

以下是较早界面版本的历史记录，保留用于追溯。

## 复合标签网站验收（2026-10-22）

- 保留全部 58 条论文记录，未改动 `data/papers.json`；十个大标签通过现有分类和维度建立可调整的映射，并支持后续逐篇显式覆盖。
- `node tests/search.test.cjs`：5 项索引逻辑检查通过，涵盖 AND / OR、排除优先级、标签循环、URL 归一化、未知值处理、显式标签覆盖和源数据不变。
- `python3 -m unittest discover -s tests -v`：18 项既有数据与构建检查通过。`node --check site/app.js`、`node --check site/search.js`、构建生成一致性检查通过。
- `node tests/browser_search.cjs`：真实 Chrome 下 11 组验收通过，涵盖十标签渲染、复合筛选、排除、键盘操作、URL 刷新与历史恢复、关键词与年份和资源组合、命中 BibTeX 导出、空状态与安全转义、详情与五种视图、无剪贴板权限时分享、390px 手机布局、离线打开和 README 入口。无浏览器 JavaScript 异常。
- 桌面截图为 1440×1080，移动截图为 390×844；页面无水平溢出。截图与报告位于忽略提交的 `test-results/`。
- 可复跑浏览器检查：先运行本地 HTTP 服务；安装可选依赖 `npm install --prefix test-results/browser-tools playwright`，然后运行 `node tests/browser_search.cjs`。可通过 `CWM_BROWSER_PATH` 指定本机 Chrome / Chromium，`CWM_TEST_URL` 指定服务器。浏览器依赖不参与网站运行。

以下为先前版本的历史记录。

核验时间：2026-10-21。

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
