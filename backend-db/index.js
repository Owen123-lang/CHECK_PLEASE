const express = require("express");
require("dotenv").config();

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

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
