const express = require("express");
const { authenticate, authorize } = require("../middleware/auth.middleware");
const userController = require("../controllers/user.controller");
const router = express.Router();

router.post("/register", userController.registerUser);
router.post('/register/admin', userController.registerUserByAdmin);
router.post("/login", userController.loginUser);
router.get("/:email", userController.getUser);
router.put("/:email/role", authenticate, authorize("admin"), userController.updateRole);
router.put("/:email/name", authenticate, userController.updateName);
router.put("/:email/password", authenticate, userController.updatePassword);
router.delete("/:email", authenticate, userController.deleteUser);

module.exports = router;
