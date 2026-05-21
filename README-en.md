# agent-edu-reviewkit 🎓 STEM Exam Review Generator

> ✨ **Cross-platform Agent skill that automatically converts STEM course materials (PDF/PPTX/DOCX) into single-file, self-contained interactive HTML review guides + exam predictions.**
> Supports math, physics, circuits, computer science, mechanical engineering, signal processing, and all STEM subjects — no coding required, just chat with AI.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20OpenCode%20%7C%20Codex%20%7C%20OpenClaw-green)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()

[中文版本](README.md)

---

## 🌟 Core Features

| Feature | Description |
|---------|-------------|
| ✅ **All STEM Subjects Supported** | Math, physics, circuits, CS, mechanical engineering, signal processing, and more |
| ✅ **Smart Image Matching** | Context-based image-chapter intelligent matching, prioritize original courseware images — 8-10 per chapter |
| ✅ **Multi-Level Vision Fallback** | Model vision → MCP vision server → user guidance, ensures image content accuracy |
| ✅ **Image Quality Detection** | Auto-analyze image quality, deduplication, report missing and low-quality images |
| ✅ **Multi-Platform Compatible** | Works with Claude Code, OpenCode, OpenClaw, Hermes, Kimi Code, Copilot |
| ✅ **Single Self-Contained File** | All CSS/JS/images/MathJax inline — zero dependencies, just double-click and use |
| ✅ **Interactive Learning** | Flashcards (double-click protection), search, collapsible derivations, progress tracking, quizzes, tabbed views |
| ✅ **Print-Friendly** | Optimized print styles for paper-based studying |
| ✅ **Exam Predictions** | Auto-generated practice questions based on course content analysis |
| ✅ **Autonomous Mode** | Fully automated, non-interactive operation for batch processing |

## 📚 Supported Subjects

| Subject Category | Example Courses | SVG Visualization Types |
|------------------|----------------|------------------------|
| 📐 Mathematics | Calculus, Linear Algebra, Probability, Complex Analysis | Function plots, integral areas, vector spaces, series expansions |
| ⚛️ Physics | Mechanics, Electromagnetism, Optics, Thermodynamics | Force diagrams, field lines, ray tracing, thermodynamic cycles |
| 🔌 Circuits & Electronics | Circuit Analysis, Analog/Digital Electronics, Signals & Systems | Schematics, timing diagrams, Bode plots, state transitions |
| 💻 Computer Science | Data Structures, Algorithms, Operating Systems, Networks | Structure diagrams, flowcharts, state machines, network topologies |
| 🏗️ Engineering | Control Theory, Mechanical Principles, Civil Structures | Control block diagrams, mechanical models, signal flow graphs |
| 📡 Signal Processing | DSP, Communications, Image Processing | (Original DSP functionality fully preserved) |

Concept-memorization courses (Biology, History, Medicine) also work — skill automatically adds comparison tables, mnemonics, and mind maps.

---

## Table of Contents

- [Key Terms (Quick Overview)](#key-terms-quick-overview)
- [What You Need](#what-you-need)
- [Quick Start (Simplest Way)](#quick-start-simplest-way)
- [What You Get](#what-you-get)
- [Detailed Usage](#detailed-usage)
- [Alternative Skill: Chapter Notes](#alternative-skill-chapter-notes)
- [Interactive Learning Features](#interactive-learning-features)
- [Supported Platforms](#supported-platforms)
- [Autonomous Agent Support](#autonomous-agent-support)
- [Privacy & Security](#privacy--security)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Key Terms (Quick Overview)

If you're new to AI coding tools, here's what some terms mean:

| Term | Plain-English Explanation |
|------|--------------------------|
| **AI Assistant / AI Coding Assistant** | A program you chat with that can run code and generate files (e.g., Claude Code, ChatGPT, GitHub Copilot) |
| **Skill** | A set of pre-written instructions telling the AI "what to do for a specific task." This project's skill is "turn courseware into a review document" |
| **HTML** | A web page file. Double-click an `.html` file to open it in your browser, with text, images, formulas, and animations |
| **Python** | A programming language. You need it to run helper scripts (very simple steps, see below) |
| **Terminal / Command Line** | A text window where you type a few commands (like `pip install`). Just copy and paste — no programming knowledge needed |
| **pip** | Python's "app store" for installing tools |
| **git clone** | Downloading a project from GitHub. If you don't use git, just download the ZIP from the webpage |
| **CDN** | A public file hosting service on the internet. The generated doc loads a math rendering engine from CDN (can also work offline, see FAQ) |
| **LaTeX** | Standard notation for math formulas. E.g., `$E = mc^2$` gets rendered as a beautifully typeset equation |

---

## What You Need

Before starting, make sure you have:

### Required

| Item | Notes |
|------|-------|
| **Computer** | Windows, macOS, or Linux |
| **Python 3.9+** | To run extraction scripts. Installation guide below |
| **Course materials** | PDF (`.pdf`), PowerPoint (`.pptx`, `.pptm`), Word (`.docx`, `.dotx`, `.dotm`) |
| **An AI assistant** | See "Choose an AI Assistant" below |
| **Internet connection** | For downloading dependencies and chatting with AI. Formula rendering also needs internet (or pre-download MathJax for offline use — see FAQ) |
| **~50 MB disk space** | For extracted text, images, and the final HTML file |

### Optional

| Item | Notes |
|------|-------|
| **Git** | For cloning the project. If you don't use git, just download as ZIP from GitHub |
| **Node.js** | Only needed for OpenCode or Codex CLI. Not needed for Claude Code, web-based AI, or other assistants |

### Install Python

- **Windows**: Download from [python.org](https://www.python.org/downloads/) — **check** "Add Python to PATH" during installation
- **macOS**: `brew install python@3`
- **Linux (Ubuntu/Debian)**: `sudo apt install python3 python3-pip`
- **Linux (Fedora)**: `sudo dnf install python3 python3-pip`

Verify:

```bash
python --version   # Should show Python 3.9+
pip --version
```

### Choose an AI Assistant

| Assistant | Installation | Interaction Mode | Best For |
|-----------|-------------|-----------------|----------|
| **Claude Code** | [Official setup guide](https://docs.anthropic.com/en/docs/claude-code) | Full interactive | Recommended. Most complete experience |
| **OpenCode** | `npm install -g opencode-ai` | Full interactive | Open-source enthusiasts |
| **OpenAI Codex CLI** | `npm install -g @openai/codex` | Full interactive | Existing OpenAI users |
| **GitHub Copilot** | [VS Code extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) | Full interactive | VS Code + Copilot users |
| **Kimi Code** | [Official docs](https://kimi.moonshot.cn/) | Full interactive | Users in China |
| **OpenClaw/Hermes** | [Installation docs](https://docs.openclaw.ai/) | Autonomous | Fully automated workflow |

> 💡 **Don't have an AI coding assistant?** You can simply copy-paste the contents of `skills/course-review-guide/SKILL.md` into any AI chat tool (ChatGPT, Kimi Chat, DeepSeek, etc.) and tell it to generate a review document. This is the simplest path — see Quick Start below.

---

## Quick Start (Simplest Way)

### Step 1: Download the Project

**Option A (Recommended): Download ZIP from GitHub**
1. Go to https://github.com/lijiawei255/agent-edu-reviewkit
2. Click the green "<> Code" button → "Download ZIP"
3. Extract to a folder of your choice

**Option B (If you use git):**
```bash
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit
```

### Step 2: Install Python Dependencies

Open a terminal (PowerShell or Command Prompt on Windows), navigate to the project folder, and run:

```bash
pip install -r requirements.txt
```

This installs all required Python packages (`pypdf`, `python-pptx`, `python-docx`) — pure Python, no extra tools needed.

### Step 3: Prepare Your Course Materials

Place your courseware files in a folder:

```
./my-courseware/
    ├── chapter1_intro.pdf
    ├── chapter2_fundamentals.pptx
    ├── chapter3_applications.docx
    └── ...
```

### Step 4: Tell Your AI Assistant What to Do

**🌐 Universal approach (works with all AI platforms — simplest):**

Open your AI assistant (Claude Code, ChatGPT, Kimi Chat, etc.) and say:

> Follow the instructions in skills/course-review-guide/SKILL.md and help me convert the course materials in [path/to/courseware] into an HTML exam review document.

If you're using a chat-style AI (not a coding assistant), paste the contents of `skills/course-review-guide/SKILL.md` into the conversation first.

**🤖 Claude Code users (recommended):**

Start Claude Code inside the project directory and say:

```
Please help me create an exam review document from my course materials
```

Claude Code auto-detects the skill. Or trigger explicitly: `/skill:course-review-guide`

**🔧 OpenCode users:**

```
@course-review Help me generate a review document, courseware is in [directory path]
```

### Step 5: Follow the AI's Prompts

The AI will guide you through:
1. Confirming the exam scope (which chapters are included)
2. Running the extraction script (the AI will tell you the exact command)
3. Running `match_images.py --interactive` to intelligently match images to chapters
4. Generating the interactive HTML review document
5. Running `python embed_images.py <filename>.html` to inline all images
6. (Optional) Running `python setup_mathjax.py` to download the math engine for offline formula viewing
7. (Optional) Generating an exam prediction document

The output is a single `.html` file — double-click to open in your browser and start studying.

---

## What You Get

**Input**: A folder of courseware files (PDF/PPTX/DOCX)

**Output**: A single, self-contained interactive HTML file, **designed for students with weak foundations**, featuring:

### 📚 Enhanced Content Depth (Beginner-Friendly)
- 🔴 **5-Layer Concept Explanation**: Each core concept includes Definition → Diagram → Physical Meaning → Math Breakdown → Applicability Conditions
- 🔴 **Ultra-Detailed Derivations**: Each derivation has at least 5 steps, with "why this step" explanations — no skipped steps!
- 🔴 **Symbol Annotations**: Every mathematical symbol includes meaning, unit, and value range on first appearance
- 🔴 **Comprehensive Computational Problems**: At least one major problem per chapter, including exam point analysis, strategy selection, detailed steps, verification methods, and common error warnings
- 🔴 **Applicability & Limitations**: Every formula clearly lists when it works and common misapplication scenarios

### 🖼️ Smart Courseware Image Embedding
- 🔴 **At least 8-10 original courseware images per chapter**, every core concept has a corresponding image
- Context-based intelligent matching: extracts surrounding text to auto-classify and link images to chapters
- Automatic image type recognition: diagrams, waveforms/spectra, formula derivations, examples, comparisons, physical models
- Cross-validation: context keyword matching + visual content description = high-confidence embedding
- Auto-generated captions: image titles and descriptions based on surrounding context
- Quality detection & deduplication: auto-detect low-quality and duplicate images
- **Inline SVG only as a last-resort backup** when courseware lacks images for a concept

### 🎮 Interactive Learning Features
- 📋 Exam cover sheet (course name, scope, format, instructor, textbook)
- 📖 Layered reading guide (multiple review paths for different skill levels)
- 📑 Clickable table of contents with progress tracking bar
- 🔍 **Full-text search** (searches reading guide, table of contents, all chapters, and appendices)
- 🗺️ Core concept mind map (inline SVG)
- 📌 Key concept deep dives (bilingual terminology, complete derivations)
- 🔑 Critical theorems and relationships
- 📐 **Collapsible derivation steps** (click to expand, save screen space)
- ⚡📖 **Tabbed views** (Quick Review / Detailed Explanation toggle)
- 🃏 **Flashcard flip cards** (click to flip — term on front, definition on back, JavaScript event binding)
- 📝 **Practice quizzes** (concept checks with revealable answers)
- ✏️ Worked examples (solution immediately follows problem, with verification and common pitfalls)
- 💡 Intuitive explanations (everyday analogies and mnemonics)
- 📋 Appendix A: Formula quick-reference cards (by chapter)
- 📋 Appendix B: Problem-solving templates (step-by-step)
- 📋 Appendix C: Common mistakes and pitfalls (confusable concepts)
- 🖨️ Print-optimized stylesheet (all interactive content auto-expands)

### Screenshots

> Put your courseware in a folder and follow the AI's prompts for similar results.
> See the test courseware (DSP / Digital Signal Processing, 24 PDFs) in the project for an example of generated output.
>
> 📸 Screenshots welcome — submit yours to Issues!

---

## Detailed Usage

### Workflow Overview

The process has seven phases, guided step-by-step by the AI:

```
Course files ──→ Phase 1: Scope ──→ Phase 2: Extraction ──→ Phase 2+: Image Matching ──→ Phase 3: Research
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

**Tip**: Prepare an exam scope list or syllabus in advance for better accuracy.

### Phase 2: Content Extraction

The AI guides you to run `extract_course_materials.py`. **Use command-line arguments** (no code editing needed):

```bash
# Basic usage: specify courseware and output directories
python extract_course_materials.py --course-dir "path/to/courseware" --output-dir "output_dir"

# Common full command:
python extract_course_materials.py \
    --course-dir "./my-courseware" \
    --text-output-dir "extracted_text" \
    --image-output-dir "extracted_images"
```

**Optional --render-pages flag**: If your AI model supports vision (multimodal models like Claude Opus 4, GPT-4V), **highly recommended**:

```bash
# Install pymupdf first: pip install pymupdf
python extract_course_materials.py --course-dir "./my-courseware" --render-pages
```

This renders PDF pages as full-page screenshots, allowing the AI to see the complete layout (formulas, charts, diagrams in context) — **significantly improves output quality**. Essential for scan-based PDFs (pure-image courseware).

The script automatically:
- Extracts text and images from all courseware files
- Detects pure-image files (scan-based PDFs) and flags them
- Inserts `[IMAGE: xxx.png]` markers in extracted text at image positions
- Produces a detailed extraction report

### Phase 2+: Smart Image Matching

After extraction, run `match_images.py` for intelligent image-to-chapter matching:

```bash
# Basic usage
python match_images.py --text-dir extracted_text --image-dir extracted_images

# Interactive confirmation mode (recommended, allows manual correction)
python match_images.py --text-dir extracted_text --image-dir extracted_images --interactive

# Specify output mapping file
python match_images.py --text-dir extracted_text -o image_mapping.json
```

Features:
- Parses all `[IMAGE: xxx.png]` markers, extracting 5 lines of context before/after each
- Keyword-based classification into 6 types: diagrams, waveform/spectrum, formula/derivation, examples, comparisons, physical models
- Confidence scoring, prioritizing high-confidence matches for embedding
- Interactive mode allows manual correction of chapter assignments
- Outputs `image_mapping.json` for use in downstream HTML generation

### Phase 3: Supplementary Research (Optional)

The AI may search for supplementary context from:
- GitHub (open course notes, problem solutions)
- Wikipedia (authoritative concept definitions)

**All external content is for reference only** — your course materials remain the primary source.

### Phase 4: HTML Generation

The AI generates an **interactive** HTML document. **The document is massive (2000+ lines) and is built using a serial Python script append approach** — write the CSS and page structure with the Write tool first, then append chapter content in batches (2-3 chapters per batch) via Python scripts, and finally append appendices and JavaScript. This avoids timeouts and output truncation from one-shot generation.

The output includes:
- **MathJax** rendering for formulas (LaTeX)
- **Inline SVG** diagrams (flowcharts, comparison charts, plots)
- **Original courseware images** (relative paths during generation, then base64-embedded via `embed_images.py`)
- **Responsive CSS** (works on desktop, tablet, mobile + print styles + sticky sidebar on wide screens)
- **Interactive components** (collapsible derivations, tabbed views, flashcards, quizzes, progress tracker, search)
- **Inline JavaScript** (zero external JS libraries, fully self-contained)

After generation, make the HTML fully self-contained:

```bash
python embed_images.py <filename>.html   # Inline all images as base64
python setup_mathjax.py                  # (One-time) Download MathJax locally for offline formulas
```

### Phase 5: Quality Assurance

The AI runs a 36-item checklist covering structure completeness, interactivity, math rendering, and print compatibility.

### Phase 6: Exam Prediction (Optional)

After finishing the review document, the AI can generate a **standalone HTML exam prediction document** — high-frequency topic predictions, chapter exercises (multiple choice, fill-in-the-blank, calculation problems), a mock exam with solutions. The prediction document uses an exam-style layout (serif fonts, minimalist design), independent from the review document, for easy printing and distribution.

### Image Recognition Capabilities

For pure-image courseware (scanned PDFs, image-only PPTX), this skill uses a three-level fallback:

| Priority | Approach | Description |
|----------|----------|-------------|
| 1 | Built-in model vision | Direct image reading (requires multimodal model) |
| 2 | MCP vision server | External vision tools via MCP protocol |
| 3 | User-guided resolution | Switch models, install MCP, or pre-process with OCR (Tesseract) |

---

## Alternative Skill: Chapter Notes

In addition to `course-review-guide` (exam review), this project includes the `course-notes` skill:

| Skill | File | Purpose | Best For |
|-------|------|---------|----------|
| **course-review-guide** | `skills/course-review-guide/SKILL.md` | Generate a complete exam review document | Pre-exam cramming, quick review |
| **course-notes** | `skills/course-notes.md` | Generate chapter-by-chapter structured notes | Long-term learning, following lectures, deep understanding |

Usage is the same — tell your AI assistant you want **chapter notes** instead of an exam review:

> Follow the instructions in skills/course-notes.md and help me convert the course materials in [path/to/courseware] into chapter-by-chapter study notes.

Both skills complement each other: use `course-notes` for daily study during the semester, then `course-review-guide` for comprehensive pre-exam review.

---

## Interactive Learning Features

The generated HTML includes interactive learning components, inspired by [Thariq's "Using Claude Code: The Unreasonable Effectiveness of HTML"](https://x.com/thariqk):

### Collapsible Derivation Steps

All mathematical derivations collapsed by default — click to expand. Saves page space and lets students reveal detail on demand. Auto-expands when printing.

### Tabbed Views

Each chapter has two tabs:
- **⚡ Quick Review**: Chapter summary, flashcard grid, key formula table
- **📖 Detailed Explanation**: Full derivations, worked examples, diagrams

### Flashcard Flip Cards

Core terminology flip cards — front shows the term, click to flip and see the definition or formula. CSS 3D transform, works with both mouse and touch.

### Practice Quizzes

Each chapter ends with 2-4 concept check questions. Answers hidden by default — click "Show Answer" to reveal. Great for self-assessment.

### Progress Tracking

The sidebar ToC includes checkboxes. Mark completed sections and the progress bar updates in real-time. Progress is saved in browser localStorage and survives page refreshes.

### Full-text Search

A search bar at the top lets you filter chapters by keyword — quickly find concepts or formulas.

### Print Compatibility

When printing, all interactive elements gracefully degrade: collapsed content expands, all tab panels show, flashcards render front+back, search and progress controls hide.

---

## Supported Platforms

| Platform | Priority | How to Use | Interaction Mode |
|----------|----------|------------|-----------------|
| **Claude Code** | P0 | Built-in `CLAUDE.md` | Full interactive |
| **OpenAI Codex CLI** | P0 | Custom Prompt | Full interactive |
| **OpenCode** | P1 | `AGENTS.md` + `opencode.json` | Full interactive |
| **OpenClaw/Hermes** | P2 | `AGENTS.md` + `exam-scope.json` | Autonomous |
| **GitHub Copilot** | Community | Custom Prompt | Full interactive |
| **Kimi Code** | Community | Custom Instructions | Full interactive |
| **Cursor** | Community | Custom Rules | Full interactive |

Platform-specific adaptations are documented in `AGENTS.md`.

---

## Autonomous Agent Support

OpenClaw, Hermes, and other autonomous agents run fully automatically **without guaranteed turn-based interaction**. This skill includes dedicated adaptations for autonomous mode.

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

A template is at `exam-scope-template.json` in the project root.

### Three-Level Scope Determination

| Level | Method | Interaction Required | Reliability |
|-------|--------|---------------------|-------------|
| 1 | Read `exam-scope.json` | None | High |
| 2 | Infer scope from filenames | None | Medium |
| 3 | Request via messaging channel | Yes (async) | High |

### Auto-Inference Mode

If `exam-scope.json` is not found, the agent infers chapter scope from filenames. The generated HTML displays a prominent autonomous mode banner, reminding users to verify the scope. The agent also auto-generates an `exam-scope-template.json` (with inferred defaults) for next time.

See `AGENTS.md` for detailed adaptation instructions.

---

## Privacy & Security

When using this tool, your course materials pass through:

1. **Local extraction**: `extract_course_materials.py` runs on your computer. Extracted text and images stay on your machine — **nothing is uploaded**.
2. **AI service provider**: When you chat with an AI assistant, course content is sent to the AI provider (e.g., Anthropic, OpenAI, Moonshot). Check their privacy policies.
3. **Web search**: The AI may access public websites (GitHub, Wikipedia) for supplementary research.

**Recommendations**:
- Remove personally identifiable information (student IDs, ID numbers) from course materials before processing
- If materials contain unpublished research or trade secrets, verify the AI provider's data usage policy first
- All intermediate files (`extracted_text/`, `extracted_images/`) are stored locally — you can delete them anytime

---

## FAQ

### Q: My courseware is scan-based PDFs (pure images) with no text layers. What do I do?

If scan quality is decent, multimodal AI models can recognize content from images. Recommendations:
1. Use `--render-pages` with the extraction script (`pip install pymupdf` first) to render pages as clear screenshots
2. Use a vision-capable model (Claude Opus 4, GPT-4V, etc.)
3. If the above isn't feasible, pre-process with OCR (Tesseract): `pip install pytesseract pdf2image`

### Q: Formulas are garbled or incomplete after extraction?

PDF text extraction can damage formulas. This skill automatically detects and fixes 6 common formula issues (fragmentation, symbol loss, fraction bar loss, superscript/subscript misplacement, matrix corruption, function name errors). All formulas are re-typeset in LaTeX for correct HTML rendering.

### Q: The generated HTML file is too large?

CSS and inline SVG add minimal weight. After running `embed_images.py` to base64-embed images, the file grows (about 1.37× total image size) but becomes fully self-contained — ideal for sharing. If too large, skip embedding and bundle the HTML with the `extracted_images/` folder instead.

### Q: How do I share and print the review document?

- **Share**: Run `python embed_images.py <filename>.html` to get a `_embedded.html` with all images inlined — send just this one file
- **Print**: Open the HTML in a browser and press `Ctrl+P` (or `Cmd+P`). Built-in `@media print` styles auto-expand all collapsed content and optimize layout

### Q: Do the interactive features (flashcards, quizzes) require internet?

No. All interactive features use pure HTML/CSS/JavaScript with zero external JS dependencies. The only thing needing internet is formula rendering. For fully offline formula viewing, run `python setup_mathjax.py` (one-time) to download MathJax locally.

### Q: How do I view formulas without internet access?

**Simplest way**: Run the one-click setup script included in the project:

```bash
python setup_mathjax.py
```

This downloads MathJax 3 to the `mathjax/` directory. The generated HTML **automatically tries local MathJax first**, falling back to CDN only if the local copy is missing. Formulas render fine without internet.

To share the HTML file with others: bundle the file together with the `mathjax/` folder.

### Q: Will my learning progress be lost?

Progress is saved in the browser's localStorage and survives page refreshes. Note: progress is tied to the file path — moving the file resets it.

### Q: Which file formats are supported?

| Format | Extensions | Status |
|--------|-----------|--------|
| PDF | `.pdf` | ✅ Fully supported |
| PowerPoint | `.pptx`, `.pptm` | ✅ Fully supported |
| Word | `.docx`, `.dotx`, `.dotm` | ✅ Fully supported |
| Legacy PowerPoint | `.ppt` | ❌ Not supported — resave as `.pptx` |
| Legacy Word | `.doc` | ❌ Not supported — resave as `.docx` |

### Q: My course is taught in English. Will this work?

Yes. The skill supports bilingual output — key terms appear in both English and Chinese. For English-only courses, mention this during scope confirmation and the AI will adjust accordingly.

### Q: How do I use OpenClaw/Hermes to autonomously generate a review document?

1. Create `exam-scope.json` in your courseware directory (use `exam-scope-template.json` as a template)
2. Clone this project to a location accessible by OpenClaw
3. The OpenClaw agent reads instructions from `AGENTS.md` and executes all phases automatically
4. After generation, check the autonomous mode banner at the top of the document to verify the exam scope

---

## Contributing

Contributions are welcome!

### Submitting an Issue

Please open an issue on [GitHub Issues](https://github.com/lijiawei255/agent-edu-reviewkit/issues) if you:
- Found a bug
- Have a feature request
- Want support for a new file format or AI platform

### Submitting a Pull Request

1. **Fork** the repository
2. Create your branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'feat: add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Pre-commit checklist**:
- [ ] Changes follow existing code style
- [ ] `extract_course_materials.py` tested on Python 3.9+
- [ ] New features are documented
- [ ] No test courseware or output files included (excluded via `.gitignore`)
- [ ] **Eliminate subject-specific descriptions in the skill**: Search skill files for residual course-specific terminology (e.g., mechatronics, PLC, DSP, waveform spectrum), instructor names, or specific courseware filenames — these may be debugging artifacts that cause the skill to overfit to one course (test-set contamination), weakening cross-disciplinary generalization. The skill description should apply to all target subject types before submission
- [ ] **Validate output with real courseware**: Run the full Phase 1-6 workflow against at least one actual course's materials, and verify that the generated review document achieves the intended goals of this change (e.g., interactive features work correctly, formulas render properly, image content cross-validates with surrounding text)
- [ ] **Confirm only skill-related files are staged**: Run `git status` and verify the staging area contains only files under `skills/` plus project-root documentation and configuration files. Course materials, extraction outputs, and test HTML should never appear in the commit

### Local Development

```bash
# Clone
git clone https://github.com/lijiawei255/agent-edu-reviewkit.git
cd agent-edu-reviewkit

# Install dependencies
pip install -r requirements.txt

# Test courseware and output directories are auto-excluded by .gitignore
# Place test materials in 测试课件(不提交)/ directory
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 Li Jiawei, Peng Chen, Cai Haoxuan
