const pdfRepository = require("../repositories/pdf.repository");
const baseResponse = require("../utils/baseResponse.util");

exports.createPdf = async (req, res) => {
    const { fileUrl } = req.body;
    const userId = req.user.id;

    if (!fileUrl) {
        return baseResponse(res, false, 400, "File URL is required", null);
    }

    try {
        const pdf = await pdfRepository.createPdf(userId, fileUrl);

        if (!pdf) {
            return baseResponse(res, false, 400, "Failed to create PDF record", null);
        }

        return baseResponse(res, true, 201, "PDF record created", pdf);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getPdf = async (req, res) => {
    const { id } = req.params;
    const userId = req.user.id;

    try {
        const pdf = await pdfRepository.getPdfById(id, userId);

        if (!pdf) {
            return baseResponse(res, false, 404, "PDF not found", null);
        }

        return baseResponse(res, true, 200, "PDF found", pdf);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getAllPdfs = async (req, res) => {
    const userId = req.user.id;

    try {
        const pdfs = await pdfRepository.getAllPdfs(userId);
        return baseResponse(res, true, 200, "PDFs retrieved successfully", pdfs);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.deletePdf = async (req, res) => {
    const { id } = req.params;
    const userId = req.user.id;

    try {
        const pdf = await pdfRepository.deletePdf(id, userId);

        if (!pdf) {
            return baseResponse(res, false, 404, "PDF not found", null);
        }

        return baseResponse(res, true, 200, "PDF deleted successfully", pdf);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};
