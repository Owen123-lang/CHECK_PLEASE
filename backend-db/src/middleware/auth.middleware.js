const { verifyToken } = require('../utils/jwt.util');
const baseResponse = require('../utils/baseResponse.util');

exports.authenticate = (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader) {
            return baseResponse(res, false, 401, "No authorization header", null);
        }

        const token = authHeader.split(' ')[1];
        const decoded = verifyToken(token);
        
        if (!decoded) {
            return baseResponse(res, false, 401, "Invalid token", null);
        }

        req.user = decoded;
        next();
    } 
    catch (error) {
        return baseResponse(res, false, 401, "Authentication failed", null);
    }
};

exports.authorize = (...roles) => {
    return (req, res, next) => {
        if (!req.user) {
            return baseResponse(res, false, 401, "User not authenticated");
        }

        if (!roles.includes(req.user.role)) {
            return baseResponse(res, false, 403, "User not authorized for this action");
        }

        next();
    };
};
