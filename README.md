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

## Screenshots

**Full Main UI with Files Loaded**
<p align="center">
 <img alt="Full Main UI" src="https://github.com/user-attachments/assets/e47528eb-63cc-4af1-9baf-253e8c5ce4f0" width="100%" />
</p>

<table>
 <tr>
 <td width="50%" valign="top">
 <b>Editor View</b><br>
 <img alt="Editor View" src="https://github.com/user-attachments/assets/e3406f44-05d3-49ee-9b51-7ff547596ea1" width="100%" />
 </td>
 <td width="50%" valign="top">
 <b>Explorer View</b><br>
 <img alt="Explorer View" src="https://github.com/user-attachments/assets/860b196d-36b6-4462-90fa-dc8bd46ed811" width="100%" />
 </td>
 </tr>
 <tr>
 <td width="50%" valign="top">
 <b>Loading Process</b><br>
 <img alt="Loading Process" src="https://github.com/user-attachments/assets/246b4a2d-0786-4996-a076-9d9f6fd8dee0" width="100%" />
 </td>
 <td width="50%" valign="top" align="center">
 <b>Settings</b><br>
 <img alt="Settings View" src="https://github.com/user-attachments/assets/88ac3a21-0620-4ebc-a3c3-ebd2eca8ce72" />
 </td>
 </tr>
</table>

---

## Why LiteDoc

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

## Key Features

### Document Intelligence

| Feature | Description |
|---|---|
| **Layout Analysis** | Kahn's Topological Sort on a DAG of geometric blocks determines correct reading order across sidebars, headers, and multi-column page layouts — no horizontal text mixing. |
| **Table Extraction** | Vector line detection builds GitHub-Flavored Markdown tables with merged cell support. |
| **Math Rendering** | Detects formula bounding boxes (including PUA-encoded symbols) and preserves them as high-fidelity images or KaTeX. |
| **Gibberish Detection** | Statistical scoring identifies corrupted custom-encoded fonts and routes them to OCR fallback. |

### Privacy & Performance

| Feature | Description |
|---|---|
| **100% Local** | All processing runs on your CPU/GPU inside the browser. Files never leave your device. |
| **Batch Processing** | Large files split into 10-page chunks. Canvas assets released dynamically to prevent memory crashes. |
| **Local Decryption** | Password-protected PDFs unlocked client-side in the browser sandbox — keys never sent anywhere. |

### Format Support & UX

| Feature | Description |
|---|---|
| **RTL & Arabic** | Native right-to-left script support with automatic line alignment and typography routing. |
| **Smart OCR Routing** | Scans initial pages for corruption; auto-detects script direction and language, initializing Tesseract.js workers on demand. |
| **Font Fallback** | Corrupted or custom-encoded fonts intercepted with image-fallback options for readability. |
| **Mobile Responsive** | Full editor, document navigation, and settings available on any screen size. |
| **Queue Control** | Pause or skip processing tasks. "Unformat" action strips markdown styling instantly. |

## Getting Started

Because LiteDoc is a purely client-side web application, you don't need to install any dependencies to run it!

**The Easiest Way:**
1. Go to the [Releases page](https://github.com/0xovo/LiteDoc/releases).
2. Download the `index.html` file from the latest release.
3. Open the downloaded `index.html` file in any modern web browser (Chrome, Edge, Firefox, Safari) and drag and drop your PDFs!

**Run from Source:**
1. Clone or download this repository.
2. Open `dist/index.html` in your browser.

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

## Architecture

LiteDoc relies on a powerful stack of client-side libraries:
* **PDF.js** - Core parsing, rendering, and text-layer extraction.
* **Tesseract.js** - WebAssembly-based OCR for scanned document fallback.
* **JSZip** - Local, client-side ZIP packaging of extracted assets.
* **KaTeX** - Fast math typesetting in the Markdown previewer.
* **Ace Editor** - High-performance code editor for tweaking Markdown before export.

## How It Works: Document Layout Analysis

Unlike basic wrapper libraries that blindly extract text sequentially from top to bottom, LiteDoc utilizes advanced Document Layout Analysis (DLA) and topological graph algorithms natively in your browser. This ensures structurally perfect extractions for complex formats like multi-column scientific papers, journals, and math-heavy PDFs.

### 1. Kahn's Topological Sort (Reading Order)
After extracting text blocks, LiteDoc maps them into a Directed Acyclic Graph (DAG) using spatial constraints.
- I use **Kahn's Topological Sort** to determine the exact human reading order.
- Edges in the graph are defined by strict geometric constraints (vertical/horizontal overlap and proximity). This eliminates "column interleaving" bugs where a right column might be accidentally read before the left.

### 2. Mathematical Equation Detection
Mathematical formulas are notoriously difficult to extract because PDF engines often map math symbols to the Private Use Area (PUA) of Unicode.
- LiteDoc analyzes character densities line-by-line using an expanded Unicode math symbol set.
- When an equation block is detected ($Density_{math} > 15\%$, or shorter lines at 30%), instead of outputting corrupted text, LiteDoc geometrically calculates the bounding box of the multi-line formula.
- The region is rendered onto an offscreen web canvas and cropped into a high-fidelity image (`[IMAGE_MATH]`), preserving visual fractions and complex integrals.

### 3. Smart Gibberish Scoring
LiteDoc implements a robust Gibberish Scorer to identify heavily corrupted, custom-encoded "subset" fonts. It calculates a statistical $Suspicion Ratio$ based on illegal character blocks. When standard text fails this heuristic, LiteDoc safely isolates the text or dynamically routes the page to my WebAssembly OCR fallback (Tesseract.js) to recover the lost data.

## Contributing

Contributions, issues, and feature requests are highly welcome! Since the goal is to keep the tool accessible and server-free, any PRs should adhere to the "100% client-side" philosophy.

**A Note on Future Updates:** Up until now, bugs and algorithmic edge-cases have been tracked manually by the maintainer. Because I currently don't have anyone actively opening issues on the repository, **future updates will be rolling out at a slower pace**. If you find a bug or want a feature, *please open an issue!* It is the best way to drive the next wave of development.

## Connect

<div align="center">

| | Link |
|---|---|
| 🌐 Website | [litedoc.xyz](https://litedoc.xyz) |
| 𝕏 Twitter | [@0xovoo](https://x.com/0xovoo) |
| ☕ Ko-fi | [ko-fi.com/0xovo](https://ko-fi.com/0xovo) |
| 📦 GitHub | [github.com/0xovo/LiteDoc](https://github.com/0xovo/LiteDoc) |
| 📧 Email | [contact@litedoc.xyz](mailto:contact@litedoc.xyz) |

</div>

## Support

LiteDoc is—and always will be—100% free and open-source. I originally built this tool to help broke students stop burning their paid AI tokens just to parse their study materials.

If LiteDoc has saved you time, protected your privacy, or spared your wallet from expensive backend API costs, **please consider making a donation!** Your support is what keeps this project alive and continuously improving.

<a href="https://ko-fi.com/0xovo" target="_blank"><img src="https://storage.ko-fi.com/cdn/kofi1.png?v=3" alt="Buy Me A Coffee" height="36"></a>

---

*Built with ❤️ by 0xovo*
