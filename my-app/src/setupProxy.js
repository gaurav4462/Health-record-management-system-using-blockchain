const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        '/api/v0/add',
        createProxyMiddleware({
            target: 'http://localhost:5001', // IPFS API is on port 5001
            changeOrigin: true,
        })
    );
};
