const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    context: __dirname,
    mode: 'development',
    entry: './eodhp_web_presence/eodhp_web_presence/static/scss/main.scss',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'eodhp_web_presence/eodhp_web_presence/static/dist'),
    },
    plugins: [
        new BundleTracker({ filename: 'webpack-stats.json' }),
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