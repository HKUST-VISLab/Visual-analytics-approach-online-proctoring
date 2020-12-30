module.exports = {
    devServer: {
      disableHostCheck: true,
      headers: {
        "Access-Control-Allow-Origin": "*"
      },
      proxy: {
        "/api": {
          target: 'http://localhost:5003',
          ws: true,
          changeOrigin: true,
        }
      }
    }
  }