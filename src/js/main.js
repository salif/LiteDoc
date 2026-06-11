/**
 * LiteDoc Central Orchestrator
 * Resolves load-order crashes and securely manages module mounting.
 */

// 3. Safely Mount Modules on Boot
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Boot] Mounting LiteDoc sub-modules...');

    // 0. (Service Worker registration removed for standalone HTML release)

    // Auto-inject logic removed because it conflicts with the build script bundler.
    // Core scripts are bundled inline.

    // 2. PDF.js Worker Initialization (delayed to ensure pdf.js is loaded)
    if (typeof pdfjsLib !== 'undefined') {
        // Configure comprehensive PDF.js options for maximum format support
        pdfjsLib.GlobalWorkerOptions.workerPort = null;

        // Default worker URL (build.py will patch this with a data URI)
        if (!pdfjsLib.GlobalWorkerOptions.workerSrc) {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        }

        // If the worker is already configured (e.g. inlined as a data URI or pointing to a CDN by the build script), skip detection
        const currentSrc = pdfjsLib.GlobalWorkerOptions.workerSrc || '';
        if (currentSrc.startsWith('data:') || currentSrc.startsWith('http')) {
            console.info('[Boot] PDF.js worker already configured.');
        } else if (window.location.protocol === 'file:') {
            console.info('[Boot] Running on file:// protocol. Using CDN for PDF.js worker.');
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        } else {
            try {
                // Try local worker first, but catch the 404 to avoid console noise if possible
                // Using { method: 'HEAD' } is better than a full GET but still shows 404 in most browsers
                const res = await fetch('js/pdf.worker.min.js', { method: 'HEAD' });
                if (res.ok || res.status === 0) {
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'js/pdf.worker.min.js';
                } else {
                    throw new Error('Local worker not found');
                }
            } catch (e) {
                console.info('[Boot] Local PDF.js worker not found or inaccessible. Falling back to CDN...');
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            }
        }

        console.info('[Boot] PDF.js worker configured successfully.');
    }

    try {
        // Execute modular initialization if the modules define them
        if (typeof window.initUI === 'function') window.initUI();
        if (typeof window.initOCR === 'function') window.initOCR();
        if (typeof window.initAddons === 'function') window.initAddons();

        // Verify critical components loaded
        if (typeof window.executePdfConversion !== 'function' && typeof window.startConversionLogic !== 'function') {
            console.warn('[Boot] pdf-parser.js has not registered the conversion engine yet.');
        }

        // Fire and forget: Precache OCR models in the background
        if (window.__litedocOCR && typeof window.__litedocOCR.precacheModels === 'function') {
            if (!window.__litedocAddons || window.__litedocAddons.ocrEnabled()) {
                window.__litedocOCR.precacheModels();
            }
        }

        console.log('[Boot] Sequence complete.');
    } catch (error) {
        console.error('[Boot] Critical module initialization failure:', error);
        if (typeof window.showAlert === 'function') {
            window.showAlert('Initialization Error', 'A critical module failed to load. Please check the console and refresh the page.');
        }
    }

    // 4. Remove Splash Screen / Preloader (FOUC protection)
    setTimeout(() => {
        const preloader = document.getElementById('app-preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
            setTimeout(() => preloader.remove(), 500); // Wait for fade transition
        }
    }, 150); // Slight delay ensures Tailwind paints first
});

// 4. Central Conversion Pipeline Hook for dropzone.js
window.startConversion = async function (filesToProcess) {
    if (typeof window.executePdfConversion === 'function') {
        return await window.executePdfConversion(filesToProcess);
    } else {
        console.error('[Orchestrator] PDF Parser module is missing or crashed during load.');
        if (typeof window.showAlert === 'function') {
            window.showAlert('System Error', 'The PDF Parser module failed to load. Please ensure your script tags are correct in index.html.');
        }
    }
};