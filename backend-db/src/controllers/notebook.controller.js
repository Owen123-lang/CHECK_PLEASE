const notebookRepository = require("../repositories/notebook.repository");
const baseResponse = require("../utils/baseResponse.util");

exports.createNotebook = async (req, res) => {
    const { title, body } = req.body;
    const userId = req.user.id;

    try {
        const notebook = await notebookRepository.createNotebook(userId, title, body);

        if (!notebook) {
            return baseResponse(res, false, 400, "Failed to create notebook", null);
        }

        return baseResponse(res, true, 201, "Notebook created successfully", notebook);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getNotebook = async (req, res) => {
    const { id } = req.params;
    const userId = req.user.id;

    try {
        const notebook = await notebookRepository.getNotebookById(id, userId);

        if (!notebook) {
            return baseResponse(res, false, 404, "Notebook not found", null);
        }

        return baseResponse(res, true, 200, "Notebook found", notebook);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getAllNotebooks = async (req, res) => {
    const userId = req.user.id;

    try {
        const notebooks = await notebookRepository.getAllNotebooks(userId);
        return baseResponse(res, true, 200, "Notebooks retrieved successfully", notebooks);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.updateNotebook = async (req, res) => {
    const { id } = req.params;
    const { title, body } = req.body;
    const userId = req.user.id;

    try {
        const notebook = await notebookRepository.updateNotebook(id, userId, title, body);

        if (!notebook) {
            return baseResponse(res, false, 404, "Notebook not found", null);
        }

        return baseResponse(res, true, 200, "Notebook updated successfully", notebook);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.deleteNotebook = async (req, res) => {
    const { id } = req.params;
    const userId = req.user.id;

    try {
        const notebook = await notebookRepository.deleteNotebook(id, userId);

        if (!notebook) {
            return baseResponse(res, false, 404, "Notebook not found", null);
        }

        return baseResponse(res, true, 200, "Notebook deleted successfully", notebook);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};
