# agent-edu-reviewkit 🎓

> A cross-platform AI assistant skill that converts course materials (PDF/PPTX/DOCX) into a **fully illustrated, interactive HTML exam review document** with a single command.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20OpenCode%20%7C%20Codex%20%7C%20OpenClaw-green)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()

[中文版本](README.md)

---

## Table of Contents

- [What You Get](#what-you-get)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Interactive Learning Features](#interactive-learning-features)
- [Supported Platforms](#supported-platforms)
- [Autonomous Agent Support](#autonomous-agent-support)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## What You Get

**Input**: A folder containing courseware files (PDF/PPTX/DOCX)

**Output**: A single, self-contained interactive HTML file featuring:

- 📋 Exam cover sheet (scope, format, instructor, textbook)
- 📖 Layered reading guide (multiple review paths for different skill levels)
- 📑 Clickable table of contents with **progress tracking**
- 🔍 Full-text search and filter
- 🗺️ Core concept mind map (inline SVG)
- 📌 Key concept deep dives (bilingual terminology, complete derivations)
- 🔑 Critical theorems and relationships
- 📐 **Collapsible derivation steps** (click to expand, save space)
- ⚡📖 **Tabbed views** (Quick Review / Detailed Explanation switch)
- 🃏 **Flashcard flip cards** (click to flip — term on front, definition on back)
- 📝 **Practice quizzes** (concept checks with reveal-able answers)
- ✏️ Worked examples (solution immediately follows each problem)
- 💡 Intuitive explanations (everyday analogies and mnemonics)
- 🖼️ Original courseware images + inline SVG diagrams
- 📋 Appendix A: Formula quick-reference cards
- 📋 Appendix B: Problem-solving templates
- 📋 Appendix C: Common mistakes and pitfalls
- 🖨️ Print-optimized stylesheet (all interactive content auto-expands)

---

## Prerequisites

### 1. Install an AI Coding Assistant

Choose and install any of the following:

| Assistant | Installation | Interaction Mode |
|-----------|-------------|-----------------|
| **Claude Code** | [Official setup guide](https://docs.anthropic.com/en/docs/claude-code) | Full interactive |
| **OpenCode** | `npm install -g opencode-ai` | Full interactive |
| **OpenAI Codex CLI** | `npm install -g @openai/codex` | Full interactive |
| **GitHub Copilot** | [VS Code extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) | Full interactive |
| **Kimi Code** | [Official documentation](https://kimi.moonshot.cn/) | Full interactive |
| **OpenClaw/Hermes** | [Installation docs](https://docs.openclaw.ai/) | Autonomous |

### 2. Install Python (3.9 or later)

- **Windows**: Download from [python.org](https://www.python.org/downloads/), check "Add Python to PATH" during installation
- **macOS**: `brew install python@3`
- **Linux (Ubuntu/Debian)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora)**: `sudo dnf install python3 python3-pip`

Verify:

```bash
python --version   # Should show Python 3.9+
pip --version
```

### 3. Install Python Dependencies

```bash
pip install pypdf python-pptx python-docx
```

All three libraries are pure Python — no C compilation required. Just `pip install` and you're ready.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit
```

### 2. Prepare Your Course Materials

Place your courseware files (`.pdf`, `.pptx`, `.docx`, and variants) into a folder:

```
./my-courseware/
    ├── chapter1_intro.pdf
    ├── chapter2_fundamentals.pptx
    ├── chapter3_applications.docx
    └── ...
```

### 3. Invoke the Skill

**Claude Code users**:

Simply say:

```
Please help me create an exam review document from my course materials
```

Claude Code will automatically detect and load the skill from `skills/course-review-guide.md`. You can also trigger it explicitly:

```
/skill:course-review-guide
```

> Make sure to start Claude Code inside the project directory, or point it to the `skills/` directory.

**OpenCode users**:

The project includes an `opencode.json` config with a `course-review` custom agent. After starting OpenCode:

```
# Connect to your model provider, then:
@course-review Help me generate a review document, courseware is in [directory path]
```

> See `AGENTS.md` in the project root for platform-specific adaptations.

**Other AI assistant users**:

Load the contents of `skills/course-review-guide.md` as a system prompt or custom instruction.

**Universal approach (works on all platforms)**:

Send the following to your AI assistant:

```
Follow the instructions in skills/course-review-guide.md and help me
convert the course materials in [path/to/courseware] into an HTML exam review document.
```

### 4. Follow the Prompts

The AI will guide you through:
1. Confirming the courseware directory and exam scope
2. Running the extraction script (`extract_course_materials.py`)
3. Generating the interactive HTML review document
4. Running `embed_images.py` to get a self-contained HTML
5. (Optional) Generating an exam prediction document

The output is a single, self-contained `.html` file — open it in any browser to read or print.

---

## Detailed Usage

### Workflow

The process has six phases:

```
Course files ──→ Phase 1: Scope ──→ Phase 2: Extraction ──→ Phase 3: Research
                                                                     │
                                                                     ▼
                         HTML document ←── Phase 5: QA ←── Phase 4: Generate
                                                                     │
                                                                     ▼
                                                           Phase 6: Exam Prediction (optional)
```

### Phase 1: Scope Confirmation

The AI scans your courseware directory, lists all files, and confirms:
- Exam scope (which chapters are in/out)
- Course name, instructor, textbook
- Exam format (closed-book / open-book)
- Output filename

**Tip**: Prepare an exam scope list or syllabus file in advance.

### Phase 2: Content Extraction

The AI guides you to run `extract_course_materials.py`:

```bash
# 1. Edit the config section (lines 49-53) to set your actual paths
# 2. Run the script
python extract_course_materials.py
```

The script automatically:
- Extracts text and images from all courseware files
- Detects pure-image files (scan-based PDFs) and flags them separately
- Inserts `[IMAGE: xxx.png]` markers in extracted text
- Produces a detailed extraction report
- Detects `exam-scope.json` (if present) and outputs scope configuration

### Phase 3: Supplementary Research (Optional)

The AI searches for supplementary context from:
- GitHub (open course notes, problem solutions)
- Wikipedia (authoritative concept definitions)
- Academic tutorials

**All external content is used for reference only** — your course materials remain the primary source.

### Phase 4: HTML Generation

The AI produces a single-file **interactive** HTML document with:
- **MathJax** rendering for all mathematical formulas (LaTeX)
- **Inline SVG** diagrams (flowcharts, block diagrams, comparison charts, plots)
- **Original courseware images** (relative paths during generation, then base64-embedded via `embed_images.py`)
- **CSS styles** (responsive design + print queries + sticky sidebar ToC on wide screens)
- **Interactive components** (collapsible derivations, tabbed views, flashcards, quizzes, progress tracker, search)
- **Inline JavaScript** (no external dependencies, fully self-contained)

After generation, run `python embed_images.py <filename>.html` to inline all images, producing a fully self-contained HTML file.

### Phase 5: Quality Assurance

The AI runs a 25-item checklist to verify completeness and correctness, covering structure, interactivity, math rendering, and print compatibility.

### Phase 6: Exam Prediction (Optional)

After finishing the review document, the AI can generate an **exam prediction document** based on course content analysis — including high-frequency topic predictions, chapter exercises, a mock exam paper with solutions, helping students target weak areas before the exam.

### Image Recognition Capabilities

For pure-image courseware (scanned PDFs, image-only PPTX), this skill uses a **three-level fallback chain**:

| Priority | Approach | Description |
|----------|----------|-------------|
| 1 | Built-in model vision | Directly read image content (requires multimodal model: Claude Opus 4, GPT-4V, Gemini Pro Vision) |
| 2 | MCP vision server | Call vision tools via MCP protocol (e.g., MiniMax MCP) |
| 3 | User-guided resolution | Guide user to switch models, install MCP, or use local OCR (Tesseract) |

If your AI assistant lacks image recognition, switch to a vision-capable model or install an MCP vision server.

### Suitable Course Types

This skill is designed for **STEM exam review** and excels with:

- **Math-heavy courses**: Calculus, Linear Algebra, Probability Theory, Complex Analysis
- **Signal/Systems courses**: Digital Signal Processing, Signals & Systems, Communication Theory
- **Physics courses**: University Physics, Theoretical Mechanics, Quantum Mechanics
- **Programming/CS courses**: Data Structures, Algorithm Design, Machine Learning

It also works well for concept-heavy courses (biology, history, medicine), automatically adapting with more comparison tables, mnemonics, and mind maps.

---

## Interactive Learning Features

The generated HTML review document includes interactive learning components, inspired by recommendations from [Thariq's "Using Claude Code: The Unreasonable Effectiveness of HTML"](https://x.com/thariqk):

### Collapsible Derivation Steps

All mathematical derivations are collapsed by default — click to expand. Saves page space and lets students reveal detail on demand. All content auto-expands when printing.

### Tabbed Views

Each chapter has two tabs:
- **⚡ Quick Review**: Chapter summary, flashcard grid, key formula table
- **📖 Detailed Explanation**: Full derivations, worked examples, diagrams

### Flashcard Flip Cards

Core terminology flip cards — front shows the term, click to flip and see the definition or formula. Uses CSS 3D transform, works with both mouse and touch.

### Practice Quizzes

Each chapter ends with 2-4 concept check questions. Answers are hidden by default — click "Show answer" to reveal. Great for self-assessment.

### Progress Tracking

The sidebar ToC includes checkboxes. Mark completed sections, and the progress bar updates in real-time. Progress is saved in browser localStorage and survives page refreshes.

### Full-text Search

A search bar at the top of the content area lets you filter chapters by keyword — quickly find concepts or formulas you need.

### Print Compatibility

When printing, all interactive elements gracefully degrade: collapsed content expands, all tab panels show, flashcards render front+back, and search/progress controls hide.

---

## Supported Platforms

| Platform | Priority | Config File | Interaction Mode |
|----------|----------|-------------|-----------------|
| **Claude Code** | P0 | `CLAUDE.md` | Full interactive |
| **OpenAI Codex CLI** | P0 | Custom Prompt | Full interactive |
| **OpenCode** | P1 | `AGENTS.md`, `opencode.json` | Full interactive |
| **OpenClaw/Hermes** | P2 | `AGENTS.md` | Autonomous |
| **GitHub Copilot** | — | `.github/copilot-instructions.md` | Full interactive |
| **Kimi Code** | — | Custom Instructions | Full interactive |
| **Cursor** | — | `.cursor/rules/` | Full interactive |

Platform-specific adaptations are documented in `AGENTS.md`.

---

## Autonomous Agent Support

OpenClaw, Hermes, and other Claw-type autonomous agents run fully automatically **without guaranteed turn-based user interaction**. This skill includes dedicated adaptations for autonomous mode.

### exam-scope.json Configuration

Place an `exam-scope.json` file in your courseware directory. Autonomous agents will read it and skip interactive scope confirmation:

```json
{
  "course_name_zh": "数字信号处理",
  "course_name_en": "Digital Signal Processing",
  "instructor": "John Smith",
  "textbook": "Digital Signal Processing, 4th Edition",
  "exam_type": "Closed-book",
  "language": "zh",
  "chapters_in_scope": ["Chapter 1", "Chapter 2", "Chapter 3"],
  "chapters_excluded": ["Chapter 6"],
  "output_filename": "DSP_Final_Review.html"
}
```

A template is provided at `exam-scope-template.json` in the project root.

### Three-Level Scope Determination

| Level | Method | Interaction Required | Reliability |
|-------|--------|---------------------|-------------|
| 1 | Read `exam-scope.json` | None | High |
| 2 | Infer scope from filenames | None | Medium |
| 3 | Request via messaging channel | Yes (async) | High |

### Auto-Inference Mode

If `exam-scope.json` is not found, the autonomous agent will infer the chapter scope from courseware filenames. The generated HTML will display a prominent **autonomous mode banner** at the top, reminding users to verify the exam scope. The agent also auto-generates an `exam-scope-template.json` (with inferred defaults) in the courseware directory for the user to fill in next time.

See `AGENTS.md` for detailed adaptation instructions.

---

## FAQ

### Q: My courseware is scan-based PDFs (pure images) with no text layers. What do I do?

If scan quality is decent, the AI's vision capability can recognize content from images. If your current model lacks vision:
1. Switch to a multimodal model (Claude Opus 4, GPT-4V, etc.)
2. Install an MCP vision server
3. Pre-process with OCR (Tesseract): `pip install pytesseract pdf2image`

### Q: Formulas are garbled or incomplete after extraction?

PDF text extraction can damage formulas. This skill automatically detects and fixes 6 common formula issues (fragmentation, symbol loss, fraction bar loss, superscript/subscript misplacement, matrix corruption, function name errors). All formulas are re-typeset in LaTeX for correct HTML rendering.

### Q: The generated HTML file is too large?

CSS and inline SVG add minimal weight. After running `embed_images.py` to base64-embed images, the file grows (about 1.37× total image size) but becomes fully self-contained — ideal for sharing. If the file is too large, skip embedding and bundle the HTML with the `extracted_images/` folder instead.

### Q: How do I share and print the review document?

- **Share**: Run `python embed_images.py <filename>.html` to get a `_embedded.html` with all images inlined — one file is all you need
- **Print**: Open the HTML in a browser and press `Ctrl+P` (or `Cmd+P`). Built-in `@media print` styles auto-expand all collapsed content and optimize the layout

### Q: Do the interactive features (flashcards, quizzes) require internet?

No. All interactive features use pure HTML/CSS/JavaScript with no external JS dependencies. The only thing requiring internet is MathJax formula rendering (see offline workaround below).

### Q: Will my learning progress be lost?

Progress is saved in the browser's localStorage and survives page refreshes. Note: progress is tied to the file path — moving the file to a different location will reset it.

### Q: Which file formats are supported?

| Format | Extensions | Status |
|--------|-----------|--------|
| PDF | `.pdf` | ✅ Fully supported |
| PowerPoint | `.pptx`, `.pptm` | ✅ Fully supported |
| Word | `.docx`, `.dotx`, `.dotm` | ✅ Fully supported |
| Legacy PowerPoint | `.ppt` | ❌ Not supported — resave as `.pptx` |
| Legacy Word | `.doc` | ❌ Not supported — resave as `.docx` |

### Q: How do I view formulas without internet access?

The generated HTML loads formula rendering from the MathJax CDN, which requires internet. For offline use:
1. **Print to PDF**: Open the HTML in a browser with internet, then use "Print → Save as PDF"
2. **Local MathJax**: Download the full MathJax package from [GitHub](https://github.com/mathjax/MathJax), extract to a `mathjax/` folder next to the HTML file, and change the MathJax `<script>` `src` to `./mathjax/es5/tex-svg.js`

### Q: My course is taught in English. Will this work?

Yes. The skill supports bilingual output — key terms will appear in both English and Chinese. For English-only courses, mention this during the scope confirmation phase, and the AI will adjust accordingly.

### Q: How do I use OpenClaw/Hermes to autonomously generate a review document?

1. Create `exam-scope.json` in your courseware directory (use `exam-scope-template.json` as a template)
2. Clone this project to a location accessible by OpenClaw
3. The OpenClaw agent will read instructions from `AGENTS.md` and execute all phases automatically
4. After generation, check the autonomous mode banner at the top of the document to verify the exam scope

---

## Contributing

Contributions are welcome! Here's how to get involved:

### Submitting an Issue

Please open an issue on [GitHub Issues](https://github.com/lijiawei255/agent-edu-reviewkit/issues) if you:
- Found a bug
- Have a feature request
- Want support for a new file format or AI platform
- Have questions about usage

### Submitting a Pull Request

1. **Fork** the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Pre-commit checklist**:
- [ ] Changes follow existing code style
- [ ] `extract_course_materials.py` tested on Python 3.9+
- [ ] New features are documented
- [ ] No test courseware or output files included (these are excluded via `.gitignore`)

### Local Development

```bash
# Clone
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit

# Install dependencies
pip install pypdf python-pptx python-docx

# Test courseware and output directories are auto-excluded by .gitignore
# Place test materials in 测试课件(不提交)/ directory
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 Jiawei Li
