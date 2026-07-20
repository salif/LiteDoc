# litedoc-cli

The [litedoc.xyz](https://litedoc.xyz) extraction engine in your terminal: deterministic
PDF → Markdown that never hallucinates, with an optional, triage-first AI repair pass
you can point at **your own** model.

```bash
pip install litedoc-cli
playwright install chromium        # one-time engine download

litedoc convert paper.pdf                  # markdown to stdout
litedoc convert scans/*.pdf -o out/ --ocr
litedoc convert paper.pdf -o out/ --images out/images   # extracted figures as JPEGs
litedoc convert scan.pdf --ai-url http://localhost:11434 --ai-model llama3.1:8b
```

* **Identical output to the web app** — it drives the same single-file engine headlessly.
* **Deterministic by default** — no AI flag, no network: nothing leaves your machine.
* **Bring your own AI** — `--ai-url` speaks Ollama or OpenAI-compatible protocols; only
  sections that are provably damaged (broken sentences, ragged tables, OCR artifacts)
  are ever sent. `--ai` uses the hosted LiteDoc service instead (token from
  `LITEDOC_TOKEN`; only damaged sections are billed).
* **Scriptable** — globs, stdin (`-`), stdout piping, `--json` envelopes, real exit codes.
* **Structure, not just prose** — `--json` returns per-page layout (lines with
  coordinates, font sizes, reading-order blocks, OCR provenance; tables as row
  arrays; figures with page + bounding box), and `--images DIR` writes detected
  figures — cropped to include their axis labels and annotations — as JPEG files
  linked from the markdown.

License: AGPL-3.0. Part of the [LiteDoc](https://github.com/0xovo/LiteDoc) project.
