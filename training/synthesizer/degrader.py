import subprocess
import os
import random
import glob
import json
import shutil

def apply_degradation(pdf_path):
    """
    Applies heavy degradation to a random subset of pages in the PDF.
    Saves the original clean PDF, rasterizes selected pages to strip text layers,
    and writes a JSON manifest of which pages were degraded.
    """
    clean_pdf_path = pdf_path.replace(".pdf", "_clean.pdf")
    manifest_path = pdf_path.replace(".pdf", "_degradation.json")
    
    # 1. Save original clean copy
    shutil.copy2(pdf_path, clean_pdf_path)
    
    work_dir = os.path.dirname(pdf_path)
    base_name = os.path.basename(pdf_path).replace(".pdf", "")
    page_pattern = os.path.join(work_dir, f"{base_name}_page_%03d.pdf")
    
    try:
        # 2. Split PDF into individual pages
        gs_split_cmd = [
            "gs", "-dBATCH", "-dNOPAUSE", "-dQUIET", "-sDEVICE=pdfwrite",
            f"-sOutputFile={page_pattern}", pdf_path
        ]
        subprocess.run(gs_split_cmd, check=True)
        
        # 3. Find all extracted pages
        extracted_pages = sorted(glob.glob(os.path.join(work_dir, f"{base_name}_page_*.pdf")))
        if not extracted_pages:
            return
            
        # 4. Pick a random subset to degrade (30% to 70% of pages)
        num_pages = len(extracted_pages)
        # Always degrade at least 1 page if there are multiple, or just 1 if only 1
        num_to_degrade = max(1, int(num_pages * random.uniform(0.3, 0.7)))
        pages_to_degrade = sorted(random.sample(range(num_pages), num_to_degrade))
        
        degraded_indices_1_based = []
        
        # 5. Rasterize the chosen pages
        for idx in pages_to_degrade:
            page_pdf = extracted_pages[idx]
            page_png = page_pdf.replace(".pdf", ".png")
            page_raster_pdf = page_pdf.replace(".pdf", "_raster.pdf")
            
            # Convert PDF to PNG (low res noise)
            subprocess.run([
                "gs", "-dQUIET", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dNOPROMPT",
                "-sDEVICE=pnggray", "-r100", f"-sOutputFile={page_png}", page_pdf
            ], check=True)
            
            # Convert PNG back to PDF
            subprocess.run(["magick", page_png, page_raster_pdf], check=True)
            
            # Replace the clean extracted page with the rasterized one
            os.replace(page_raster_pdf, page_pdf)
            degraded_indices_1_based.append(idx + 1)
            
            if os.path.exists(page_png):
                os.remove(page_png)
                
        # 6. Recombine all pages back into the main PDF path
        gs_merge_cmd = [
            "gs", "-dBATCH", "-dNOPAUSE", "-dQUIET", "-sDEVICE=pdfwrite",
            f"-sOutputFile={pdf_path}"
        ] + extracted_pages
        subprocess.run(gs_merge_cmd, check=True)
        
        # 7. Write manifest
        with open(manifest_path, 'w') as f:
            json.dump({
                "total_pages": num_pages,
                "degraded_pages": degraded_indices_1_based,
                "clean_pdf": os.path.basename(clean_pdf_path)
            }, f, indent=2)
            
    except Exception as e:
        print(f"[WARNING] Degradation failed on {pdf_path}: {e}")
        
    finally:
        # Cleanup temporary page PDFs
        for p in glob.glob(os.path.join(work_dir, f"{base_name}_page_*.pdf")):
            try:
                os.remove(p)
            except:
                pass
