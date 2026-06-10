/**
 * LiteDoc Central Orchestrator
 * Resolves load-order crashes and securely manages module mounting.
 */

// 3. Safely Mount Modules on Boot
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Boot] Mounting LiteDoc sub-modules...');

    // 0. Register Service Worker for PWA / Offline capabilities
    if ('serviceWorker' in navigator && window.location.protocol !== 'file:') {
        try {
            await navigator.serviceWorker.register('./sw.js');
            console.log('[Boot] Service Worker registered successfully.');
        } catch (e) {
            console.warn('[Boot] Service Worker registration failed:', e);
        }
    }

    // Auto-inject logic removed because it conflicts with the build script bundler.
    // Core scripts are bundled inline.

    // 2. PDF.js Worker Initialization (delayed to ensure pdf.js is loaded)
    if (typeof pdfjsLib !== 'undefined') {
        // Configure comprehensive PDF.js options for maximum format support
        pdfjsLib.GlobalWorkerOptions.workerPort = null;

        if (window.location.protocol === 'file:') {
            console.info('[Boot] Running on file:// protocol. Using CDN for PDF.js worker.');
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        } else {
            try {
                const res = await fetch('js/pdf.worker.min.js', { method: 'HEAD' });
                if (res.ok || res.status === 0) {
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'js/pdf.worker.min.js';
                } else {
                    throw new Error('Local worker not found');
                }
            } catch (e) {
                console.warn('[Boot] Local PDF.js worker not found. Falling back to CDN...');
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