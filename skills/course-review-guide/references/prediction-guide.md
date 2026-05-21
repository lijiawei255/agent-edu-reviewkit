# 考试押题文档生成指南

## 文档定位

押题文档是**独立HTML文件**（不追加到复习文档），用于考前针对性练习和查漏补缺。采用试卷风格排版（衬线字体、极简布局、打印时隐藏解答）。

## HTML模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[课程名] 考试押题文档</title>
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']], tags: 'ams' },
  svg: { fontCache: 'global' }
};
</script>
<script id="MathJax-script" async src="./mathjax/es5/tex-svg.js"
        onerror="var cdn=document.createElement('script');cdn.id='MathJax-script';cdn.async=true;
        cdn.src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
        this.remove();document.head.appendChild(cdn);"></script>
<style>
  :root { --primary: #1a1a2e; --bg: #fafaf9; --text: #1a1a2e; --border: #d1d5db; --radius: 8px; }
  body {
    font-family: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
    color: var(--text);
    background: #f5f5f0;
    line-height: 1.9;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }
  h1 { text-align: center; font-size: 1.8rem; margin-bottom: 0.5rem; }
  h2 {
    border-bottom: 2px solid #333;
    padding-bottom: 0.3rem;
    margin: 2.5rem 0 1rem;
    font-size: 1.3rem;
  }
  h3 { margin: 1.5rem 0 0.8rem; font-size: 1.1rem; }
  .meta { text-align: center; color: #666; margin-bottom: 2rem; font-size: 0.9rem; }
  .section {
    background: #fff;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1.5rem 0;
  }

  /* 题目样式 */
  .question { margin: 1.2rem 0; padding: 1rem; background: #fafaf5; border-radius: var(--radius); border-left: 3px solid #2563eb; }
  .question.fill-blank { border-left-color: #16a34a; }
  .question.calculation { border-left-color: #dc2626; }
  .question.short-answer { border-left-color: #d97706; }
  .q-label { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; margin-right: 0.5rem; }
  .q-label-choice { background: #dbeafe; color: #1e40af; }
  .q-label-fill { background: #dcfce7; color: #166534; }
  .q-label-calc { background: #fee2e2; color: #991b1b; }
  .q-label-short { background: #fef3c7; color: #92400e; }

  /* 解答样式 */
  details.solution {
    margin: 0.8rem 0;
    padding: 0.8rem 1rem;
    background: #f0f9ff;
    border: 1px dashed #3b82f6;
    border-radius: 8px;
  }
  details.solution summary { cursor: pointer; font-weight: 600; color: #2563eb; user-select: none; }
  .solution-content { padding-top: 0.5rem; }

  /* 评分要点 */
  .scoring { background: #fefce8; border: 1px solid #eab308; border-radius: 4px; padding: 0.5rem 0.8rem; margin: 0.5rem 0; font-size: 0.85rem; }

  /* 易错提示 */
  .common-mistake { background: #fef2f2; border-left: 3px solid #ef4444; padding: 0.5rem 0.8rem; margin: 0.5rem 0; font-size: 0.85rem; }

  /* 预测标签 */
  .prediction-badge { display: inline-block; padding: 0.15em 0.5em; border-radius: 10px; font-size: 0.75rem; font-weight: bold; }
  .high { background: #fee2e2; color: #991b1b; }
  .medium { background: #fef3c7; color: #92400e; }
  .low { background: #dcfce7; color: #166534; }

  .chapter-ref { font-size: 0.85rem; color: #666; margin-top: 0.3rem; }
  pre { background: #1e293b; color: #e2e8f0; padding: 1rem; border-radius: 8px; overflow-x: auto; font-size: 0.9rem; }
  table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
  th, td { border: 1px solid var(--border); padding: 0.5rem 0.8rem; text-align: left; }
  th { background: #f0f0f0; font-weight: 600; }

  @media print {
    body { background: #fff; font-size: 12pt; }
    h1 { font-size: 18pt; }
    details.solution { display: none; }
    .section { border: 1px solid #ccc; break-inside: avoid; }
    .question { break-inside: avoid; }
  }
</style>
</head>
<body>
```

## 文档结构

```html
<h1>📝 [课程名] 考试押题文档</h1>
<div class="meta">
  <p>[考试类型] | 基于[N]份课件内容分析 | [生成日期]</p>
  <p><strong>题型分布预测</strong>：[按用户指定的比例]</p>
</div>

<!-- 1. 押题概述 -->
<div class="section">
<h2>📊 押题概述与出题概率</h2>
<table>
  <tr><th>章节</th><th>出题概率</th><th>主要题型</th><th>预测依据</th></tr>
  <tr>
    <td>[章节名]</td>
    <td><span class="prediction-badge high">🔴 极高</span></td>
    <td>[题型]</td>
    <td>[预测理由——基于课件内容的具体分析]</td>
  </tr>
  <!-- 每章一行 -->
</table>
</div>

<!-- 2. 分章节押题 -->
<div class="section">
<h2>🎯 分章节重点押题</h2>

<h3>[章节名] <span class="prediction-badge high">🔴 极高</span></h3>
<p><strong>高频考点</strong>：[概念名]——预测理由：[具体原因]，可能出题形式：[选择/填空/计算]</p>
<!-- 每章2-4道重点推导题和概念应用题 -->
</div>

<!-- 3. 模拟试卷 -->
<div class="section">
<h2>📋 第一部分：选择题（15-20题）</h2>

<div class="question">
<p><span class="q-label q-label-choice">Q1</span> <strong>[题目主题]</strong></p>
<p>[完整题干，所有选项]</p>
<details class="solution"><summary>答案与解析</summary>
<div class="solution-content">
  <p><strong>[正确答案]</strong></p>
  <p>[详细解析——不只是选哪个，还要解释为什么对、为什么错]</p>
  <p class="chapter-ref">考点来源：[课件文件] [页码/幻灯片]</p>
  <div class="common-mistake"><strong>⚠ 常见错误</strong>：[学生容易选错的选项及原因]</div>
</div>
</details>
</div>
<!-- 以此类推 -->
</div>

<div class="section">
<h2>📝 第二部分：填空题（10-15题）</h2>

<div class="question fill-blank">
<p><span class="q-label q-label-fill">Q16</span> [题目描述，空白处用 <strong>______</strong> 表示]</p>
<details class="solution"><summary>答案</summary>
<div class="solution-content">
  <p><strong>[答案]</strong></p>
  <p>[解析]</p>
  <p class="chapter-ref">考点来源：[课件文件]</p>
</div>
</details>
</div>
<!-- 以此类推 -->
</div>

<div class="section">
<h2>🔢 第三部分：计算题（5-8题）</h2>

<div class="question calculation">
<p><span class="q-label q-label-calc">Q26</span> <strong>[题目主题]（[分值]分）</strong></p>
<p>[完整题目描述，包含所有已知条件和所求]</p>
<details class="solution"><summary>答案与解析</summary>
<div class="solution-content">
  <p><strong>(1)</strong> [第一问解答]</p>
  <p>$$[完整计算过程]$$</p>
  <p><strong>(2)</strong> [第二问解答]...</p>
  <p>$$\boxed{[最终结果]}$$</p>
  <div class="scoring">
    <strong>📊 评分要点</strong>：
    <br>• 步骤1（X分）：[评分要求]
    <br>• 步骤2（X分）：[评分要求]
    <br>• 最终结果（X分）：[评分要求]
    <br>• 总计：[总分]分
  </div>
  <div class="common-mistake"><strong>⚠ 常见错误</strong>：[2-3个常见错误及避免方法]</div>
  <p class="chapter-ref">考点来源：[课件文件] [页码]，对应[Tutorial/作业]第X题</p>
</div>
</details>
</div>
<!-- 以此类推 -->
</div>

<!-- 4. 押题依据表 -->
<div class="section">
<h2>📋 押题依据表</h2>
<table>
  <tr><th>题号</th><th>知识点</th><th>对应课件</th><th>出题理由</th></tr>
  <tr>
    <td>Q1</td>
    <td>[知识点]</td>
    <td>[文件名] [页码]</td>
    <td>[为什么预测这道题——课件标注重点？历年常考？核心基础？]</td>
  </tr>
  <!-- 每一题一行 -->
</table>
</div>

</body>
</html>
```

## 题目数量标准

| 题型 | 最少数量 | 推荐数量 | 说明 |
|------|---------|---------|------|
| 选择题 | 15道 | 20道 | 覆盖所有考试章节，每章至少1道 |
| 填空题 | 10道 | 15道 | 覆盖关键公式和概念 |
| 计算题 | 5道 | 8道 | 覆盖主要计算类型，每类至少1道 |
| 简答题（如适用）| 3道 | 5道 | 概念对比、原理解释 |

**总计不少于30道题，推荐40道以上。**

## 每题质量标准

每道题必须包含以下要素：

### 选择题
- [ ] 题干清晰，4个选项（不要3个或5个，保持统一）
- [ ] 选项之间有明显区分度（不要让两个选项过于相似）
- [ ] 错误选项有"陷阱"——对应常见错误理解
- [ ] 解析说明：为什么正确选项是对的、其他选项为什么错
- [ ] 考点来源标注

### 填空题
- [ ] 填空位置合理（填关键公式、参数、概念名）
- [ ] 答案唯一确定（不要有歧义）
- [ ] 解析包含计算或推理过程
- [ ] 考点来源标注

### 计算题
- [ ] 题目有实际工程/物理背景（不只是纯数学运算）
- [ ] 包含多步求解（2-4个子问题，层层递进）
- [ ] 详细解答包含：每一步的完整表达式 + 为什么这一步
- [ ] **评分要点**：各步骤分值分配
- [ ] **常见错误预判**：至少2个
- [ ] 最终结果 `\boxed{}`
- [ ] 考点来源标注（含课件页码）

## 公式格式（押题文档适用）

- `$$` 独立公式块单独成行，成对出现
- 行内公式用 `$...$`
- 中文说明放在 `$$` 块外部
- 所有答案和解析在 `<details class="solution">` 中（默认折叠）
