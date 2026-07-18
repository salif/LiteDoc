# Sample Materials

One representative synthetic document per category, included so you can see the
shape of the training data without downloading a large corpus. Each `.pdf` is a
procedurally generated document; the matching `.json` is its ground-truth Markdown
(prose / tables / math / rtl blocks) used for scoring. The `Scanned` and `Cursed`
categories also include a `_degradation.json` manifest (which pages were rasterized
to stress OCR) and a `_clean.pdf` (the pre-degradation original).

These are **samples only** — the optimizer trains against a full corpus you
generate yourself, which is intentionally not committed (it's large and 100%
reproducible). To regenerate the full dataset:

```bash
python training/orchestrator.py --synthesize 20 --seed 42
python training/orchestrator.py --synthesize-holdout 5
```

See `training/README.md` for the full pipeline.
