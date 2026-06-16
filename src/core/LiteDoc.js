import * as pdfParser from './layout/pdf-parser.js';
import * as addons from './extraction/addons.js';

export default class LiteDoc {
    constructor(config = {}) {
        this.config = config;
        if (typeof window !== 'undefined' && addons.initAddons) {
            addons.initAddons();
        }
    }

    async parse(pdfSource) {
        return await pdfParser.executePdfConversion([pdfSource], this.config);
    }
}

if (typeof window !== 'undefined') {
    window.LiteDoc = LiteDoc;
    window.executePdfConversion = pdfParser.executePdfConversion;
}
