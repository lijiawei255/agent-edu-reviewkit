# agent-edu-reviewkit 🎓

> A cross-platform AI assistant skill that converts course materials (PDF/PPTX/DOCX) into a **fully illustrated, high-quality HTML exam review document** with a single command.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Copilot%20%7C%20Codex%20%7C%20Kimi%20Code-green)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()

[中文版本](README.md)

---

## Table of Contents

- [What You Get](#what-you-get)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Supported Platforms](#supported-platforms)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## What You Get

**Input**: A folder containing courseware files (PDF/PPTX/DOCX)

**Output**: A single, self-contained HTML file featuring:

- 📋 Exam cover sheet (scope, format, instructor, textbook)
- 📖 Layered reading guide (multiple review paths for different skill levels)
- 📑 Clickable table of contents with anchor navigation
- 🗺️ Core concept mind map (inline SVG)
- 📌 Key concept deep dives (bilingual terminology, complete derivations)
- 🔑 Critical theorems and relationships
- 📐 Completed derivations (all "obviously", "it follows that", "we can easily prove" gaps filled in)
- ✏️ Worked examples (solution immediately follows each problem)
- 💡 Intuitive explanations (everyday analogies and mnemonics)
- 🖼️ Original courseware images + inline SVG diagrams
- 📋 Appendix A: Formula quick-reference cards
- 📋 Appendix B: Problem-solving templates
- 📋 Appendix C: Common mistakes and pitfalls
- 🖨️ Print-optimized stylesheet

---

## Prerequisites

### 1. Install an AI Coding Assistant

Choose and install any of the following:

| Assistant | Installation |
|-----------|-------------|
| **Claude Code** | [Official setup guide](https://docs.anthropic.com/en/docs/claude-code) |
| **GitHub Copilot** | [VS Code extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) or [JetBrains plugin](https://plugins.jetbrains.com/plugin/17718-github-copilot) |
| **OpenAI Codex CLI** | `npm install -g @openai/codex` |
| **Kimi Code** | [Official documentation](https://kimi.moonshot.cn/) |
| **Cursor** | [Download](https://cursor.sh/) |

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
3. Generating the HTML review document

The output is a single `.html` file — open it in any browser to read or print.

---

## Detailed Usage

### Workflow

The process has five phases:

```
Course files ──→ Phase 1: Scope ──→ Phase 2: Extraction ──→ Phase 3: Research
                                                                     │
                                                                     ▼
                         HTML document ←── Phase 5: QA ←── Phase 4: Generate
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
# 1. Edit the config section (line 44-46) to set your actual paths
# 2. Run the script
python extract_course_materials.py
```

The script automatically:
- Extracts text and images from all courseware files
- Detects pure-image files (scan-based PDFs) and flags them separately
- Inserts `[IMAGE: xxx.png]` markers in extracted text
- Produces a detailed extraction report

### Phase 3: Supplementary Research (Optional)

The AI searches for supplementary context from:
- GitHub (open course notes, problem solutions)
- Wikipedia (authoritative concept definitions)
- Academic tutorials

**All external content is used for reference only** — your course materials remain the primary source.

### Phase 4: HTML Generation

The AI produces a single-file HTML document with:
- **MathJax** rendering for all mathematical formulas (LaTeX)
- **Inline SVG** diagrams (flowcharts, block diagrams, comparison charts, plots)
- **Original courseware images** (via relative paths)
- **CSS styles** (responsive design + print media queries)

### Phase 5: Quality Assurance

The AI runs a 16-item checklist to verify completeness and correctness.

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

## Supported Platforms

| Platform | How to Use |
|----------|-----------|
| **Claude Code** | Native YAML frontmatter skill support — place in project `skills/` directory |
| **GitHub Copilot** | Use `skills/course-review-guide.md` content as `.github/copilot-instructions.md` |
| **OpenAI Codex CLI** | Load skill content as a custom System Prompt |
| **Kimi Code** | Load as Custom Instructions |
| **Cursor** | Place in `.cursor/rules/` directory |
| **Other assistants** | Copy skill content into the assistant's system prompt / custom instructions |

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

The HTML itself is compact — CSS and inline SVG add minimal weight. Courseware images are referenced by relative paths, not embedded as base64, keeping the file manageable. To share, bundle the HTML with the `extracted_images/` folder.

### Q: How do I print the review document?

The HTML includes `@media print` styles. Open in a browser and press `Ctrl+P` (or `Cmd+P`). Print styles automatically optimize font sizes and hide non-essential elements.

### Q: Which file formats are supported?

| Format | Extensions | Status |
|--------|-----------|--------|
| PDF | `.pdf` | ✅ Fully supported |
| PowerPoint | `.pptx`, `.pptm` | ✅ Fully supported |
| Word | `.docx`, `.dotx`, `.dotm` | ✅ Fully supported |
| Legacy PowerPoint | `.ppt` | ❌ Not supported — resave as `.pptx` |
| Legacy Word | `.doc` | ❌ Not supported — resave as `.docx` |

### Q: My course is taught in English. Will this work?

Yes. The skill supports bilingual output — key terms will appear in both English and Chinese. For English-only courses, mention this during the scope confirmation phase, and the AI will adjust accordingly.

---

## Contributing

Contributions are welcome! Here's how to get involved:

### Submitting an Issue

Please open an issue on [GitHub Issues](https://github.com/lijiawei255/agent-edu-reviewkit/issues) if you:
- Found a bug
- Have a feature request
- Want support for a new file format
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
