const db = require("../database/pg.database");

exports.createPdf = async (userId, fileUrl) => {
    try {
        const res = await db.query(
            `INSERT INTO pdf (user_id, file_url)
             VALUES ($1, $2)
             RETURNING *`,
            [userId, fileUrl]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getPdfById = async (id, userId) => {
    try {
        const res = await db.query(
            `SELECT * FROM pdf 
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

exports.getAllPdfs = async (userId) => {
    try {
        const res = await db.query(
            `SELECT * FROM pdf 
             WHERE user_id = $1 
             ORDER BY created_at DESC`,
            [userId]
        );

        return res.rows;
    } catch (error) {
        console.error("Error executing query", error);
    }
};

exports.deletePdf = async (id, userId) => {
    try {
        const res = await db.query(
            `DELETE FROM pdf 
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
