import json
import re

def normalize_text(text):
    """Normalize text by stripping extra whitespace, markdown syntax, and casing."""
    # Strip basic markdown headers
    text = re.sub(r'#+\s+', '', text)
    # Strip bold/italic markers
    text = re.sub(r'\*\*|\*|__|_', '', text)
    # Strip blockquote markers
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    # Remove code fences
    text = re.sub(r'```[a-z]*\n?', '', text)
    text = text.replace('`', '')
    # Normalize smart quotes to standard quotes (or just strip them)
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    # Convert to lowercase and normalize whitespace
    text = " ".join(text.lower().split())
    return text

def parse_and_save_ground_truth(structured_data, output_path):
    """
    Saves the structured ground truth.
    Prose is normalized to avoid penalizing markdown formatting loss.
    Tables and math are kept literal for structural matching later.
    """
    gt = {
        "prose": [normalize_text(p) for p in structured_data["prose"]],
        "tables": structured_data["tables"],
        "math": structured_data["math"]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gt, f, ensure_ascii=False, indent=2)
