const db = require("../database/pg.database");

exports.createChat = async (notebookId, sender, body) => {
    try {
        const res = await db.query(
            `INSERT INTO chat (notebook_id, sender, body)
             VALUES ($1, $2, $3)
             RETURNING *`,
            [notebookId, sender, body]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getChatById = async (id, notebookId) => {
    try {
        const res = await db.query(
            `SELECT * FROM chat 
             WHERE id = $1 AND notebook_id = $2`,
            [id, notebookId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getChatsByNotebookId = async (notebookId) => {
    try {
        const res = await db.query(
            `SELECT * FROM chat 
             WHERE notebook_id = $1 
             ORDER BY created_at ASC`,
            [notebookId]
        );

        return res.rows;
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.updateChat = async (id, notebookId, body) => {
    try {
        const res = await db.query(
            `UPDATE chat 
             SET body = $1 
             WHERE id = $2 AND notebook_id = $3 
             RETURNING *`,
            [body, id, notebookId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.deleteChat = async (id, notebookId) => {
    try {
        const res = await db.query(
            `DELETE FROM chat 
             WHERE id = $1 AND notebook_id = $2 
             RETURNING *`,
            [id, notebookId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};
