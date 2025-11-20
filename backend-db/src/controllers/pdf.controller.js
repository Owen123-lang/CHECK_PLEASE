const pdfRepository = require("../repositories/pdf.repository");
const baseResponse = require("../utils/baseResponse.util");
const cloudinary = require("cloudinary").v2;
const { Readable } = require("stream");

exports.createPdf = async (req, res) => {
    const userId = req.user.id;

    // Get file from any field name (files is array from .any())
    const file = req.files && req.files.length > 0 ? req.files[0] : null;

    if (!file) {
        return baseResponse(res, false, 400, "PDF file is required", null);
    }

    // Validate file type
    if (file.mimetype !== 'application/pdf') {
        return baseResponse(res, false, 400, "Only PDF files are allowed", null);
    }

    try {
        // Upload to Cloudinary
        const result = await new Promise((resolve, reject) => {
            const stream = cloudinary.uploader.upload_stream(
                {
                    resource_type: "raw",
                    folder: `check_please/pdfs/${userId}`,
                    public_id: file.originalname.split('.')[0],
                    format: "pdf"
                },
                (error, result) => {
                    if (error) reject(error);
                    else resolve(result);
                }
            );
            Readable.from(file.buffer).pipe(stream);
        });

        const fileUrl = result.secure_url;
        const cloudinaryPublicId = result.public_id;

        // Save to database
        const pdf = await pdfRepository.createPdf(userId, fileUrl, cloudinaryPublicId);

        if (!pdf) {
            return baseResponse(res, false, 400, "Failed to create PDF record", null);
        }

        return baseResponse(res, true, 201, "PDF uploaded successfully", pdf);
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
        // Get PDF first to retrieve cloudinary_public_id
        const pdf = await pdfRepository.getPdfById(id, userId);
        if (!pdf) {
            return baseResponse(res, false, 404, "PDF not found", null);
        }

        // Delete from Cloudinary using public_id
        if (pdf.cloudinary_public_id) {
            try {
                await cloudinary.uploader.destroy(pdf.cloudinary_public_id, {
                    resource_type: 'raw'
                });

                console.log(`Deleted from Cloudinary: ${pdf.cloudinary_public_id}`);
            } catch (cloudinaryError) {
                console.error("Cloudinary deletion error:", cloudinaryError);
                // Continue with database deletion even if Cloudinary deletion fails
            }
        }

        // Delete from database
        const deletedPdf = await pdfRepository.deletePdf(id, userId);

        if (!deletedPdf) {
            return baseResponse(res, false, 404, "PDF not found", null);
        }

        return baseResponse(res, true, 200, "PDF deleted successfully", deletedPdf);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.updatePdf = async (req, res) => {
    const { id } = req.params;
    const userId = req.user.id;

    // Get file from any field name (files is array from .any())
    const file = req.files && req.files.length > 0 ? req.files[0] : null;

    if (!file) {
        return baseResponse(res, false, 400, "PDF file is required", null);
    }

    // Validate file type
    if (file.mimetype !== 'application/pdf') {
        return baseResponse(res, false, 400, "Only PDF files are allowed", null);
    }

    try {
        // Get old PDF first
        const oldPdf = await pdfRepository.getPdfById(id, userId);
        if (!oldPdf) {
            return baseResponse(res, false, 404, "PDF not found", null);
        }

        // Upload new file to Cloudinary
        const result = await new Promise((resolve, reject) => {
            const stream = cloudinary.uploader.upload_stream(
                {
                    resource_type: "raw",
                    folder: `check_please/pdfs/${userId}`,
                    public_id: file.originalname.split('.')[0],
                    format: "pdf"
                },
                (error, result) => {
                    if (error) reject(error);
                    else resolve(result);
                }
            );
            Readable.from(file.buffer).pipe(stream);
        });

        const fileUrl = result.secure_url;
        const cloudinaryPublicId = result.public_id;

        // Delete old file from Cloudinary
        if (oldPdf.cloudinary_public_id) {
            try {
                await cloudinary.uploader.destroy(oldPdf.cloudinary_public_id, {
                    resource_type: 'raw'
                });

                console.log(`Deleted old file from Cloudinary: ${oldPdf.cloudinary_public_id}`);
            } catch (cloudinaryError) {
                console.error("Cloudinary deletion error:", cloudinaryError);
                // Continue with database update even if Cloudinary deletion fails
            }
        }

        // Update database with new file
        const pdf = await pdfRepository.updatePdf(id, userId, fileUrl, cloudinaryPublicId);

        if (!pdf) {
            return baseResponse(res, false, 400, "Failed to update PDF record", null);
        }

        return baseResponse(res, true, 200, "PDF updated successfully", pdf);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};
