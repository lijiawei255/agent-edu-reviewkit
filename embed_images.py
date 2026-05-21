"""
HTML图片内嵌工具 —— 将相对路径图片引用转换为 base64 data URI。

使用方法:
  python embed_images.py review.html              # 输出 review_embedded.html
  python embed_images.py review.html --in-place    # 原地替换
  python embed_images.py review.html --image-dir extracted_images
"""

import os
import sys
import base64
import argparse
import hashlib
from html.parser import HTMLParser

# HTML 无内容标签（不生成闭合标签）
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'source', 'track', 'wbr',
}


def mime_type_from_ext(ext):
    """通过文件扩展名推断 MIME 类型"""
    mapping = {
        '.png':  'image/png',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif':  'image/gif',
        '.bmp':  'image/bmp',
        '.webp': 'image/webp',
        '.svg':  'image/svg+xml',
        '.tiff': 'image/tiff',
        '.ico':  'image/x-icon',
    }
    return mapping.get(ext.lower(), 'application/octet-stream')


def get_image_hash(filepath):
    """计算图片文件的哈希值，用于去重检测"""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'rb') as f:
            data = f.read(65536)  # 读取前64KB用于哈希
        return hashlib.md5(data).hexdigest()
    except OSError:
        return None


def validate_image(filepath):
    """检查图片文件是否可读（魔数校验）"""
    if not os.path.exists(filepath):
        return False
    if os.path.getsize(filepath) < 32:
        return False
    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)
        valid = [
            b'\x89PNG\r\n\x1a\n',
            b'\xff\xd8\xff',
            b'GIF8',
            b'BM',
            b'<svg',
            b'<SVG',
            b'<?xml',
        ]
        for magic in valid:
            if header[:len(magic)] == magic:
                return True
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return True
        return False
    except OSError:
        return False


def analyze_image_quality(filepath):
    """
    分析图片质量，返回质量评级
    返回: (quality: str, size: int, width_guess: int, height_guess: int)
    quality: 'excellent', 'good', 'poor', 'too_small'
    """
    if not os.path.exists(filepath):
        return ('missing', 0, 0, 0)

    size = os.path.getsize(filepath)

    # 太小的图片
    if size < 1024:  # < 1KB
        return ('too_small', size, 0, 0)

    # 根据文件大小粗略估算分辨率
    # 假设中等压缩率的JPG/PNG约 0.5-2 bytes/pixel
    est_pixels = size // 2  # 保守估算
    width_guess = int(est_pixels ** 0.5)
    height_guess = width_guess

    if size > 100 * 1024:  # > 100KB
        quality = 'excellent'
    elif size > 30 * 1024:  # > 30KB
        quality = 'good'
    elif size > 10 * 1024:  # > 10KB
        quality = 'poor'
    else:
        quality = 'too_small'

    return (quality, size, width_guess, height_guess)


class ImgSrcRewriter(HTMLParser):
    """解析HTML，将图片引用替换为 base64 data URI"""

    def __init__(self, image_dir, image_cache):
        super().__init__()
        self.image_dir = image_dir
        self.image_cache = image_cache
        self.output_parts = []
        self.embedded_count = 0
        self.total_size = 0
        self.missing_images = []
        self.poor_quality_images = []
        self.duplicate_images = {}  # hash -> [paths]
        self._seen_hashes = {}  # hash -> first_path
        self._path_index = None  # 延迟构建：basename -> full_path 索引
        self.error_count = 0

    def error(self, message):
        """记录 HTML 解析错误，不中断处理"""
        self.error_count += 1

    def handle_starttag(self, tag, attrs):
        attr_str = self._build_attr_string(tag, attrs)
        self.output_parts.append(f"<{tag}{attr_str}>")

    def handle_endtag(self, tag):
        if tag not in VOID_ELEMENTS:
            self.output_parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.output_parts.append(data)

    def handle_comment(self, data):
        self.output_parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.output_parts.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.output_parts.append(f"<?{data}>")

    def handle_entityref(self, name):
        self.output_parts.append(f"&{name};")

    def handle_charref(self, name):
        self.output_parts.append(f"&#{name};")

    def _build_attr_string(self, tag, attrs):
        result = []
        # 用于判断 link 标签是否引用图标
        rel_value = None
        for name, value in attrs:
            if name == 'rel':
                rel_value = (value or '').lower()

        for name, value in attrs:
            if value is None:
                result.append(f' {name}')
            elif tag == 'img' and name == 'src':
                result.append(f' {name}="{self._convert_src(value)}"')
            elif tag == 'img' and name == 'srcset':
                result.append(f' {name}="{self._convert_srcset(value)}"')
            elif tag == 'source' and name == 'srcset':
                result.append(f' {name}="{self._convert_srcset(value)}"')
            elif tag == 'image' and name == 'href':
                result.append(f' {name}="{self._convert_src(value)}"')
            elif tag == 'link' and name == 'href' and rel_value and 'icon' in rel_value:
                result.append(f' {name}="{self._convert_src(value)}"')
            else:
                result.append(f' {name}="{value}"')
        return ''.join(result)

    def _convert_srcset(self, srcset_value):
        """将 srcset 属性中的所有 URL 转换为 data URI"""
        parts = []
        for entry in srcset_value.split(','):
            entry = entry.strip()
            if not entry:
                continue
            tokens = entry.rsplit(None, 1)
            if len(tokens) == 2:
                url, descriptor = tokens
                desc_lower = descriptor.rstrip(',')
                if desc_lower in ('1x', '2x', '3x', '4x') or desc_lower.endswith('w'):
                    new_url = self._convert_src(url.strip())
                    parts.append(f"{new_url} {descriptor}")
                    continue
            new_url = self._convert_src(entry.strip())
            parts.append(new_url)
        return ', '.join(parts)

    def _resolve_image(self, src):
        """多级路径解析：子目录保留 → 纯文件名 → 当前目录 → 递归搜索"""
        if os.path.isabs(src) and os.path.exists(src):
            return src

        # 策略1：相对于 image_dir，保留子目录结构
        candidate = os.path.normpath(os.path.join(self.image_dir, src.lstrip('/\\')))
        if os.path.exists(candidate):
            return candidate

        # 策略2：仅文件名（向后兼容的扁平查找）
        candidate = os.path.join(self.image_dir, os.path.basename(src))
        if os.path.exists(candidate):
            return candidate

        # 策略3：相对于当前工作目录
        if os.path.exists(src):
            return src

        # 策略4：在 image_dir 中递归搜索同名文件
        basename = os.path.basename(src)
        if self._path_index is None:
            self._path_index = {}
            if os.path.isdir(self.image_dir):
                for root, _dirs, files in os.walk(self.image_dir):
                    for fname in files:
                        if fname not in self._path_index:
                            self._path_index[fname] = os.path.join(root, fname)
        match = self._path_index.get(basename)
        if match:
            return match

        return None

    def _convert_src(self, src):
        """将相对路径转换为 base64 data URI。找不到文件则保持原路径。"""
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            return src

        img_path = self._resolve_image(src)

        if img_path is None or not validate_image(img_path):
            if img_path is None:
                self.missing_images.append(src)
                print(f"  ⚠ 警告：找不到图片文件 '{src}'，保持原始引用", file=sys.stderr)
            else:
                self.missing_images.append(src)
                print(f"  ⚠ 警告：图片文件 '{src}' 损坏或无法识别，保持原始引用", file=sys.stderr)
            return src

        # 质量检测
        quality, size, w, h = analyze_image_quality(img_path)
        if quality in ('too_small', 'poor'):
            self.poor_quality_images.append((src, quality, size))

        # 去重检测
        img_hash = get_image_hash(img_path)
        if img_hash:
            if img_hash in self._seen_hashes:
                # 发现重复图片
                first_path = self._seen_hashes[img_hash]
                if first_path not in self.duplicate_images:
                    self.duplicate_images[first_path] = []
                self.duplicate_images[first_path].append(src)
            else:
                self._seen_hashes[img_hash] = src

        abs_path = os.path.abspath(img_path)

        if abs_path in self.image_cache:
            encoded = self.image_cache[abs_path]
        else:
            try:
                file_size = os.path.getsize(abs_path)
            except OSError:
                self.missing_images.append(src)
                return src
            MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
            if file_size > MAX_IMAGE_SIZE:
                print(f"  ⚠ 警告：图片 '{src}' 过大 ({file_size/1024/1024:.1f} MB)，跳过内嵌，保留原始引用",
                      file=sys.stderr)
                self.missing_images.append(src)
                return src
            with open(abs_path, 'rb') as f:
                data = f.read()
            encoded = base64.b64encode(data).decode('ascii')
            self.image_cache[abs_path] = encoded
            self.embedded_count += 1
            self.total_size += len(data)

        ext = os.path.splitext(abs_path)[1]
        mime = mime_type_from_ext(ext)
        return f"data:{mime};base64,{encoded}"


def analyze_image_directory(image_dir):
    """分析图片目录，统计所有图片的质量信息"""
    if not os.path.isdir(image_dir):
        return None

    stats = {
        'total': 0,
        'excellent': 0,
        'good': 0,
        'poor': 0,
        'too_small': 0,
        'total_size': 0,
        'extensions': {},
    }

    for root, _dirs, files in os.walk(image_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if validate_image(fpath):
                quality, size, _w, _h = analyze_image_quality(fpath)
                ext = os.path.splitext(fname)[1].lower()
                stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
                stats['total'] += 1
                stats[quality] = stats.get(quality, 0) + 1
                stats['total_size'] += size

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='将HTML中的相对路径图片引用内嵌为 base64 data URI'
    )
    parser.add_argument('html_file', help='输入的HTML文件路径')
    parser.add_argument('--image-dir', default='extracted_images',
                        help='图片文件所在目录（默认: extracted_images）')
    parser.add_argument('--in-place', action='store_true',
                        help='原地替换输入文件（默认输出到 <name>_embedded.html）')
    parser.add_argument('--analyze-only', action='store_true',
                        help='只分析图片目录质量，不生成HTML')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='输出详细的处理信息')
    args = parser.parse_args()

    # 仅分析图片目录模式
    if args.analyze_only:
        stats = analyze_image_directory(args.image_dir)
        if stats is None:
            print(f"错误：图片目录 '{args.image_dir}' 不存在")
            sys.exit(1)

        print("=" * 50)
        print(f"📊 图片目录质量分析: {args.image_dir}")
        print("=" * 50)
        print(f"  总图片数: {stats['total']}")
        print(f"  总大小: {stats['total_size'] / 1024:.0f} KB")
        print()
        print("  质量分布:")
        print(f"    ✅ 优秀(>100KB): {stats['excellent']}")
        print(f"    ✔️  良好(>30KB):  {stats['good']}")
        print(f"    ⚠️  一般(>10KB):  {stats['poor']}")
        print(f"    ❌ 过小(<10KB):   {stats['too_small']}")
        print()
        print("  格式分布:")
        for ext, count in sorted(stats['extensions'].items()):
            print(f"    {ext}: {count}")
        print("=" * 50)
        return

    if not os.path.exists(args.html_file):
        print(f"错误：文件 '{args.html_file}' 不存在。")
        sys.exit(1)

    if not os.path.isdir(args.image_dir):
        print(f"警告：图片目录 '{args.image_dir}' 不存在。将只根据原始路径查找图片。",
              file=sys.stderr)

    with open(args.html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    rewriter = ImgSrcRewriter(args.image_dir, {})
    rewriter.feed(html)
    rewriter.close()

    output_html = ''.join(rewriter.output_parts)

    if args.in_place:
        output_path = args.html_file
    else:
        base, ext = os.path.splitext(args.html_file)
        output_path = f"{base}_embedded{ext}"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    # 输出详细统计
    print("=" * 50)
    print("✅ 图片内嵌完成")
    print("=" * 50)
    print(f"  内嵌图片数: {rewriter.embedded_count}")

    if rewriter.error_count > 0:
        print(f"  ⚠️  HTML解析警告: 发现 {rewriter.error_count} 个格式问题，已跳过")

    if rewriter.embedded_count > 0:
        size_kb = rewriter.total_size / 1024
        encoded_kb = rewriter.total_size * 1.37 / 1024
        print(f"  原始大小: {size_kb:.0f} KB")
        print(f"  Base64后: ~{encoded_kb:.0f} KB")

    if rewriter.missing_images:
        print(f"\n  ⚠️  缺失图片 ({len(rewriter.missing_images)}张):")
        for img in rewriter.missing_images[:5]:
            print(f"    - {img}")
        if len(rewriter.missing_images) > 5:
            print(f"    ... 还有 {len(rewriter.missing_images) - 5} 张")

    if rewriter.poor_quality_images and args.verbose:
        print(f"\n  ⚠️  低质量图片 ({len(rewriter.poor_quality_images)}张):")
        for img, quality, size in rewriter.poor_quality_images[:5]:
            print(f"    - {img} [{quality}, {size} bytes]")

    if rewriter.duplicate_images and args.verbose:
        total_dups = sum(len(v) for v in rewriter.duplicate_images.values())
        print(f"\n  ℹ️  重复图片检测 ({total_dups}次重复):")
        for i, (original, duplicates) in enumerate(rewriter.duplicate_images.items()):
            if i >= 3:
                print(f"    ... 还有 {len(rewriter.duplicate_images) - 3} 组")
                break
            print(f"    原图: {original}")
            for dup in duplicates:
                print(f"      ↳ {dup}")

    print(f"\n  📄 输出文件: {os.path.abspath(output_path)}")
    print("=" * 50)


if __name__ == '__main__':
    main()
