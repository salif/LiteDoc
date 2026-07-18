import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from synthesizer.ground_truth import normalize_text


def _strip_page_headers(text):
    return re.sub(r"## Page \d+\s*", "", text)


def _extract_paragraphs(text):
    text = _strip_page_headers(text)
    blocks = []
    for block in re.split(r"\n\s*\n", text):
        normalized = normalize_text(block)
        if normalized:
            blocks.append(normalized)
    return blocks


def _word_seq_ratio(a, b):
    return difflib.SequenceMatcher(None, a.split(), b.split()).ratio()


def _order_concordance(positions):
    """Fraction of pairs of matched blocks that appear in GT order (Kendall-style)."""
    if len(positions) < 2:
        return 1.0
    concordant = 0
    pairs = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            pairs += 1
            if positions[i] <= positions[j]:
                concordant += 1
    return concordant / pairs


def score_prose(gt_prose_list, extracted_text):
    """
    Scores prose per GT block on content AND word order, then scales by how well
    the blocks' order in the output matches GT order. A scrambled extraction must
    score well below a faithful one — the optimizer is otherwise free to trade
    reading order away entirely (it did: see the v3.0.0 fitness overhaul).
    """
    if not gt_prose_list:
        return 1.0

    ext_blocks = _extract_paragraphs(extracted_text)
    ext_joined = " ".join(ext_blocks)
    block_offsets = []
    offset = 0
    for block in ext_blocks:
        block_offsets.append(offset)
        offset += len(block) + 1

    total_score = 0.0
    matched_positions = []
    for gt_block in gt_prose_list:
        if not gt_block:
            continue

        content = 0.0
        best_pos = None
        if gt_block in ext_joined:
            content = 1.0
            best_pos = ext_joined.find(gt_block)
        else:
            for pos, block in enumerate(ext_blocks):
                ratio = difflib.SequenceMatcher(None, gt_block, block).ratio()
                if ratio > content:
                    content = ratio
                    best_pos = block_offsets[pos]

            matcher = difflib.SequenceMatcher(None, gt_block, ext_joined)
            match = matcher.find_longest_match(0, len(gt_block), 0, len(ext_joined))
            if len(gt_block) > 0 and match.size / len(gt_block) > content:
                content = match.size / len(gt_block)
                best_pos = match.b

        word_order = _word_seq_ratio(gt_block, ext_joined)
        for block in ext_blocks:
            if word_order >= 1.0:
                break
            word_order = max(word_order, _word_seq_ratio(gt_block, block))

        total_score += (0.6 * content) + (0.4 * word_order)
        if content > 0.3 and best_pos is not None:
            matched_positions.append(best_pos)

    block_order = _order_concordance(matched_positions)
    base = total_score / max(1, len(gt_prose_list))
    return base * (0.7 + 0.3 * block_order)


def _parse_markdown_tables(text):
    tables = []
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if "|" not in line:
            i += 1
            continue

        table_lines = []
        while i < len(lines) and "|" in lines[i]:
            table_lines.append(lines[i])
            i += 1

        rows = []
        for table_line in table_lines:
            stripped = table_line.strip()
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells:
                rows.append(cells)

        if rows:
            tables.append(rows)

    return tables


def _table_similarity(gt_table, ext_table):
    if not gt_table or not ext_table:
        return 0.0

    gt_rows, gt_cols = len(gt_table), max(len(row) for row in gt_table)
    ext_rows, ext_cols = len(ext_table), max(len(row) for row in ext_table)

    shape_score = 1.0 - (
        abs(gt_rows - ext_rows) / max(gt_rows, ext_rows, 1)
        + abs(gt_cols - ext_cols) / max(gt_cols, ext_cols, 1)
    ) / 2.0

    gt_cells = [cell.strip().lower() for row in gt_table for cell in row if cell.strip()]
    ext_cells = [cell.strip().lower() for row in ext_table for cell in row if cell.strip()]

    if not gt_cells:
        return shape_score * 0.5

    # Exact cell-for-cell matches score fully; a GT cell that only appears as a
    # substring of some (e.g. merged) cell gets half credit, so cell merging is
    # visibly penalised instead of free.
    ext_cell_set = set(ext_cells)
    ext_joined = " | ".join(ext_cells)
    content_score = 0.0
    for cell in gt_cells:
        if cell in ext_cell_set:
            content_score += 1.0
        elif cell in ext_joined:
            content_score += 0.5
    content_score /= len(gt_cells)

    return (shape_score * 0.3) + (content_score * 0.7)


def score_tables(gt_tables, extracted_text):
    """
    Scores tables by parsing markdown table structures and comparing shape + cell content.
    """
    ext_tables = _parse_markdown_tables(extracted_text)

    if not gt_tables and not ext_tables:
        return 1.0
    if not gt_tables and ext_tables:
        return 0.0
    if gt_tables and not ext_tables:
        return 0.0

    total_score = 0.0
    for gt_table in gt_tables:
        best = max((_table_similarity(gt_table, ext_table) for ext_table in ext_tables), default=0.0)
        total_score += best

    return total_score / max(1, len(gt_tables))


def _normalize_math(text):
    text = re.sub(r"\$+", "", text)
    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\\\", r"\\", text)
    return " ".join(text.lower().split())


def score_math(gt_math, extracted_text):
    """
    Scores math by checking if LaTeX content was preserved, with fuzzy fallback for OCR noise.
    """
    if not gt_math:
        return 1.0

    ext_norm = _normalize_math(extracted_text)
    total_score = 0.0

    for block in gt_math:
        core_math = _normalize_math(block.replace("$$", "").strip())
        if not core_math:
            continue

        if core_math in ext_norm:
            total_score += 1.0
        else:
            matcher = difflib.SequenceMatcher(None, core_math, ext_norm)
            match = matcher.find_longest_match(0, len(core_math), 0, len(ext_norm))
            total_score += match.size / max(1, len(core_math))

    return total_score / max(1, len(gt_math))


def calculate_fitness(gt_path, extracted_text):
    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    s_prose = score_prose(gt.get("prose", []), extracted_text)
    s_tables = score_tables(gt.get("tables", []), extracted_text)
    s_math = score_math(gt.get("math", []), extracted_text)
    s_rtl = score_prose(gt.get("rtl", []), extracted_text)

    if "rtl" in gt and gt["rtl"]:
        final_score = (s_prose * 0.3) + (s_tables * 0.3) + (s_math * 0.2) + (s_rtl * 0.2)
    else:
        final_score = (s_prose * 0.4) + (s_tables * 0.4) + (s_math * 0.2)
        
    return {
        "overall": final_score,
        "prose": s_prose,
        "tables": s_tables,
        "math": s_math,
        "rtl": s_rtl,
    }
