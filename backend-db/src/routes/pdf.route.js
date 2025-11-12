const express = require("express");
const router = express.Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const pdfController = require("../controllers/pdf.controller");
const multer = require("multer");
const multerErrorHandler = require("../utils/multerErrorHandler.util");

// Configure Multer for in-memory PDF storage
const storage = multer.memoryStorage();
const fileFilter = (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
        cb(null, true);
    } else {
        cb(new Error('Only PDF files are allowed'), false);
    }
};
const uploadPdf = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

// Routes
router.post("/", authenticate, uploadPdf.any(), pdfController.createPdf);
router.get("/", authenticate, pdfController.getAllPdfs);
router.get("/:id", authenticate, pdfController.getPdf);
router.delete("/:id", authenticate, pdfController.deletePdf);

// Error handling middleware for Multer
router.use(multerErrorHandler);

module.exports = router;
