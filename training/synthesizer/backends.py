import subprocess
import os

def render_with_weasyprint(md_content, output_pdf_path):
    import weasyprint
    import markdown
    
    # Render with basic markdown extensions
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Magazine-style CSS
    css = """
    @page { 
        size: A4; 
        margin: 2cm; 
        @bottom-center { content: counter(page); font-family: sans-serif; font-size: 10pt; color: #666; }
    }
    body { 
        font-family: 'Times New Roman', serif; 
        font-size: 11pt;
        line-height: 1.5;
        column-count: 2; 
        column-gap: 1.5cm; 
        column-fill: balance;
        text-align: justify;
    }
    h1 { 
        column-span: all; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        font-size: 36pt;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 0.5em;
        line-height: 1.1;
        border-bottom: 4px solid #000;
        padding-bottom: 10px;
    }
    h2 { 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
        font-size: 16pt;
        margin-top: 1.5em;
        break-after: avoid;
    }
    p { margin-top: 0; margin-bottom: 1em; }
    
    /* Drop Cap */
    p:first-of-type::first-letter {
        font-size: 300%;
        font-weight: bold;
        line-height: 1;
        color: #2b6cb0;
    }
    
    /* Pull Quote */
    blockquote {
        font-family: 'Georgia', serif;
        font-size: 18pt;
        line-height: 1.4;
        font-style: italic;
        color: #333;
        margin: 2em 0;
        padding: 1em 0;
        border-top: 2px solid #000;
        border-bottom: 2px solid #000;
        text-align: center;
        break-inside: avoid;
    }
    
    /* Infobox */
    .infobox {
        background: #f0f4f8;
        border: 1px solid #cce;
        padding: 1.5em;
        margin: 2em 0;
        break-inside: avoid;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 10pt;
        border-top: 6px solid #2b6cb0;
    }
    .infobox h3 { margin-top: 0; color: #2b6cb0; font-size: 14pt; }
    .infobox ul { padding-left: 1.5em; }
    
    /* Standard Tables */
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 2em 0; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 9pt;
        break-inside: avoid;
    }
    th { border-bottom: 2px solid #000; padding: 6px; text-align: left; }
    td { border-bottom: 1px solid #ccc; padding: 6px; }
    
    pre { background: #f4f4f4; padding: 1em; break-inside: avoid; }
    
    /* Arabic Support */
    .arabic {
        direction: rtl;
        unicode-bidi: bidi-override;
        font-family: 'Amiri', 'DejaVu Sans', sans-serif;
        text-align: right;
    }
    """
    
    full_html = f"<html><head><style>{css}</style></head><body>{html_content}</body></html>"
    weasyprint.HTML(string=full_html).write_pdf(output_pdf_path)

def render_with_typst(md_content, output_pdf_path, category):
    import re
    import base64
    
    tmp_md = output_pdf_path.replace(".pdf", ".md")
    tmp_typst = output_pdf_path.replace(".pdf", ".typ")
    
    svg_files = []
    def replace_svg(match):
        caption = match.group(1)
        b64_data = match.group(2)
        svg_data = base64.b64decode(b64_data).decode('utf-8')
        # Unique filename based on hash
        tmp_svg = output_pdf_path.replace(".pdf", f"_{abs(hash(b64_data))}.svg")
        with open(tmp_svg, 'w', encoding='utf-8') as f:
            f.write(svg_data)
        svg_files.append(tmp_svg)
        return f"![{caption}]({os.path.basename(tmp_svg)})"
        
    md_content = re.sub(r'!\[(.*?)\]\(data:image/svg\+xml;base64,(.*?)\)', replace_svg, md_content)
    
    # Intercept RTL HTML for Typst
    md_content = re.sub(
        r"<div dir='rtl' class='arabic'>\n\n(.*?)\n\n</div>\n",
        r"```{=typst}\n#set text(dir: rtl)\n\1\n```\n",
        md_content,
        flags=re.DOTALL
    )
    
    with open(tmp_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    try:
        # Convert MD to Typst using Pandoc
        subprocess.run(["pandoc", tmp_md, "-o", tmp_typst], check=True)
        
        # Inject template logic if needed
        with open(tmp_typst, 'r', encoding='utf-8') as f:
            typst_src = f.read()
            
        preamble = ""
        if category == "Academic":
            # Using default Typst font to avoid missing font errors
            preamble = '#set page(columns: 2)\n\n'
        
        with open(tmp_typst, 'w', encoding='utf-8') as f:
            f.write(preamble + typst_src)

        # Compile Typst to PDF
        subprocess.run(["typst", "compile", tmp_typst, output_pdf_path], check=True)
    except FileNotFoundError:
        print("[ERROR] Missing typst or pandoc executable on system.")
        raise
    finally:
        if os.path.exists(tmp_md): os.remove(tmp_md)
        if os.path.exists(tmp_typst): os.remove(tmp_typst)
        for svg in svg_files:
            if os.path.exists(svg): os.remove(svg)

def render_with_pandoc_latex(md_content, output_pdf_path):
    tmp_md = output_pdf_path.replace(".pdf", ".md")
    with open(tmp_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    try:
        # Render using xelatex via Pandoc with Book template
        subprocess.run(["pandoc", tmp_md, "-o", output_pdf_path, "--pdf-engine=xelatex", "-V", "documentclass=book", "-V", "classoption=twoside"], check=True)
    except FileNotFoundError:
        print("[ERROR] Missing pandoc or xelatex executable on system.")
        raise
    finally:
        if os.path.exists(tmp_md): os.remove(tmp_md)

def render_pdf(category, md_content, output_pdf_path):
    if category in ["Academic", "Notebook", "Cursed"]:
        render_with_typst(md_content, output_pdf_path, category)
    elif category == "Book":
        render_with_pandoc_latex(md_content, output_pdf_path)
    else:
        render_with_weasyprint(md_content, output_pdf_path)
