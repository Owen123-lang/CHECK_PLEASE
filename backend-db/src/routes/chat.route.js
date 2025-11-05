const router = require("express").Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const chatController = require("../controllers/chat.controller");
const authMiddleware = require("../middleware/auth.middleware");

router.post("/", chatController.createChat);
router.get("/notebook/:notebookId", chatController.getAllChats);
router.get("/notebook/:notebookId/:id", chatController.getChat);
router.put("/notebook/:notebookId/:id", chatController.updateChat);
router.delete("/notebook/:notebookId/:id", chatController.deleteChat);

module.exports = router;
