const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');


module.exports = {
    context: __dirname,
    mode: 'development',
    entry: './eodhp_web_presence/eodhp_web_presence/static/scss/main.scss',
    output: {
        filename: "[name]-[contenthash].js",
        path: path.resolve(__dirname, "assets/webpack_bundles/"),
        publicPath: process.env.NODE_ENV === 'development' ? 'http://localhost:3000/static/' : '/static/'
    },
    devServer: {
        compress: true,
        port: 3000,
        hot: true,
        host: '0.0.0.0',
        headers: { 'Access-Control-Allow-Origin': '*' },
        static: {
            directory: path.join(__dirname, 'assets/webpack_bundles/'),
            publicPath: '/static/',
            watch: true,
        }
    },
    plugins: [
        new BundleTracker({ path: __dirname, filename: 'webpack-stats.json' }),
        new webpack.HotModuleReplacementPlugin(),
    ],
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'sass-loader',
                ],
            },
        ],
    },
};
