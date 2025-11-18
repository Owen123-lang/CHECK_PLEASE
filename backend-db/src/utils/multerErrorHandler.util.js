const multer = require("multer");

const multerErrorHandler = (error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({
                status: false,
                code: 400,
                message: "File size exceeds 50MB limit",
                data: null
            });
        }
        if (error.code === 'LIMIT_PART_COUNT') {
            return res.status(400).json({
                status: false,
                code: 400,
                message: "Too many file parts",
                data: null
            });
        }
        return res.status(400).json({
            status: false,
            code: 400,
            message: error.message,
            data: null
        });
    }
    if (error) {
        return res.status(400).json({
            status: false,
            code: 400,
            message: error.message || "File upload error",
            data: null
        });
    }
    next();
};

module.exports = multerErrorHandler;
