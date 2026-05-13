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
    }
    return mapping.get(ext.lower(), 'application/octet-stream')


class ImgSrcRewriter(HTMLParser):
    """解析HTML，替换 <img src> 为 data URI"""

    def __init__(self, image_dir, image_cache):
        super().__init__()
        self.image_dir = image_dir
        self.image_cache = image_cache
        self.output_parts = []
        self.embedded_count = 0
        self.total_size = 0

    def handle_starttag(self, tag, attrs):
        attr_str = self._build_attr_string(tag, attrs, is_start=True)
        self.output_parts.append(f"<{tag}{attr_str}>")

    def handle_endtag(self, tag):
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

    def _build_attr_string(self, tag, attrs, is_start):
        result = []
        for name, value in attrs:
            if tag == 'img' and name == 'src':
                new_src = self._convert_src(value)
                result.append(f' {name}="{new_src}"')
            elif value is None:
                result.append(f' {name}')
            else:
                result.append(f' {name}="{value}"')
        return ''.join(result)

    def _convert_src(self, src):
        """将相对路径转换为 base64 data URI。如果图片找不到，保持原路径不变。"""
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            return src

        # 解析图片文件路径
        img_path = src
        if not os.path.isabs(img_path):
            # 尝试从 image_dir 解析
            candidate = os.path.join(self.image_dir, os.path.basename(img_path))
            if os.path.exists(candidate):
                img_path = candidate
            # 也尝试原始相对路径
            elif os.path.exists(img_path):
                img_path = img_path

        if not os.path.exists(img_path):
            print(f"  ⚠ 警告：找不到图片文件 '{src}'，保持原始引用", file=sys.stderr)
            return src

        if img_path in self.image_cache:
            encoded = self.image_cache[img_path]
        else:
            with open(img_path, 'rb') as f:
                data = f.read()
            encoded = base64.b64encode(data).decode('ascii')
            self.image_cache[img_path] = encoded
            self.embedded_count += 1
            self.total_size += len(data)

        ext = os.path.splitext(img_path)[1]
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
        encoded_kb = rewriter.total_size * 1.37 / 1024  # base64 ~37% overhead
        print(f"  Image raw size: {size_kb:.0f} KB")
        print(f"  Base64 encoded: ~{encoded_kb:.0f} KB")
    print(f"  Output: {os.path.abspath(output_path)}")


if __name__ == '__main__':
    main()
