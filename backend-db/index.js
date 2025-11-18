const express = require("express");
const cloudinary = require("cloudinary").v2;
require("dotenv").config();

// Configure Cloudinary
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

const app = express();
const PORT = process.env.PORT || 3000;
const cors = require("cors");

const corsOptions = {
  origin: [
    "http://localhost:5173",
  ],
  methods: ["GET", "POST", "PUT", "DELETE"],
  credentials: true,
};
app.use(cors(corsOptions));

app.use(express.json());

app.use("/api/users", require("./src/routes/user.route"));
app.use("/api/notebooks", require("./src/routes/notebook.route"));
app.use("/api/pdfs", require("./src/routes/pdf.route"));
app.use("/api/chat", require("./src/routes/chat.route"));

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
