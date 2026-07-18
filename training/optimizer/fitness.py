import json
import os
import re
import sys
import glob
import base64
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark.harness import extract_markdown_with_litedoc
from benchmark.scoring import calculate_fitness

PDF_CACHE = {}

def get_cached_pdf_b64(pdf_path):
    # Check mtime on every hit: evolve_dataset.py swaps in a fresh corpus at the
    # SAME paths, and a long-running optimizer process must not keep scoring
    # stale cached PDFs against the new ground truth.
    mtime = os.path.getmtime(pdf_path)
    cached = PDF_CACHE.get(pdf_path)
    if cached is None or cached[0] != mtime:
        with open(pdf_path, 'rb') as f:
            PDF_CACHE[pdf_path] = (mtime, base64.b64encode(f.read()).decode('utf-8'))
        cached = PDF_CACHE[pdf_path]
    return cached[1]

CATEGORIES = ["Academic", "Book", "Notebook", "Magazine", "Scanned", "Cursed"]

TRAIN_DIR = "training/source_materials"
HOLDOUT_DIR = "training/holdout_materials"


def _empty_breakdown():
    return {
        cat: {"score": 0.0, "count": 0, "crashes": 0, "expected": 0, "prose": 0.0, "tables": 0.0, "math": 0.0, "rtl": 0.0}
        for cat in CATEGORIES
    }


def _count_expected_pdfs(data_dir):
    expected = {}
    for category in CATEGORIES:
        cat_dir = os.path.join(data_dir, category)
        count = 0
        if os.path.exists(cat_dir):
            for pdf in glob.glob(os.path.join(cat_dir, "*.pdf")):
                if pdf.endswith("_clean.pdf"):
                    continue
                gt_path = pdf.replace(".pdf", ".json")
                if os.path.exists(gt_path):
                    count += 1
        expected[category] = count
    return expected


def _apply_garbage_score(score_data, pdf_path, extracted_md):
    manifest_path = pdf_path.replace(".pdf", "_degradation.json")
    if not os.path.exists(manifest_path):
        return score_data

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    present_pages = set(map(int, re.findall(r"## Page (\d+)", extracted_md)))
    total_pages = manifest.get("total_pages", 0)
    degraded_pages = set(manifest.get("degraded_pages", []))

    flagged_garbage = set(range(1, total_pages + 1)) - present_pages

    true_positives = len(flagged_garbage & degraded_pages)
    precision = true_positives / max(1, len(flagged_garbage))
    recall = true_positives / max(1, len(degraded_pages))

    garbage_score = 0.0
    if precision + recall > 0:
        garbage_score = 2 * (precision * recall) / (precision + recall)

    score_data["overall"] = (score_data["overall"] * 0.8) + (garbage_score * 0.2)
    score_data["garbage"] = garbage_score
    return score_data


def evaluate_parameters(params, data_dir=TRAIN_DIR):
    """
    Evaluates a parameter configuration against the full dataset.
    Crashes and extraction errors score 0.0 and are counted toward the average.
    """
    breakdown = _empty_breakdown()
    expected = _count_expected_pdfs(data_dir)

    for category in CATEGORIES:
        breakdown[category]["expected"] = expected[category]

    total_score = 0.0
    file_count = 0

    with sync_playwright() as p:
        # Launch Chromium once for this optimization trial
        from benchmark.harness import LITEDOC_HTML
        html_path = f"file://{os.path.abspath(LITEDOC_HTML)}"
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path, wait_until="load", timeout=30000)

        for category in CATEGORIES:
            cat_dir = os.path.join(data_dir, category)
            if not os.path.exists(cat_dir):
                continue

            # Enable OCR only for Scanned and Cursed documents to bypass it on native text docs
            enable_ocr = category in ("Scanned", "Cursed")

            for pdf in sorted(glob.glob(os.path.join(cat_dir, "*.pdf"))):
                if pdf.endswith("_clean.pdf"):
                    continue

                gt_path = pdf.replace(".pdf", ".json")
                if not os.path.exists(gt_path):
                    continue

                pdf_b64 = get_cached_pdf_b64(pdf)

                extracted_md = extract_markdown_with_litedoc(
                    pdf, params, page=page, enable_ocr=enable_ocr, pdf_b64=pdf_b64
                )
                file_count += 1
                breakdown[category]["count"] += 1

                if extracted_md.startswith("ERROR:"):
                    print(f"[WARNING] Crash on {pdf}: {extracted_md}")
                    breakdown[category]["crashes"] += 1
                    breakdown[category]["score"] += 0.0
                    
                    # The Playwright JS context or Tesseract worker is likely dead/OOM. 
                    # Reload the page to recover before the next PDF.
                    try:
                        print(f"[INFO] Reloading Playwright page to recover from crash...")
                        page.reload(wait_until="load", timeout=30000)
                    except Exception as e:
                        print(f"[ERROR] Page reload failed, recreating browser context... ({e})")
                        browser.close()
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(html_path, wait_until="load", timeout=30000)
                    continue

                # Proactively reload the page every 20 documents to prevent Tesseract memory leaks
                if file_count % 20 == 0:
                    try:
                        page.reload(wait_until="load", timeout=30000)
                    except:
                        pass

                try:
                    score_data = calculate_fitness(gt_path, extracted_md)
                    score_data = _apply_garbage_score(score_data, pdf, extracted_md)
                except Exception as e:
                    print(f"[ERROR] Scoring failed on {pdf}: {e}")
                    breakdown[category]["crashes"] += 1
                    score_data = {"overall": 0.0}

                total_score += score_data.get("overall", 0.0)
                breakdown[category]["score"] += score_data.get("overall", 0.0)
                breakdown[category]["prose"] += score_data.get("prose", 0.0)
                breakdown[category]["tables"] += score_data.get("tables", 0.0)
                breakdown[category]["math"] += score_data.get("math", 0.0)
                breakdown[category]["rtl"] += score_data.get("rtl", 0.0)

    if file_count == 0:
        return 0.0, breakdown

    avg_score = total_score / file_count

    for cat in breakdown:
        if breakdown[cat]["count"] > 0:
            count = breakdown[cat]["count"]
            breakdown[cat]["score"] /= count
            breakdown[cat]["prose"] /= count
            breakdown[cat]["tables"] /= count
            breakdown[cat]["math"] /= count
            breakdown[cat]["rtl"] /= count

    evaluated_categories = [c for c in breakdown.values() if c["count"] > 0]
    if evaluated_categories:
        min_cat_score = min(c["score"] for c in evaluated_categories)
        if min_cat_score < 0.1:
            avg_score *= 0.5

    return avg_score, breakdown
