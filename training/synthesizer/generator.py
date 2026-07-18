import random

# Expanded Vocabularies
BASE_SUBJECTS = ["system", "algorithm", "model", "pipeline", "framework", "architecture", "dataset", "parser", "extractor", "benchmark", "heuristic", "optimizer", "configuration", "document", "layout", "module", "component", "layer", "interface", "API"]
BASE_ADJECTIVES = ["novel", "robust", "scalable", "efficient", "complex", "dynamic", "static", "neural", "bayesian", "heuristic", "optimized", "structured", "unstructured", "distributed", "concurrent", "asynchronous"]
SUBJECTS = [f"The {adj} {sub}" for adj in BASE_ADJECTIVES for sub in BASE_SUBJECTS]

BASE_VERBS = ["processes", "analyzes", "evaluates", "optimizes", "extracts", "parses", "identifies", "classifies", "generates", "synthesizes", "validates", "transforms", "normalizes", "aggregates", "computes"]
BASE_ADVERBS = ["rapidly", "accurately", "dynamically", "statically", "heuristically", "automatically", "manually", "concurrently", "sequentially", "recursively"]
VERBS = [f"{adv} {v}" for adv in BASE_ADVERBS for v in BASE_VERBS]

BASE_OBJECTS = ["the foundational parameters.", "complex layout structures.", "large-scale datasets.", "document understanding.", "table reconstruction accuracy.", "visual hierarchy.", "bounding box coordinates.", "extraction thresholds.", "OCR noise.", "rasterization artifacts."]
OBJECTS = [f"{adj} {obj}" for adj in BASE_ADJECTIVES for obj in BASE_OBJECTS]

ADVERBS = ["Moreover,", "However,", "In contrast,", "Furthermore,", "Surprisingly,", "As a result,", "Consequently,", "In particular,", "Interestingly,", "Ultimately,", "Specifically,", "Generally,", "Historically,", "Theoretically,", "Practically,"]

ARABIC_WORDS = ["هذا", "نص", "تجريبي", "باللغة", "العربية", "لاختبار", "دعم", "الاتجاه", "من", "اليمين", "إلى", "اليسار", "الذكاء", "الاصطناعي", "معالجة", "اللغات", "الطبيعية", "استخراج", "المعلومات", "من", "المستندات", "شبكة", "عصبية", "عميقة", "تعلم", "آلي", "بيانات", "ضخمة"]

def _generate_sentence(length_mode="typical"):
    sentence = f"{random.choice(SUBJECTS)} {random.choice(VERBS)} {random.choice(OBJECTS)}"
    if random.random() > 0.5:
        sentence = f"{random.choice(ADVERBS)} {sentence.lower()}"
        
    if length_mode == "fragment":
        return f"{random.choice(SUBJECTS)} {random.choice(VERBS)}."
    elif length_mode == "run-on":
        parts = [f"{random.choice(SUBJECTS)} {random.choice(VERBS)} {random.choice(OBJECTS).replace('.', '')}" for _ in range(random.randint(2, 4))]
        return ", and ".join(parts) + "."
    return sentence

def _generate_prose(sentences_min=3, sentences_max=8):
    sentences = []
    for _ in range(random.randint(sentences_min, sentences_max)):
        rand = random.random()
        if rand < 0.15: mode = "fragment"
        elif rand < 0.85: mode = "typical"
        else: mode = "run-on"
        sentences.append(_generate_sentence(mode))
    return " ".join(sentences)

def generate_paragraph():
    return _generate_prose(4, 12) + "\n"

def generate_rtl_paragraph():
    arabic_text = " ".join(random.choices(ARABIC_WORDS, k=random.randint(20, 60)))
    return f"<div dir='rtl' class='arabic'>\n\n{arabic_text}\n\n</div>\n", arabic_text

def generate_heading(depth=1):
    return f"{'#' * depth} {_generate_prose(1, 1).replace('.', '').title()}\n"

def generate_list(items=5, nested=False):
    out = ""
    for _ in range(items):
        out += f"- {_generate_sentence('fragment').replace('.', '')}\n"
        if nested and random.random() > 0.5:
            out += f"  - {_generate_sentence('fragment').replace('.', '')}\n"
    return out

def generate_table(rows=5, cols=4):
    out = ""
    gt_table = []
    
    headers = [f"Col {i}" for i in range(cols)]
    out += "|" + "|".join([f" {h} " for h in headers]) + "|\n"
    out += "|" + "|".join(["---"] * cols) + "|\n"
    gt_table.append(headers)
    
    for _ in range(rows):
        row_data = []
        for _ in range(cols):
            cell_type = random.random()
            if cell_type < 0.3:
                val = str(random.randint(10, 9999))
            elif cell_type < 0.6:
                val = f"{random.uniform(0, 100):.2f}%"
            else:
                val = random.choice(BASE_ADJECTIVES).title() + " " + random.choice(BASE_SUBJECTS)
            row_data.append(val)
            
        out += "|" + "|".join([f" {cell} " for cell in row_data]) + "|\n"
        gt_table.append(row_data)
        
    # Returns raw list-of-lists for GT
    return out, gt_table

def generate_math():
    block_raw = random.choice([
        r"\int_{a}^{b} x^2 \,dx",
        r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
        r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}",
        r"f(x) = \begin{cases} x & \text{if } x > 0 \\ 0 & \text{otherwise} \end{cases}"
    ])
    inline_raw = random.choice([r"\alpha + \beta = \gamma", r"E = mc^2", r"O(n \log n)"])
    
    md_out = f"Here is some inline math: ${inline_raw}$. And a block equation:\n\n$$ {block_raw} $$\n"
    gt_out = f"Here is some inline math: {inline_raw}. And a block equation: {block_raw}"
    return md_out, gt_out

def generate_code():
    lang = random.choice(["python", "js", "rust"])
    if lang == "python":
        code = "def hello():\n    print('Hello World')\n    return 42"
    elif lang == "js":
        code = "function hello() {\n  console.log('Hello');\n  return 42;\n}"
    else:
        code = "fn main() {\n    println!(\"Hello\");\n}"
    return f"```{lang}\n{code}\n```\n"

def generate_footnote(fn_counter):
    text = _generate_prose(1, 2)
    md = f"This needs a citation.[^{fn_counter}]\n\n[^{fn_counter}]: {text}\n"
    return md, text, fn_counter + 1

def generate_pull_quote():
    quote = _generate_sentence("typical")
    return f"> **“{quote}”**\n", quote

def generate_infobox():
    items = [_generate_sentence("fragment").replace(".", "") for _ in range(3)]
    list_md = "\n".join([f"- {item}" for item in items])
    box_content = f"<div class='infobox'>\n\n### Key Takeaways\n\n{list_md}\n\n</div>\n"
    gt_content = "Key Takeaways " + " ".join(items)
    return box_content, gt_content

def generate_figure():
    caption = "Figure: " + _generate_sentence("fragment").replace(".", "")
    b64_svg = "PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjY2NjY2NjIi8+PC9zdmc+"
    md = f"![{caption}](data:image/svg+xml;base64,{b64_svg})\n\n*{caption}*\n"
    return md, caption

def build_document(category, seed=None):
    if seed is not None:
        random.seed(seed)

    blocks = []
    structured_data = {"prose": [], "tables": [], "math": [], "rtl": []}
    fn_counter = 1
    
    def add_block(b_type, content, gt_content=None):
        blocks.append(content)
        if b_type == "prose":
            structured_data["prose"].append(gt_content or content.strip())
        elif b_type == "table":
            structured_data["tables"].append(gt_content or content.strip())
        elif b_type == "math":
            structured_data["math"].append(gt_content or content.strip())
        elif b_type == "rtl":
            structured_data["rtl"].append(gt_content or content.strip())

    if category == "Academic":
        add_block("prose", generate_heading(1))
        add_block("prose", generate_paragraph())
        
        num_sections = random.randint(2, 5)
        for _ in range(num_sections):
            add_block("prose", generate_heading(2))
            add_block("prose", generate_paragraph())
            
            sub_blocks = []
            if random.random() > 0.3: sub_blocks.append("math")
            if random.random() > 0.4: sub_blocks.append("table")
            if random.random() > 0.6: sub_blocks.append("figure")
            if random.random() > 0.5: sub_blocks.append("footnote")
            
            random.shuffle(sub_blocks)
            for b in sub_blocks:
                if b == "math":
                    md, gt = generate_math()
                    add_block("math", md, gt_content=gt)
                elif b == "table":
                    md, gt = generate_table(random.randint(3, 8), random.randint(2, 5))
                    add_block("table", md, gt_content=gt)
                elif b == "figure":
                    md, gt = generate_figure()
                    add_block("prose", md, gt_content=gt)
                elif b == "footnote":
                    md, gt, fn_counter = generate_footnote(fn_counter)
                    add_block("prose", md, gt_content=gt)
                    
            add_block("prose", generate_paragraph())
            
    elif category == "Book":
        add_block("prose", generate_heading(1))
        num_sections = random.randint(3, 6)
        for _ in range(num_sections):
            add_block("prose", generate_paragraph())
            
            if random.random() > 0.5:
                add_block("prose", generate_list(nested=True))
            if random.random() > 0.7:
                md, gt, fn_counter = generate_footnote(fn_counter)
                add_block("prose", md, gt_content=gt)
                
            add_block("prose", generate_heading(2))
            add_block("prose", generate_paragraph())
            
    elif category == "Notebook":
        add_block("prose", generate_heading(1))
        num_sections = random.randint(2, 5)
        for _ in range(num_sections):
            add_block("prose", generate_code())
            add_block("prose", generate_paragraph())
            if random.random() > 0.3:
                md, gt = generate_math()
                add_block("math", md, gt_content=gt)
            
    elif category == "Magazine":
        add_block("prose", generate_heading(1))
        add_block("prose", "**" + _generate_prose(2, 4) + "**\n") 
        add_block("prose", generate_paragraph())
        
        num_sections = random.randint(1, 3)
        for _ in range(num_sections):
            sub_blocks = ["figure", "table", "pull_quote", "infobox"]
            random.shuffle(sub_blocks)
            
            for b in sub_blocks:
                if b == "figure" and random.random() > 0.3:
                    md, gt = generate_figure()
                    add_block("prose", md, gt_content=gt)
                elif b == "table" and random.random() > 0.5:
                    md, gt = generate_table(random.randint(5, 10), random.randint(2, 4))
                    add_block("table", md, gt_content=gt)
                elif b == "pull_quote" and random.random() > 0.3:
                    md, gt = generate_pull_quote()
                    add_block("prose", md, gt_content=gt)
                elif b == "infobox" and random.random() > 0.5:
                    md, gt = generate_infobox()
                    add_block("prose", md, gt_content=gt)
                    
            add_block("prose", generate_heading(2))
            add_block("prose", generate_paragraph())
            add_block("prose", generate_paragraph())
        
    elif category == "Cursed":
        add_block("prose", generate_heading(1))
        add_block("prose", generate_paragraph())
        
        md, gt = generate_rtl_paragraph()
        add_block("rtl", md, gt_content=gt)
        
        md, gt = generate_table()
        add_block("table", md, gt_content=gt)
        
        md, gt = generate_math()
        add_block("math", md, gt_content=gt)
        
        add_block("prose", generate_code())
        
    elif category == "Scanned":
        add_block("prose", generate_heading(1))
        add_block("prose", generate_paragraph())
        
        if random.random() > 0.5:
            md, gt = generate_table(random.randint(3, 6), random.randint(2, 4))
            add_block("table", md, gt_content=gt)
            
        add_block("prose", generate_paragraph())
        
    else:
        raise ValueError(f"Unknown document category: {category}")

    return "\n\n".join(blocks), structured_data
