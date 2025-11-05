const db = require("../database/pg.database");

exports.createNotebook = async (userId, title, body) => {
    try {
        const res = await db.query(
            `INSERT INTO notebook (user_id, title, body)
             VALUES ($1, $2, $3)
             RETURNING *`,
            [userId, title, body]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getNotebookById = async (id, userId) => {
    try {
        const res = await db.query(
            `SELECT * FROM notebook 
             WHERE id = $1 AND user_id = $2`,
            [id, userId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getAllNotebooks = async (userId) => {
    try {
        const res = await db.query(
            `SELECT * FROM notebook 
             WHERE user_id = $1 
             ORDER BY created_at DESC`,
            [userId]
        );

        return res.rows;
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.updateNotebook = async (id, userId, title, body) => {
    try {
        const res = await db.query(
            `UPDATE notebook 
             SET title = $1, body = $2 
             WHERE id = $3 AND user_id = $4 
             RETURNING *`,
            [title, body, id, userId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.deleteNotebook = async (id, userId) => {
    try {
        const res = await db.query(
            `DELETE FROM notebook 
             WHERE id = $1 AND user_id = $2 
             RETURNING *`,
            [id, userId]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};
