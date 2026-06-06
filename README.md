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
  <img alt="Full Main UI" src="https://github.com/user-attachments/assets/c7efadbc-84c5-4ec1-a586-b54a38852581" width="100%" />
</p>

<table>
  <tr>
    <td width="50%" valign="top">
      <b>📝 Editor View</b><br>
      <img alt="Editor View" src="https://github.com/user-attachments/assets/7951682e-8681-446b-a265-5f25500c412a" width="100%" />
    </td>
    <td width="50%" valign="top">
      <b>📂 Explorer View</b><br>
      <img alt="Explorer View" src="https://github.com/user-attachments/assets/a2f79d42-588e-48aa-a85c-3c83d30c5275" width="100%" />
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <b>⏳ Loading Process</b><br>
      <img alt="Loading Process" src="https://github.com/user-attachments/assets/60141156-5c43-46bb-bab9-10323501af60" width="100%" />
    </td>
    <td width="50%" valign="top" align="center">
      <b>⚙️ Settings</b><br>
      <img alt="Settings View" src="https://github.com/user-attachments/assets/a8446842-49f8-41c6-a189-38ea42e90a9c" width="45%" />
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

## 💬 Connect & Socials

- 🌐 **Website:** [litedoc.xyz](https://litedoc.xyz/)
- 🐙 **GitHub Repo:** [0xovo/LiteDoc](https://github.com/0xovo/LiteDoc)
- 🐦 **Twitter / X:** [@0xovoo](https://x.com/0xovoo)

## ☕ Support

I originally built this tool to help broke students stop burning their paid AI tokens just to parse their study materials. If LiteDoc saved you time or money, consider supporting the project!

<a href="https://ko-fi.com/0xovo" target="_blank"><img src="https://storage.ko-fi.com/cdn/kofi1.png?v=3" alt="Buy Me A Coffee" height="36"></a>

---

*Built with ❤️ by 0xovo*
