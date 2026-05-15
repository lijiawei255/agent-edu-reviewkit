"""下载 MathJax v3 到本地，供生成的 HTML 离线使用。

用法: python setup_mathjax.py

下载 MathJax es5 目录到 ./mathjax/，使生成的复习文档无需联网即可渲染数学公式。
"""

import os
import sys
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

MATHJAX_VERSION = "3.2.2"
# npm registry tarball (优先：结构为 package/es5/...)
NPM_URL = f"https://registry.npmjs.org/mathjax/-/mathjax-{MATHJAX_VERSION}.tgz"
# GitHub release tarball（备用：结构为 MathJax-3.2.2/es5/...）
GITHUB_URL = f"https://github.com/mathjax/MathJax/archive/refs/tags/{MATHJAX_VERSION}.tar.gz"
OUTPUT_DIR = Path(__file__).resolve().parent / "mathjax"

# 不同源对应的 tarball 内部 es5 路径
SOURCE_ROOTS = {
    NPM_URL: f"package/es5",
    GITHUB_URL: f"MathJax-{MATHJAX_VERSION}/es5",
}


def download(url, timeout=60):
    """下载 URL 内容，失败返回 None"""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def extract_es5(tarball_data, url):
    """从 tarball 中提取 es5/ 目录，返回源目录路径"""
    src_root = SOURCE_ROOTS.get(url)
    with tarfile.open(fileobj=__import__('io').BytesIO(tarball_data), mode="r:gz") as tf:
        tmpdir = tempfile.mkdtemp()
        tf.extractall(tmpdir)
        src_es5 = os.path.join(tmpdir, src_root)
        if os.path.isdir(src_es5):
            return src_es5
        # 如果指定 root 不存在，尝试自动检测
        for root, dirs, _files in os.walk(tmpdir):
            if root.endswith("es5") and os.path.isfile(os.path.join(root, "tex-svg.js")):
                return root
        shutil.rmtree(tmpdir, ignore_errors=True)
        return None


def main():
    if OUTPUT_DIR.exists():
        es5 = OUTPUT_DIR / "es5" / "tex-svg.js"
        if es5.exists():
            print(f"MathJax 已安装在 {OUTPUT_DIR}")
            print(f"  tex-svg.js: {es5}")
            return
        else:
            print(f"{OUTPUT_DIR} 存在但不完整，重新下载...")
            shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    errors = []
    for url in [NPM_URL, GITHUB_URL]:
        print(f"正在下载 MathJax v{MATHJAX_VERSION} ...")
        print(f"  源: {url}")
        try:
            tarball = download(url, timeout=120)
        except Exception as e:
            errors.append(f"{url}: {e}")
            print(f"  下载失败: {e}")
            continue

        print(f"  已下载 {len(tarball) / 1024 / 1024:.1f} MB，正在解压...")
        try:
            tmpdir = extract_es5(tarball, url)
        except Exception as e:
            errors.append(f"{url} (解压): {e}")
            print(f"  解压失败: {e}")
            continue

        if tmpdir is None:
            errors.append(f"{url}: 在压缩包中未找到 es5/ 目录")
            print("  错误: 在压缩包中未找到 es5/ 目录")
            continue

        dst_es5 = str(OUTPUT_DIR / "es5")
        if os.path.exists(dst_es5):
            shutil.rmtree(dst_es5)
        shutil.copytree(tmpdir, dst_es5)
        shutil.rmtree(os.path.dirname(tmpdir), ignore_errors=True)  # 清理临时目录
        break
    else:
        print("\n所有下载源均失败:")
        for err in errors:
            print(f"  - {err}")
        print("\n请检查网络连接，或手动下载 MathJax 3 es5 并解压到 mathjax/ 目录。")
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
        sys.exit(1)

    es5 = OUTPUT_DIR / "es5" / "tex-svg.js"
    if es5.exists():
        size_mb = sum(f.stat().st_size for f in OUTPUT_DIR.rglob("*") if f.is_file()) / 1024 / 1024
        print(f"完成！MathJax 已安装到 {OUTPUT_DIR}")
        print(f"  磁盘占用: {size_mb:.1f} MB")
        print(f"  入口文件: mathjax/es5/tex-svg.js")
        print()
        print("生成的 HTML 会自动优先使用本地 MathJax。无网络时公式也能正常渲染。")
    else:
        print("警告: 解压完成但未找到 mathjax/es5/tex-svg.js，请检查安装结果。")


if __name__ == "__main__":
    main()
