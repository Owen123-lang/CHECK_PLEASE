require("dotenv").config();

const { Pool } = require("pg");

// Configure pool with proper settings for Neon/serverless PostgreSQL
const pool = new Pool({
    connectionString: process.env.PG_CONNECTION_STRING,
    ssl: {
        rejectUnauthorized: false,
    },
    // Connection pool settings optimized for serverless
    max: 20, // Maximum number of clients in the pool
    idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
    connectionTimeoutMillis: 10000, // Return an error after 10 seconds if connection could not be established
});

// Handle pool errors to prevent crashes
pool.on('error', (err, client) => {
    console.error('Unexpected error on idle client', err);
    // Don't exit the process, just log the error
});

const connect = async () => {
    try {
        const client = await pool.connect();
        console.log("Connected to the database");
        client.release();
    }
    catch (error) {
        console.error("Error connecting to the database", error);
    }
}

connect();

const query = async (text, params) => {
    const client = await pool.connect();
    try {
        const res = await client.query(text, params);
        return res;
    }
    catch (error) {
        console.error("Error executing query", error);
        throw error;
    }
    finally {
        client.release();
    }
}

module.exports = {
    query,
    pool, // Export pool for graceful shutdown if needed
};