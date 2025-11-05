const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || "32d2d17234b07cbdc1bced20a5ed311a1b00b3fc668b6fe6754f72fb19161c6e";
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '6h';

exports.generateToken = (payload) => {
    try {
        const token = jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
        return token;
    } 
    catch (error) {
        console.error('Token generation error:', error);
        throw error;
    }
};

exports.verifyToken = (token) => {
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        return decoded;
    } 
    catch (error) {
        console.error('Token verification error:', error);
        return null;
    }
};
