const router = require("express").Router();
const { authenticate, authorize } = require("../middleware/auth.middleware");
const chatController = require("../controllers/chat.controller");

router.post("/", authenticate, chatController.createChat);
router.get("/notebook/:notebookId", authenticate, chatController.getAllChats);
router.get("/notebook/:notebookId/:id", authenticate, chatController.getChat);
router.put("/notebook/:notebookId/:id", authenticate, chatController.updateChat);
router.delete("/notebook/:notebookId/:id", authenticate, chatController.deleteChat);

module.exports = router;
