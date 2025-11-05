const express = require("express");
const router = express.Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const notebookController = require("../controllers/notebook.controller");

router.post("/", notebookController.createNotebook);
router.get("/", notebookController.getAllNotebooks);
router.get("/:id", notebookController.getNotebook);
router.put("/:id", notebookController.updateNotebook);
router.delete("/:id", notebookController.deleteNotebook);

module.exports = router;
