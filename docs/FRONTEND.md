# Web 前端维护

网站使用两个静态入口，共享 `catalog.js` 中的目录数据：

- `site/index.html` + `site/home.js`：项目介绍、研究方向、新闻、近期论文和阅读路径。
- `site/papers.html` + `site/app.js`：搜索、筛选、五种目录视图、论文详情、引用和对比。
- `site/style.css`：既有公共样式，也供自动生成的文档页使用。
- `site/pages.css`：两个入口的布局样式，通过页面 class 限定作用范围。
- `site/theme.css`：共用的颜色、字号、间距、圆角、阴影和交互状态；深浅主题集中维护。
- `site/theme.js`：页面绘制前恢复主题偏好，并在导航中提供 System → Light → Dark 三态 SVG 图标按钮（显示器／太阳／月亮）。按钮保留完整 `aria-label` 和 `title`，默认跟随系统，手动选择保存在本地；所有入口与生成文档共用。
- `site/fonts/`：随站点发布的 Newsreader（标题）、Source Sans 3（正文）、IBM Plex Mono（代码）字体及各自的 OFL 许可证。字体仅包含拉丁字形，中文使用系统衬线／无衬线字体回退，无运行时外部字体请求。

论文、分类及新闻继续在 `data/` 中维护。`catalog.js` 与导出文件由原有构建脚本生成，不手动编辑。新增论文无需同时维护两份页面内容。

首页通过 `papers.html?track=...`、`?path=...` 和 `?paper=...` 链接论文库。旧首页上的筛选参数及 `#library`、`#benchmark-entry` 锚点会跳转到论文库，保留查询参数和锚点。仅带跟踪参数的首页链接仍显示首页。

文档页统一由 `scripts/build.py` 的 `document_page()` 生成，包括 `docs/TOPIC_REVIEW.md` 对应的 `site/topic-review.html`，以及本说明对应的 `site/frontend.html`。修改 Markdown 源文档或模板后运行构建，不直接编辑生成的 HTML。导航以 `aria-current="page"` 标出当前文档，并使用与首页一致的主题强调色和下划线。

两个入口和所有文档的主导航固定为 Home、Papers、Taxonomy、Research notes、Contribute、Repository guide，顺序与本地目标一致。Repository guide 始终链接 `readme.html`，不因配置 GitHub 仓库地址而改变。未列入主导航的辅助文档在正文上方的面包屑中标记当前页，不向顶部菜单临时增删条目。

## 离线主题与深链接

`file://` 访问仍使用本地字体与脚本，不需要服务器或网络。主题默认跟随系统，手动选择保存在 `localStorage`。HTTP 同源页面共享该选择；浏览器并未统一保证 `file://` 的跨文件存储行为，隐私设置也可能禁止存储。在不共享存储的环境中，新页面会回到系统主题，可在当前页重新选择，或通过本地 HTTP 服务获得稳定的跨页记忆。存储不可用不影响阅读与当前页主题切换。

离线复现记录（2026-10-26）：开始视觉升级前，Chrome 155.0.8059.85 和 Edge 156.0.4314.42 在已有修复的工作区中通过 Dark 导航、当前页高亮和绕过缓存刷新；未复现颜色不更新。升级后再使用这两款浏览器和 Playwright Firefox 157.0 验证上述场景，均保持暗色，Taxonomy 具有绿色下划线。Firefox 首次运行时缺少测试浏览器，安装后已补测通过。完整结果写入 `test-results/file-browser-results.json`。这表示当前版本通过验证，不表示所有浏览器的离线存储行为都相同。

`#benchmark-entry` 会在手机端自动展开集合面板并定位；关闭 `?paper=ID` 打开的详情时删除 `paper` 参数，保留其余查询参数与锚点，刷新不会再次打开已关闭的详情。首页 brand 与 Home 链接均使用 `index.html`，不会在离线浏览时进入目录列表。

## 视觉升级与性能边界

所有页面使用同一套吸顶 header，支持时以半透明背景和 `backdrop-filter` 模糊增强；不支持时保留实色背景。文档页的 header 与目录通过 `document_page()` 生成，不增加运行时目录脚本。含至少四个二级标题的文档自动生成去重锚点和目录：1100px 以上为吸顶侧栏，较窄屏幕为原生折叠面板。正文始终为 16px。

首页 SVG、光斑、两张方向卡片和论文卡片使用 `theme.css` 的深浅主题变量。首页和论文库以及生成文档预加载 Newsreader 正体和 Source Sans 3；字体仍使用 `font-display:swap`，离线失败时可以回退到本机字体。代码框改为图下正常文档流，避免压住立方体。资源图标为内联 SVG，并保留可读文字。

首页计数只运行一次，卡片鼠标光晕通过 `requestAnimationFrame` 每帧最多写一次 `--x` / `--y`；减少动画模式下禁用计数和跟随效果。进场动画只在支持 `animation-timeline:view()` 时启用，基础样式始终显示内容。切换主题时若支持 View Transitions，则使用独立圆形快照从按钮位置扩散，并配合页面淡入；动画只改变 `transform` / `opacity`，文字不会随圆形缩放。未支持或开启减少动画时直接切换。SVG 虚线路径按设计使用 `stroke-dashoffset`，这是局部 SVG 重绘的特例；同样在减少动画模式下停用。论文卡片使用 `content-visibility:auto` 与估算高度，打印时恢复完整渲染。

浏览器测试输出 `theme-{light|dark}-{index|papers|taxonomy}.html-{1440|1024|768|390}.png`，共 24 张；额外检查 320px 不溢出、目录链接、吸顶位置、主题降级、减少动画和 `file://`。`test-results/` 已忽略，不提交截图和临时检查产物。

## 本地验证

在仓库根目录运行：

```bash
python -X utf8 -m unittest discover -s tests -v
python -X utf8 scripts/build.py --check
node --check site/app.js
node --check site/home.js
node --check site/theme.js
python -m http.server 8000 --bind 127.0.0.1 --directory site
```

首页为 `http://127.0.0.1:8000/`，论文库为 `http://127.0.0.1:8000/papers.html`。也可直接打开两个 HTML 文件，继续支持离线浏览。

安装可选的 Playwright 与 Chromium 后，在另一个终端运行 `python -X utf8 tests/browser_smoke.py`。也可用环境变量 `CWM_BROWSER_PATH` 指定已安装的 Chromium 浏览器，`CWM_TEST_URL` 指定站点根地址。测试覆盖两个入口、旧链接、详情、筛选、对比和四种屏幕宽度；截图输出到已忽略的 `test-results/`。

PowerShell 使用本机 Chrome 的示例（服务器需先启动）：

```powershell
$env:CWM_BROWSER_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
python -X utf8 tests/browser_smoke.py
```

离线主题检查会使用已安装的 Chrome、Edge 和 Playwright Firefox；可用 `CWM_EDGE_PATH` / `CWM_FIREFOX_PATH` 指定路径。未安装的浏览器会明确报告 skipped，而不会算作通过。浏览器仅为可选测试工具，不属于站点依赖。

部署继续使用仓库原有 GitHub Pages 工作流，无新增构建依赖。
