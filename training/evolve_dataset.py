#!/usr/bin/env python3
"""
evolve_dataset.py — regenerate the training corpus with a fresh random seed.

Why: the continuous optimizer converges (plateaus) when it searches against one fixed
dataset — it just memorizes that exact set. Rotating the training data on a schedule
turns the search into *domain randomization*: the optimizer keeps facing new (but
same-style) documents, so it's pushed toward parameters that generalize across many
document variations instead of overfitting one snapshot. This is what stops it getting
stuck.

The layouts stay realistic — the synthesizer's per-document randomness varies content,
structure, tables, and section composition within human-document norms (it's not
chaotic noise), only the seed changes each generation.

Meant to run on a timer (see litedoc-evolve.timer) alongside the always-on optimizer.
Writes to a temp dir and atomically swaps it in, so a trial that's mid-read never sees a
half-written corpus.

    python training/evolve_dataset.py --per-category 20
"""

import argparse
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from optimizer.fitness import TRAIN_DIR  # "training/source_materials"


def main():
    parser = argparse.ArgumentParser(description="Rotate the training corpus with a fresh seed")
    parser.add_argument("--per-category", type=int, default=20, help="Docs per category")
    args = parser.parse_args()

    seed = random.randint(1, 10_000_000)
    staging = TRAIN_DIR + "_next"
    stamp = datetime.now(timezone.utc).isoformat()
    print(f"[{stamp}] Evolving training corpus — fresh seed={seed}, {args.per_category}/category")

    # Synthesize the new generation into a staging dir (orchestrator takes --seed; the
    # staging path is handled by synthesizing then swapping, since orchestrator writes to
    # TRAIN_DIR by default — we redirect via a temporary rename dance below).
    if os.path.exists(staging):
        shutil.rmtree(staging)

    # orchestrator.synthesize_dataset writes to out_dir; call it directly for a clean path.
    from orchestrator import synthesize_dataset
    synthesize_dataset(args.per_category, seed=seed, out_dir=staging)

    # Atomic-ish swap: move the live set aside, move staging into place, delete the old.
    old = TRAIN_DIR + "_old"
    if os.path.exists(old):
        shutil.rmtree(old)
    if os.path.exists(TRAIN_DIR):
        os.rename(TRAIN_DIR, old)
    os.rename(staging, TRAIN_DIR)
    if os.path.exists(old):
        shutil.rmtree(old)

    n_pdfs = sum(len([f for f in files if f.endswith(".pdf")]) for _, _, files in os.walk(TRAIN_DIR))
    print(f"[{stamp}] Done. New corpus live at {TRAIN_DIR} ({n_pdfs} pdfs). "
          f"The optimizer will face it on its next trial.")


if __name__ == "__main__":
    main()
