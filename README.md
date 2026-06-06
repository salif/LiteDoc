# 📄 LiteDoc

**A 100% Local, Browser-Based PDF to Markdown Converter.**

LiteDoc is a zero-setup, client-side tool built to extract text, images, tables, and math from PDFs. Save your LLM tokens and avoid wrestling with heavy backend environments—just drop your file in the browser and get clean Markdown.

---

## 🥊 Why LiteDoc? (vs. Markitdown, Docling, Marker)

There are incredible, industry-standard tools out there for PDF parsing, like **Markitdown** (Microsoft), **Docling** (IBM), and **Marker**. However, they are fundamentally built for automated backend pipelines, which introduces significant friction for average users.

| Feature | 🐍 Markitdown / Docling / Marker | 🌐 LiteDoc |
| :--- | :--- | :--- |
| **Setup Required** | `pip install`, Python environments, Docker | **Zero.** Just open a web page. |
| **Target Audience** | Backend Devs, Data Engineers, AI Pipelines | **Everyone.** Students, researchers, writers. |
| **Processing** | Local CLI or Server-side API | **100% Client-side** (WASM + JS). |
| **Privacy** | Depends on your infrastructure setup | **Absolute.** Files never leave your device. |

**LiteDoc is for people who just want their Markdown *right now*.** 
No dependencies, no server uploads, no privacy concerns. It runs entirely on your local machine using your browser's resources.

---

## ✨ Key Features

- **🔒 100% Local & Private:** Unpacks, parses, and converts PDFs entirely in the browser via `pdf.js`.
- **🖼️ Built-in OCR:** Automatically runs WebAssembly-based Tesseract.js on textless, scanned pages.
- **📊 Tables & Vectors:** Detects column structures, reconstructs tables, and extracts vector-drawn charts as standalone images.
- **🧮 Math & Academic Support:** Extracts LaTeX math regions and renders them beautifully via KaTeX.
- **🌍 Arabic & RTL:** Auto-detects and properly formats right-to-left languages with proper font fallbacks.
- **🛡️ Password Support:** Safely prompts for passwords to unlock protected documents locally.
- **🧹 Corrupted Font Handling:** Detects custom-encoded "garbage" fonts and offers smart fallbacks, including rendering unreadable pages as high-quality images.

## 🚀 Getting Started

Because LiteDoc is a purely client-side web application, installation takes seconds.

1. Clone or download this repository.
2. Open `index.html` in any modern web browser (Chrome, Edge, Firefox, Safari).
3. Drag and drop your PDFs!

### Extracting Files
Once processing finishes, you can preview the generated Markdown directly in the built-in Ace Editor. 
Click **Download Files (.zip)** to get a neatly packaged archive containing your `.md` file and an attached folder containing all extracted images, tables, and charts.

## 🛠️ Architecture & Under the Hood

LiteDoc relies on a powerful stack of client-side libraries:
* **PDF.js** - Core parsing, rendering, and text-layer extraction.
* **Tesseract.js** - WebAssembly-based OCR for scanned document fallback.
* **JSZip** - Local, client-side ZIP packaging of extracted assets.
* **KaTeX** - Fast math typesetting in the Markdown previewer.
* **Ace Editor** - High-performance code editor for tweaking Markdown before export.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Since the goal is to keep the tool accessible and server-free, any PRs should adhere to the "100% client-side" philosophy.

## ☕ Support

I originally built this tool to help broke students stop burning their paid AI tokens just to parse their study materials. If LiteDoc saved you time or money, consider supporting the project!

<a href="https://ko-fi.com/0xovo" target="_blank"><img src="https://storage.ko-fi.com/cdn/kofi1.png?v=3" alt="Buy Me A Coffee" height="36"></a>

---

*Built with ❤️ by 0xovo*
