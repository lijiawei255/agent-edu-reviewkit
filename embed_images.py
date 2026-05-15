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


class ImgSrcRewriter(HTMLParser):
    """解析HTML，将图片引用替换为 base64 data URI"""

    def __init__(self, image_dir, image_cache):
        super().__init__()
        self.image_dir = image_dir
        self.image_cache = image_cache
        self.output_parts = []
        self.embedded_count = 0
        self.total_size = 0
        self._path_index = None  # 延迟构建：basename -> full_path 索引

    def error(self, message):
        """忽略 HTML 解析错误，避免因畸形输入崩溃"""
        pass

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
                print(f"  ⚠ 警告：找不到图片文件 '{src}'，保持原始引用", file=sys.stderr)
            else:
                print(f"  ⚠ 警告：图片文件 '{src}' 损坏或无法识别，保持原始引用", file=sys.stderr)
            return src

        abs_path = os.path.abspath(img_path)

        if abs_path in self.image_cache:
            encoded = self.image_cache[abs_path]
        else:
            with open(abs_path, 'rb') as f:
                data = f.read()
            encoded = base64.b64encode(data).decode('ascii')
            self.image_cache[abs_path] = encoded
            self.embedded_count += 1
            self.total_size += len(data)

        ext = os.path.splitext(abs_path)[1]
        mime = mime_type_from_ext(ext)
        return f"data:{mime};base64,{encoded}"


def main():
    parser = argparse.ArgumentParser(
        description='将HTML中的相对路径图片引用内嵌为 base64 data URI'
    )
    parser.add_argument('html_file', help='输入的HTML文件路径')
    parser.add_argument('--image-dir', default='extracted_images',
                        help='图片文件所在目录（默认: extracted_images）')
    parser.add_argument('--in-place', action='store_true',
                        help='原地替换输入文件（默认输出到 <name>_embedded.html）')
    args = parser.parse_args()

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

    print(f"Done: {rewriter.embedded_count} image(s) embedded")
    if rewriter.embedded_count > 0:
        size_kb = rewriter.total_size / 1024
        encoded_kb = rewriter.total_size * 1.37 / 1024
        print(f"  Image raw size: {size_kb:.0f} KB")
        print(f"  Base64 encoded: ~{encoded_kb:.0f} KB")
    print(f"  Output: {os.path.abspath(output_path)}")


if __name__ == '__main__':
    main()
