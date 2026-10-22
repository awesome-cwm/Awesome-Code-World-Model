"""兼容旧验收入口；真实浏览器检查统一由 browser_search.cjs 执行。"""
import shutil
import subprocess
from pathlib import Path

if __name__ == '__main__':
    node = shutil.which('node')
    if not node:
        raise SystemExit('Browser verification needs Node.js. See docs/VALIDATION.md.')
    script = Path(__file__).with_name('browser_search.cjs')
    raise SystemExit(subprocess.call([node, str(script)], cwd=str(script.parent.parent)))
