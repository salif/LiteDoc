<div align="center">
  <h1>📄 LiteDoc</h1>
  <p><b>A 100% Local, Browser-Based PDF to Markdown Converter.</b></p>
  
  [![Try it Live](https://img.shields.io/badge/🚀_Try_LiteDoc_Live-litedoc.xyz-6366f1?style=for-the-badge)](https://litedoc.xyz/)
  [![GitHub stars](https://img.shields.io/github/stars/0xovo/LiteDoc?style=for-the-badge&color=eab308)](https://github.com/0xovo/LiteDoc/stargazers)
  [![Twitter Follow](https://img.shields.io/badge/Follow_@0xovoo-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/0xovoo)

  <br />
  
  <i>LiteDoc is a zero-setup, client-side tool built to extract text, images, tables, and math from PDFs. Save your LLM tokens and avoid wrestling with heavy backend environments—just drop your file in the browser and get clean Markdown.</i>
</div>

---

## 📸 See it in Action

**Full Main UI with Files Loaded**
<p align="center">
  <img alt="Full Main UI" src="https://github.com/user-attachments/assets/e47528eb-63cc-4af1-9baf-253e8c5ce4f0" width="100%" />
</p>

<table>
  <tr>
    <td width="50%" valign="top">
      <b>📝 Editor View</b><br>
      <img alt="Editor View" src="https://github.com/user-attachments/assets/e3406f44-05d3-49ee-9b51-7ff547596ea1" width="100%" />
    </td>
    <td width="50%" valign="top">
      <b>📂 Explorer View</b><br>
      <img alt="Explorer View" src="https://github.com/user-attachments/assets/860b196d-36b6-4462-90fa-dc8bd46ed811" width="100%" />
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <b>⏳ Loading Process</b><br>
      <img alt="Loading Process" src="https://github.com/user-attachments/assets/246b4a2d-0786-4996-a076-9d9f6fd8dee0" width="100%" />
    </td>
    <td width="50%" valign="top" align="center">
      <b>⚙️ Settings</b><br>
      <img alt="Settings View" src="https://github.com/user-attachments/assets/88ac3a21-0620-4ebc-a3c3-ebd2eca8ce72" />
    </td>
  </tr>
</table>

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

- **🔒 100% Local & Private:** Core extraction, OCR, and bundling run entirely on your local CPU/GPU inside the browser. Files never touch any server.
- **🧩 Document Layout Analysis (DLA):** Employs a recursive **XY-Cut algorithm** to map out and isolate sidebars, headers, and multi-column flows, preventing horizontal text mixing.
- **🖼️ Smart OCR & OSD Router:** Runs a lightweight 400x400px pre-pass to auto-detect script direction and language, dynamically initializing WebAssembly Tesseract.js workers.
- **📊 Table & Vector Figures:** Detects vector lines to construct pristine GitHub-Flavored Markdown tables (supporting complex merged cells) and crops diagrams/charts as JPEG assets.
- **🧮 LaTeX Math Equations:** Automatically detects math formula bounding boxes and renders them with KaTeX.
- **🌍 Arabic & RTL Formatting:** Native support for Right-to-Left scripts with automatic line alignment and typography routing.
- **🛡️ Local Decryption:** Handles password-protected PDFs securely by prompt-unlocking them locally in the browser sandbox.
- **🧹 Custom Font Fallbacks:** Intercepts corrupted, custom-encoded "garbage" fonts, offering image-fallback options to ensure the document remains readable.
- **⚡ Batch Queuing & Memory Protection:** Processes large files in 10-page chunks and releases web canvas assets dynamically to prevent Out-Of-Memory (OOM) browser crashes.
- **📱 Fully Mobile Responsive:** Overhauled layout designed to offer full-editor features, document navigation, and settings toggles on mobile screens.
- **⏸️ Queue & Formatting Control:** Pause or skip processing tasks on demand, or use the "Unformat" action to strip markdown styling instantly.

## 🚀 Getting Started

Because LiteDoc is a purely client-side web application, you can run the pre-built version instantly:

1. Clone or download this repository.
2. Open `dist/index.html` in any modern web browser (Chrome, Edge, Firefox, Safari).
3. Drag and drop your PDFs!

### Development & Custom Builds
If you want to modify the source code:
1. Make changes inside the `src/` directory (includes modular CSS and JS).
2. Bundle your changes into a single self-contained file by running:
   ```bash
   python scripts/build.py
   ```
3. The compiled production bundle will be updated at `dist/index.html`.

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

## 💬 Connect & Socials

- 🌐 **Website:** [litedoc.xyz](https://litedoc.xyz/)
- 🐙 **GitHub Repo:** [0xovo/LiteDoc](https://github.com/0xovo/LiteDoc)
- 🐦 **Twitter / X:** [@0xovoo](https://x.com/0xovoo)

## ☕ Support

I originally built this tool to help broke students stop burning their paid AI tokens just to parse their study materials. If LiteDoc saved you time or money, consider supporting the project!

<a href="https://ko-fi.com/0xovo" target="_blank"><img src="https://storage.ko-fi.com/cdn/kofi1.png?v=3" alt="Buy Me A Coffee" height="36"></a>

---

*Built with ❤️ by 0xovo*
