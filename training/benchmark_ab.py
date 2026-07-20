#!/usr/bin/env python3
"""Compare two LiteDoc parameter configurations against the synthetic dataset."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimizer.fitness import evaluate_parameters


def load_params(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def print_report(label, score, breakdown):
    print(f"\n{label}")
    print("-" * len(label))
    print(f"Overall: {score * 100:.2f}%")
    for category, stats in breakdown.items():
        if stats.get("expected", 0) == 0:
            continue
        crashes = stats.get("crashes", 0)
        crash_note = f", {crashes} crash(es)" if crashes else ""
        print(f"  {category:10s} {stats['score'] * 100:6.2f}%  ({stats['count']}/{stats['expected']} docs{crash_note})")


def main():
    parser = argparse.ArgumentParser(description="A/B benchmark two LiteDoc parameter sets")
    parser.add_argument("--baseline", required=True, help="Path to baseline params JSON")
    parser.add_argument("--candidate", required=True, help="Path to candidate params JSON")
    parser.add_argument("--data", default="training/source_materials", help="Dataset directory")
    parser.add_argument("--json-out", default="", help="Also write full results as JSON to this path")
    args = parser.parse_args()

    baseline = load_params(args.baseline)
    candidate = load_params(args.candidate)

    print("Running baseline evaluation...")
    base_score, base_breakdown = evaluate_parameters(baseline, args.data)

    print("Running candidate evaluation...")
    cand_score, cand_breakdown = evaluate_parameters(candidate, args.data)

    print_report("Baseline", base_score, base_breakdown)
    print_report("Candidate", cand_score, cand_breakdown)

    delta = (cand_score - base_score) * 100
    sign = "+" if delta >= 0 else ""
    print(f"\nDelta: {sign}{delta:.2f} percentage points")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump({
                "baseline": {"score": base_score, "breakdown": base_breakdown},
                "candidate": {"score": cand_score, "breakdown": cand_breakdown},
                "delta_points": delta,
                "dataset": args.data,
            }, f, indent=2)


if __name__ == "__main__":
    main()
