const express = require("express");
const router = express.Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const pdfController = require("../controllers/pdf.controller");

router.post("/", pdfController.createPdf);
router.get("/", pdfController.getAllPdfs);
router.get("/:id", pdfController.getPdf);
router.delete("/:id", pdfController.deletePdf);

module.exports = router;
