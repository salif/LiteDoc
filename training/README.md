# LiteDoc Synthetic Dataset Training Pipeline

Programmatically synthesize diverse PDF documents with accurate Markdown ground truth, then tune LiteDoc's heuristic extraction parameters via Bayesian optimization.

## Why Synthetic Generation?

Instead of manually annotating existing PDFs, we use **forward synthesis**: raw Markdown is compiled into PDFs using layout engines (Typst, WeasyPrint, Pandoc/LaTeX), guaranteeing perfect ground-truth alignment.

Document categories:

- **Academic** — two-column Typst layouts, math, tables, figures
- **Book** — long-form prose via Pandoc + XeLaTeX
- **Notebook** — code blocks and inline math
- **Magazine** — multi-column CSS grids, pull quotes, infoboxes
- **Cursed** — RTL Arabic + intentionally rasterized pages to stress OCR and garbage detection

## Architecture

```
training/
├── orchestrator.py          # CLI entry point
├── synthesizer/
│   ├── generator.py         # Procedural Markdown content
│   ├── backends.py          # Typst / LaTeX / WeasyPrint renderers
│   ├── degrader.py          # Rasterizes random pages for Cursed docs
│   └── ground_truth.py      # Normalizes and saves GT JSON
├── benchmark/
│   ├── harness.py           # Playwright driver for real LiteDoc extraction
│   └── scoring.py           # Prose / table / math fitness functions
├── optimizer/
│   ├── search.py            # Optuna TPE Bayesian search
│   └── fitness.py           # Full-dataset evaluation loop
├── source_materials/        # Generated PDFs + ground-truth JSON
├── dashboard/               # Live optimization charts
└── current_params.json      # Best-known tuning parameters
```

## Setup

### Python dependencies

```bash
pip install -r training/requirements.txt
playwright install chromium
```

### System dependencies

These must be on your `PATH` depending on which categories you generate:

| Tool | Used for |
|------|----------|
| `typst` | Academic, Notebook, Cursed |
| `pandoc` | All Typst paths + Book |
| `xelatex` | Book |
| `gs` (Ghostscript) | Cursed degradation |
| `magick` (ImageMagick) | Cursed degradation |

## Usage

Run all commands from the **project root**.

### 1. Synthesize dataset

```bash
python training/orchestrator.py --synthesize 20 --seed 42
```

Generates 20 PDFs per category (100 total). Use `--seed` for reproducible content. The existing 5-per-category set is fine for smoke tests; 20+ is recommended before long optimization runs.

### 2. Preflight + optimize

```bash
python training/orchestrator.py --optimize 100
```

Runs preflight checks (Playwright, dataset presence, smoke extraction) then resumes the Optuna study. State persists in `training/optimizer_state.db`. Best parameters are written to `training/current_params.json` when a run finishes.

Skip preflight if you already verified the harness:

```bash
python training/orchestrator.py --optimize 50 --skip-preflight
```

### 3. Monitor progress

```bash
python training/orchestrator.py --dashboard
```

Opens `http://localhost:8080` with live charts from `dashboard/data.json`.

## Benchmarking

Compare two parameter sets side by side:

```bash
python training/benchmark_ab.py \
  --baseline training/current_params.json \
  --candidate path/to/other_params.json
```

This runs the full dataset through LiteDoc headlessly and prints per-category scores.

## Scoring

Fitness is a weighted blend per document:

- **Prose (40%)** — per-block fuzzy matching against extracted paragraphs (tolerates page splits and column reordering)
- **Tables (40%)** — parsed markdown table shape + cell content overlap
- **Math (20%)** — LaTeX preservation with fuzzy OCR fallback
- **Cursed bonus** — garbage-page detection F1 from degradation manifests (20% of Cursed doc score)

Extraction crashes and timeouts score **0.0** and are counted in the average.

## Tuned Parameters

The optimizer searches 13 parameters injected via `window.__litedocTunerConfig` at extraction time. See `training/optimizer/search.py` for the full search space.
