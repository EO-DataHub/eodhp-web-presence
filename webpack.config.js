const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');


module.exports = {
    context: __dirname,
    mode: process.env.NODE_ENV,
    entry: {
        main: './eodhp_web_presence/eodhp_web_presence/static/entrypoint.js',
        access_page: './eodhp_web_presence/home/static/js/access_page.js',
    },
    output: {
        filename: process.env.NODE_ENV === 'development' ? '[name].js' : '[name]-[contenthash].js',
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
                test: /\.(scss|css)$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'sass-loader',
                ],
            },
            {
                test: /\.(?:js|mjs|cjs)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', { targets: "defaults" }]
                        ]
                    }
                }
            }
        ],
    },
};
