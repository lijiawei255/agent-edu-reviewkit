#!/usr/bin/env python3
"""
图片智能匹配工具 —— 根据文本上下文匹配提取的课件图片

功能:
1. 解析提取的文本中的 [图片: xxx.png] 标记
2. 提取每张图片的上下文文字（前后各3段）
3. 为每张图片生成内容描述和分类标签
4. 输出图片-章节匹配关系JSON
5. 支持交互式确认图片与章节的对应关系

使用方法:
  python match_images.py --text-dir extracted_text --image-dir extracted_images
  python match_images.py --text-dir extracted_text --output mapping.json
  python match_images.py --interactive  # 交互式确认模式
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict


# 图片类型关键词映射（用于上下文分类）
IMAGE_TYPE_KEYWORDS = {
    'diagram': [
        '框图', '流程图', '示意图', '结构图', '架构图', '系统图',
        'block', 'diagram', 'flowchart', 'structure', 'architecture'
    ],
    'waveform': [
        '波形', '频谱', '时域', '频域', '曲线', '响应',
        'waveform', 'spectrum', 'frequency', 'time domain', 'response'
    ],
    'formula': [
        '公式', '推导', '证明', '定理', '方程',
        'formula', 'equation', 'derive', 'proof', 'theorem'
    ],
    'example': [
        '例题', '例子', '示例', '解答', '计算',
        'example', 'sample', 'solution', 'calculation'
    ],
    'comparison': [
        '对比', '比较', '区别', 'vs', 'versus',
        'comparison', 'difference', 'contrast'
    ],
    'model': [
        '模型', '物理', '几何', '空间',
        'model', 'physics', 'geometry', 'spatial'
    ],
}


def parse_image_markers(text_content):
    """
    解析文本中的 [图片: xxx.png] 标记
    返回: list of (image_filename, context_before, context_after, line_number)
    """
    lines = text_content.split('\n')
    results = []

    for i, line in enumerate(lines):
        match = re.search(r'\[图片:\s*([^\]]+)\]', line)
        if match:
            filename = match.group(1).strip()

            # 提取前后各3段上下文
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            context_before = '\n'.join(lines[start:i]).strip()
            context_after = '\n'.join(lines[i+1:end]).strip()

            results.append({
                'filename': filename,
                'context_before': context_before,
                'context_after': context_after,
                'line_number': i + 1,
                'combined_context': f"{context_before}\n{context_after}".strip()
            })

    return results


def classify_image_by_context(context_text):
    """
    根据上下文文字判断图片类型
    返回: dict {type: score} 按分数降序
    """
    scores = defaultdict(int)
    text_lower = context_text.lower()

    for img_type, keywords in IMAGE_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[img_type] += 1

    # 排序
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_scores) if sorted_scores else {'unknown': 0}


def extract_chapter_info(context_text):
    """
    从上下文中尝试提取章节信息
    """
    # 常见章节标题模式
    patterns = [
        r'第[零一二三四五六七八九十\d]+章',
        r'Chapter\s*\d+',
        r'第\s*[零一二三四五六七八九十\d]+\s*节',
        r'Section\s*\d+',
        r'\d+\.\d+',  # 1.1, 2.3.4 等编号
    ]

    for pattern in patterns:
        match = re.search(pattern, context_text)
        if match:
            return match.group(0)

    return None


def analyze_all_images(text_dir, image_dir=None):
    """
    分析所有提取的文本文件，建立图片映射
    """
    all_images = {}
    chapter_mapping = defaultdict(list)
    stats = {
        'total_markers': 0,
        'files_processed': 0,
        'images_by_type': defaultdict(int),
    }

    text_path = Path(text_dir)
    if not text_path.exists():
        print(f"错误：文本目录不存在: {text_dir}", file=sys.stderr)
        return None

    # 处理所有 .txt 文件
    for txt_file in sorted(text_path.glob('*.txt')):
        stats['files_processed'] += 1
        print(f"处理: {txt_file.name}")

        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        markers = parse_image_markers(content)
        stats['total_markers'] += len(markers)

        for marker in markers:
            filename = marker['filename']

            # 分类图片
            type_scores = classify_image_by_context(marker['combined_context'])
            primary_type = next(iter(type_scores.keys()), 'unknown')
            stats['images_by_type'][primary_type] += 1

            # 提取章节信息
            chapter = extract_chapter_info(marker['combined_context'])

            image_info = {
                'filename': filename,
                'source_file': txt_file.name,
                'line_number': marker['line_number'],
                'context_preview': marker['combined_context'][:200] + '...' if len(marker['combined_context']) > 200 else marker['combined_context'],
                'image_type': primary_type,
                'type_scores': dict(type_scores),
                'chapter_hint': chapter,
                'confidence': max(type_scores.values()) if type_scores else 0,
            }

            all_images[filename] = image_info

            # 按章节分组
            if chapter:
                chapter_mapping[chapter].append(filename)
            else:
                chapter_mapping['未分类'].append(filename)

    # 检查图片文件是否存在
    if image_dir:
        image_path = Path(image_dir)
        if image_path.exists():
            existing_files = set(f.name for f in image_path.iterdir() if f.is_file())
            for img_name in list(all_images.keys()):
                all_images[img_name]['file_exists'] = img_name in existing_files
                if not all_images[img_name]['file_exists']:
                    all_images[img_name]['status'] = 'missing'

    result = {
        'images': all_images,
        'chapter_mapping': dict(chapter_mapping),
        'stats': dict(stats),
    }

    return result


def print_analysis_report(result):
    """
    打印分析报告
    """
    print("\n" + "=" * 70)
    print("📊 图片智能匹配分析报告")
    print("=" * 70)

    stats = result['stats']
    print(f"\n  📁 处理文件数: {stats['files_processed']}")
    print(f"  🖼 发现图片标记: {stats['total_markers']}")

    print("\n  📋 图片类型分布:")
    for img_type, count in sorted(stats['images_by_type'].items(), key=lambda x: x[1], reverse=True):
        type_names = {
            'diagram': '🔵 概念示意图',
            'waveform': '🟢 波形频谱图',
            'formula': '🔴 公式推导图',
            'example': '🟡 例题配图',
            'comparison': '💜 对比分析图',
            'model': '🧩 物理模型图',
            'unknown': '❓ 未知类型',
        }
        label = type_names.get(img_type, img_type)
        print(f"    {label}: {count} 张")

    print("\n  📚 章节映射概览:")
    for chapter, images in sorted(result['chapter_mapping'].items()):
        print(f"    {chapter}: {len(images)} 张")

    # 检查缺失文件
    missing = [img for img, info in result['images'].items() if not info.get('file_exists', True)]
    if missing:
        print(f"\n  ⚠️  缺失图片文件 ({len(missing)} 张):")
        for m in missing[:10]:
            print(f"    - {m}")
        if len(missing) > 10:
            print(f"    ... 还有 {len(missing) - 10} 张")

    print("\n" + "=" * 70)


def interactive_confirmation(result):
    """
    交互式确认模式
    """
    print("\n" + "=" * 70)
    print("🤝 交互式图片-章节匹配确认")
    print("=" * 70)
    print("\n提示: 检查每张图片的上下文描述，确认章节归属是否正确。")
    print("      输入 y 确认，n 修正，s 跳过，q 退出。\n")

    confirmed = {}
    need_review = []

    for i, (filename, info) in enumerate(result['images'].items(), 1):
        print(f"\n[{i}/{len(result['images'])}] {filename}")
        print(f"  推测类型: {info.get('image_type', 'unknown')}")
        print(f"  推测章节: {info.get('chapter_hint', '未分类')}")
        print(f"  上下文预览: {info.get('context_preview', '')[:150]}")

        while True:
            resp = input("  确认正确？[y(是)/n(修正)/s(跳过)/q(退出)]: ").strip().lower()
            if resp == 'y':
                confirmed[filename] = {**info, 'reviewed': True, 'status': 'confirmed'}
                break
            elif resp == 'n':
                new_chapter = input("  输入正确章节（如 '第3章'）: ").strip()
                if new_chapter:
                    info['chapter_hint'] = new_chapter
                    info['user_override'] = True
                confirmed[filename] = {**info, 'reviewed': True, 'status': 'user_corrected'}
                break
            elif resp == 's':
                confirmed[filename] = {**info, 'reviewed': False, 'status': 'skipped'}
                break
            elif resp == 'q':
                print("\n用户退出。")
                return confirmed
            else:
                print("  请输入 y/n/s/q")

    print(f"\n✅ 完成！已确认 {len([v for v in confirmed.values() if v.get('reviewed')])} 张图片")
    return confirmed


def main():
    parser = argparse.ArgumentParser(
        description='图片智能匹配工具 —— 根据文本上下文匹配提取的课件图片'
    )
    parser.add_argument('--text-dir', default='extracted_text',
                        help='提取的文本文件目录（默认: extracted_text）')
    parser.add_argument('--image-dir', default='extracted_images',
                        help='提取的图片文件目录（默认: extracted_images）')
    parser.add_argument('--output', '-o', default='image_mapping.json',
                        help='输出JSON文件路径（默认: image_mapping.json）')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='交互式确认模式')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='安静模式，不输出详细报告')
    args = parser.parse_args()

    # 执行分析
    result = analyze_all_images(args.text_dir, args.image_dir)
    if result is None:
        sys.exit(1)

    # 输出报告
    if not args.quiet:
        print_analysis_report(result)

    # 交互式确认
    if args.interactive:
        confirmed = interactive_confirmation(result)
        result['images'] = confirmed
        result['stats']['user_confirmed'] = len(confirmed)

    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if not args.quiet:
        print(f"\n📄 匹配结果已保存到: {os.path.abspath(args.output)}")
        print("\n💡 使用提示:")
        print("  - 在生成复习文档时，参考此JSON文件按章节嵌入图片")
        print("  - 优先嵌入 confidence 高的图片")
        print("  - 对于 missing 状态的图片，使用SVG作为后备")


if __name__ == '__main__':
    main()
