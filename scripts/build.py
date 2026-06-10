#!/usr/bin/env python3
"""
build_prod.py — Production Bundler
Bundles src/ into a single self-contained dist/index.html.
"""

import re
import sys
import base64
import hashlib
import textwrap
import urllib.request
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

SRC_DIR = Path(__file__).parent.parent / "src"
DIST_DIR = Path(__file__).parent.parent / "dist"
OUT_FILE = DIST_DIR / "index.html"
CACHE_DIR = Path(__file__).parent.parent / ".build_cache"

# Load order for critical scripts
JS_PREFERRED_ORDER = [
    "js/utils.js",
    "js/state.js",
    "js/terminal.js",
    "js/ui.js",
    "js/ui-controls.js",
    "js/markdown-renderer.js",
    "js/pdf-parser.js",
    "js/ocr.js",
    "js/file-tree.js",
    "js/dropzone.js",
    "js/reset-utils.js",
    "js/downloads.js",
    "js/mobile-ux.js",
    "js/addons.js",
    "js/demo.js",
    "js/main.js"
]

CSS_PREFERRED_ORDER = [
    "css/main.css",
    "css/addons.css",
    "css/mobile.css"
]

# ── Logging ───────────────────────────────────────────────────────────────────

OK, ERR, INFO, WARN = "✔", "✘", "•", "⚠"

def log(tag: str, msg: str):
    color = {"✔": "32", "✘": "31", "•": "36", "⚠": "33"}.get(tag, "37")
    print(f"  \033[{color}m{tag}\033[0m  {msg}")

# ── Utils ─────────────────────────────────────────────────────────────────────

def read(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text

def fetch_url(url: str) -> str:
    CACHE_DIR.mkdir(exist_ok=True)
    key = CACHE_DIR / f"{hashlib.md5(url.encode()).hexdigest()}.txt"
    if key.exists():
        log(INFO, f"cache hit: {url}")
        return key.read_text(encoding="utf-8", errors="ignore")
    log(INFO, f"downloading: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r:
            data = r.read().decode("utf-8", errors="ignore")
        key.write_text(data, encoding="utf-8")
        return data
    except Exception as e:
        log(ERR, f"download failed {url}: {e}")
        return ""

def resolve_file_order(src: Path, preferred: list[str], glob: str, exclude: list[str] = None) -> list[str]:
    if exclude is None: exclude = []
    existing_preferred = [p for p in preferred if (src / p).exists() and p not in exclude]
    preferred_set = set(existing_preferred)
    all_on_disk = sorted(str(f.relative_to(src)).replace("\\", "/") for f in (src / glob.split("/")[0]).glob(f"*.{glob.split('.')[-1]}"))
    all_on_disk = [f for f in all_on_disk if f not in exclude]
    main = "js/main.js"
    extras = [f for f in all_on_disk if f not in preferred_set and f != main]
    result = existing_preferred + extras
    if main in all_on_disk and main not in result:
        result.append(main)
    return result

# ── Bundlers ──────────────────────────────────────────────────────────────────

def safe_js(content: str) -> str:
    return content.replace("</script>", "<\\/script>")

def bundle_css(src: Path, files: list[str]) -> str:
    parts = []
    for rel in files:
        content = read(src / rel)
        if content: parts.append(f"/* {rel} */\n{content}")
    return "\n\n".join(parts)

def bundle_js(src: Path, files: list[str]) -> str:
    parts = []
    for rel in files:
        content = read(src / rel)
        if content:
            content = content.replace("</script>", "<\\/script>")
            parts.append(f"// ----- {rel} -----\n;\n{content}\n;\n")
    return "\n".join(parts)

def inline_into_html(html: str, css_blob: str, js_blob: str) -> str:
    # Local CSS
    local_link = re.compile(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*href=["\'](?!https?://)([^"\']+)["\'][^>]*/?>', re.IGNORECASE)
    html = local_link.sub("", html)

    # Remote CSS
    remote_link = re.compile(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*href=["\'](https?://[^"\']+)["\'][^>]*/?>', re.IGNORECASE)
    remote_css = []
    def fetch_link(m):
        c = fetch_url(m.group(1))
        if c: remote_css.append(f"/* {m.group(1)} */\n{c}")
        return ""
    html = remote_link.sub(fetch_link, html)

    full_css = "\n\n".join(remote_css) + ("\n\n" if remote_css else "") + css_blob
    style_tag = f"\n<style>\n{full_css}\n</style>\n"
    html = html.replace("</head>", style_tag + "</head>", 1) if "</head>" in html else style_tag + html

    # Local JS
    local_script = re.compile(r'<script\b[^>]*src=["\'](?!https?://)([^"\']+)["\'][^]*>\s*</script>', re.IGNORECASE)
    html = local_script.sub("", html)

    # Remote JS
    remote_script = re.compile(r'<script\b[^>]*src=["\'](https?://[^"\']+)["\'][^>]*>\s*</script>', re.IGNORECASE)
    remote_js = []
    def fetch_remote_script(m):
        url = m.group(1)
        content = fetch_url(url)
        content = content.replace("</script>", "<\\/script>")
        remote_js.append(f"// {url}\n;\n{content}\n;\n")
        return ""
    html = remote_script.sub(fetch_remote_script, html)

    full_js = "\n\n".join(remote_js) + ("\n\n" if remote_js else "") + js_blob
    script_tag = f"\n<script>\n{full_js}\n</script>\n"
    html = html.replace("</body>", script_tag + "</body>", 1) if "</body>" in html else html + "\n" + script_tag

    return html

# ── Main ──────────────────────────────────────────────────────────────────────

def build():
    print("\n╔══════════════════════════════════════╗")
    print(  "║      build_prod.py  —  bundler       ║")
    print(  "╚══════════════════════════════════════╝\n")

    if not SRC_DIR.exists():
        log(ERR, "src/ not found"); sys.exit(1)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Discovery
    css_files = resolve_file_order(SRC_DIR, CSS_PREFERRED_ORDER, "css/*.css")
    js_files  = resolve_file_order(SRC_DIR, JS_PREFERRED_ORDER,  "js/*.js", exclude=["js/benchmark.js"])
    
    # Bundle
    css_blob = bundle_css(SRC_DIR, css_files)
    js_blob  = bundle_js(SRC_DIR, js_files)

    # Worker Patching
    pdf_worker_url = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"
    pdf_worker_code = fetch_url(pdf_worker_url)
    if pdf_worker_code:
        b64 = base64.b64encode(pdf_worker_code.encode()).decode()
        data_uri = f"data:application/javascript;base64,{b64}"
        js_blob, n = re.subn(r'https?://[^\s\'"]+pdf\.worker[^\s\'"]*\.js', data_uri, js_blob)
        log(OK, f"pdf.worker inlined ({n} refs)")

    # Tesseract
    tess_lib = safe_js(fetch_url("https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"))
    if tess_lib:
        js_blob = tess_lib + "\n\n" + js_blob
        log(OK, "Tesseract library inlined")

    # HTML
    html = read(SRC_DIR / "index.html")
    output = inline_into_html(html, css_blob, js_blob)
    OUT_FILE.write_text(output, encoding="utf-8")
    
    log(OK, f"Production build complete: {OUT_FILE.name} ({OUT_FILE.stat().st_size/1024:,.1f} KB)")

    # Asset copy (Essential only)
    import shutil
    if (SRC_DIR / "sw.js").exists():
        shutil.copy2(SRC_DIR / "sw.js", DIST_DIR / "sw.js")
        log(OK, "copied sw.js")

    print("\n  Deployment ready in dist/.\n")

if __name__ == "__main__":
    build()
