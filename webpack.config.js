const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    context: __dirname,
    mode: 'development',
    entry: './eodhp_web_presence/eodhp_web_presence/static/scss/main.scss',
    output: {
        filename: "[name]-[contenthash].js",
        path: path.resolve(__dirname, "assets/webpack_bundles/"),
        publicPath: "/static/"
    },
    plugins: [
        new BundleTracker({ path: __dirname, filename: 'webpack-stats.json' }),
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
