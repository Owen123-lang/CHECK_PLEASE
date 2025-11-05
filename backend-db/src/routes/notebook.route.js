const express = require("express");
const router = express.Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const notebookController = require("../controllers/notebook.controller");

router.post("/", authenticate, notebookController.createNotebook);
router.get("/", authenticate, notebookController.getAllNotebooks);
router.get("/:id", authenticate, notebookController.getNotebook);
router.put("/:id", authenticate, notebookController.updateNotebook);
router.delete("/:id", authenticate, notebookController.deleteNotebook);

module.exports = router;
