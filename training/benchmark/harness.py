"""
Playwright harness for benchmarking the real litedoc-core.js engine.

Drives headless Chromium, loads the LiteDoc app, injects tuning parameters
via window.__litedocTunerConfig, feeds PDFs as File objects, and captures
the real Markdown output from state.processedData.
"""
import os
import json
import base64
from playwright.sync_api import sync_playwright

# Path to the LiteDoc entry point (relative to project root)
LITEDOC_HTML = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'index.html')

def extract_markdown_with_litedoc(pdf_path, params, page=None, enable_ocr=True, pdf_b64=None):
    """
    Spins up Playwright (or reuses a page), loads the real LiteDoc app,
    injects tuning parameters, feeds the PDF, and returns the Markdown.
    """
    html_path = f"file://{os.path.abspath(LITEDOC_HTML)}"
    abs_pdf = os.path.abspath(pdf_path)
    
    if pdf_b64 is None:
        with open(abs_pdf, 'rb') as f:
            pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
            
    pdf_name = os.path.basename(abs_pdf)
    
    # Internal runner if page is not provided
    if page is None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                # 1. Load the LiteDoc UI
                page.goto(html_path, wait_until="load", timeout=30000)
                
                # Set the OCR flag directly in memory and reset
                page.evaluate(f"""
                    if (typeof window.__litedocAddons !== 'undefined' && window.__litedocAddons._settings) {{
                        window.__litedocAddons._settings.ocrEnabled = {str(enable_ocr).lower()};
                    }}
                    if (typeof window.resetTool === 'function') {{
                        window.resetTool(true);
                    }}
                """)
                
                # 2. Inject the tuning parameters
                page.evaluate(f"window.__litedocTunerConfig = {json.dumps(params)};")
                
                # 3. Perform conversion
                return _run_conversion_in_page(page, pdf_b64, pdf_name)
            except Exception as e:
                return f"ERROR: Playwright crash - {str(e)}"
            finally:
                browser.close()
    else:
        # Reusing the existing page
        try:
            # Set the OCR flag directly in memory and clear previous tool states
            page.evaluate(f"""
                if (typeof window.__litedocAddons !== 'undefined' && window.__litedocAddons._settings) {{
                    window.__litedocAddons._settings.ocrEnabled = {str(enable_ocr).lower()};
                }}
                if (typeof window.resetTool === 'function') {{
                    window.resetTool(true);
                }}
            """)
            
            # Inject parameters
            page.evaluate(f"window.__litedocTunerConfig = {json.dumps(params)};")
            
            # Perform conversion
            return _run_conversion_in_page(page, pdf_b64, pdf_name)
        except Exception as e:
            return f"ERROR: Playwright reuse crash - {str(e)}"


def _run_conversion_in_page(page, pdf_b64, pdf_name):
    """Helper to execute conversion inside loaded page context."""
    return page.evaluate("""
        async ([b64, filename]) => {
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('LiteDoc extraction timeout after 180s')), 180000)
            );
            
            const extractPromise = (async () => {
                try {
                    // Decode base64 to binary
                    const binary = atob(b64);
                    const bytes = new Uint8Array(binary.length);
                    for (let i = 0; i < binary.length; i++) {
                        bytes[i] = binary.charCodeAt(i);
                    }
                    
                    // Create a real File object
                    const file = new File([bytes], filename, { type: 'application/pdf' });
                    
                    if (typeof window.executePdfConversion === 'undefined') {
                        return "ERROR: executePdfConversion not found on window";
                    }
                    
                    await window.executePdfConversion([file]);
                    
                    if (typeof state !== 'undefined' && state.processedData && state.processedData.length > 0) {
                        return state.processedData[0].mdText || "";
                    }
                    
                    return "ERROR: state.processedData empty after conversion";
                } catch (e) {
                    return "ERROR: " + e.toString();
                }
            })();
            
            try {
                return await Promise.race([extractPromise, timeoutPromise]);
            } catch (e) {
                return "ERROR: " + e.toString();
            }
        }
    """, [pdf_b64, pdf_name])


def smoke_test(params=None):
    """
    Quick sanity check: run one extraction and verify we get non-error output.
    Returns True if the harness is functional.
    """
    if params is None:
        params = {}
    
    # Find any PDF in source_materials
    import glob
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'source_materials')
    pdfs = glob.glob(os.path.join(data_dir, '**', '*.pdf'), recursive=True)
    
    if not pdfs:
        print("[SMOKE TEST] No PDFs found in source_materials/")
        return False
    
    test_pdf = pdfs[0]
    print(f"[SMOKE TEST] Testing with {test_pdf}...")
    result = extract_markdown_with_litedoc(test_pdf, params)
    
    if result.startswith("ERROR:"):
        print(f"[SMOKE TEST] FAILED: {result}")
        return False
    
    if not result or len(result.strip()) < 10:
        print(f"[SMOKE TEST] FAILED: Output too short ({len(result)} chars)")
        return False
    
    print(f"[SMOKE TEST] PASSED: Got {len(result)} chars of Markdown")
    return True
