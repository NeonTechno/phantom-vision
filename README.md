# 👁️ Phantom Vision

> AI-powered image analysis CLI — describe, tag, and interrogate any image using Claude's vision.

![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude%20AI-orange?style=flat-square)

---

## ✨ Features

- 🔍 **Describe** — Get a rich natural language description of any image
- 🏷️ **Tag** — Auto-generate semantic tags for an image
- ❓ **Ask** — Ask any question about an image and get an AI answer
- 📊 **Analyze** — Deep structured analysis (objects, colors, mood, text, scene)
- 🎨 **Batch mode** — Process multiple images at once

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/NeonTechno/phantom-vision.git
cd phantom-vision

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Run it!
python phantom.py describe path/to/image.jpg
python phantom.py tag path/to/image.jpg
python phantom.py ask path/to/image.jpg "What emotion does this convey?"
python phantom.py analyze path/to/image.jpg
```

---

## 📖 Usage

```
Usage: phantom.py [OPTIONS] COMMAND IMAGE_PATH [QUESTION]

Commands:
  describe    Natural language description of the image
  tag         Generate semantic tags
  ask         Ask a specific question about the image
  analyze     Full structured analysis (JSON output)
  batch       Process all images in a directory

Options:
  --output    Output format: text | json (default: text)
  --model     Claude model to use (default: claude-opus-4-6)
  --verbose   Show token usage and timing
  --help      Show this message
```

---

## 🛠️ Built With

- [Anthropic Claude](https://www.anthropic.com) — Vision AI backbone
- [Pillow](https://python-pillow.org/) — Image loading & preprocessing
- [Rich](https://github.com/Textualize/rich) — Beautiful terminal output
- [Click](https://click.palletsprojects.com/) — CLI framework

---

## 📄 License

MIT © [NeonTechno](https://github.com/NeonTechno)
