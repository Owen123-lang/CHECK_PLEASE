const db = require("../database/pg.database");

exports.registerUser = async (name, email, hash) => {
  try {
    const res = await db.query(
      `INSERT INTO users (name, email, password) 
             VALUES ($1, $2, $3) 
             RETURNING *`,
      [name, email, hash]
    );

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};

// Endpoint to make account with role (for development purpose only)
exports.registerUserByAdmin = async (name, email, hash, role) => {
    try {
        const res = await db.query(
            `INSERT INTO users (name, email, password, role)
             VALUES ($1, $2, $3, $4)
             RETURNING *`,
            [name, email, hash, role]
        );

        if (!res?.rows[0]) {
            return null;
        }

        return res.rows[0];
    }
    catch (error) {
        console.error("Error executing query", error);
    }
};

exports.getUserByEmail = async (email) => {
  try {
    const res = await db.query("SELECT * FROM users WHERE email = $1", [email]);

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};

exports.updateRole = async (email, user) => {
  try {
    const res = await db.query(
      `UPDATE users 
             SET role = $1
             WHERE email = $2 
             RETURNING *`,
      [user.role, email]
    );

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};

exports.updateName = async (email, user) => {
  try {
    const res = await db.query(
      "UPDATE users SET name = $1 WHERE email = $2 RETURNING *",
      [user.name, email]
    );

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};

exports.updatePassword = async (email, hash) => {
  try {
    const res = await db.query(
      "UPDATE users SET password = $1 WHERE email = $2 RETURNING *",
      [hash, email]
    );

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};

exports.deleteUser = async (email) => {
  try {
    const res = await db.query(
      "DELETE FROM users WHERE email = $1 RETURNING *",
      [email]
    );

    if (!res?.rows[0]) {
      return null;
    }

    return res.rows[0];
  } catch (error) {
    console.error("Error executing query", error);
  }
};