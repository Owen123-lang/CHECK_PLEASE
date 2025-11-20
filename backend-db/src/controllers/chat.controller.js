const chatRepository = require("../repositories/chat.repository");
const baseResponse = require("../utils/baseResponse.util");

exports.createChat = async (req, res) => {
    const { notebookId, sender, body } = req.body;

    if (!notebookId || !sender || !body) {
        return baseResponse(res, false, 400, "Missing required fields: notebookId, sender, body", null);
    }

    try {
        const chat = await chatRepository.createChat(notebookId, sender, body);

        if (!chat) {
            return baseResponse(res, false, 400, "Failed to create chat", null);
        }

        return baseResponse(res, true, 201, "Chat created successfully", chat);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getChat = async (req, res) => {
    const { id, notebookId } = req.params;

    try {
        const chat = await chatRepository.getChatById(id, notebookId);

        if (!chat) {
            return baseResponse(res, false, 404, "Chat not found", null);
        }

        return baseResponse(res, true, 200, "Chat found", chat);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.getAllChats = async (req, res) => {
    const { notebookId } = req.params;

    try {
        const chats = await chatRepository.getChatsByNotebookId(notebookId);
        return baseResponse(res, true, 200, "Chats retrieved successfully", chats);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.updateChat = async (req, res) => {
    const { id, notebookId } = req.params;
    const { body } = req.body;

    try {
        const chat = await chatRepository.updateChat(id, notebookId, body);

        if (!chat) {
            return baseResponse(res, false, 404, "Chat not found", null);
        }

        return baseResponse(res, true, 200, "Chat updated successfully", chat);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};

exports.deleteChat = async (req, res) => {
    const { id, notebookId } = req.params;

    try {
        const chat = await chatRepository.deleteChat(id, notebookId);

        if (!chat) {
            return baseResponse(res, false, 404, "Chat not found", null);
        }

        return baseResponse(res, true, 200, "Chat deleted successfully", chat);
    } catch (error) {
        console.error("Server error", error);
        return baseResponse(res, false, 500, "Server Error", null);
    }
};
