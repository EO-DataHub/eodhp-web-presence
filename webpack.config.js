const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');

const dotenv = require('dotenv');

require('dotenv').config();
dotenv.config();
const DJANGO_ENV = process.env.DJANGO_ENV;

module.exports = {
    context: __dirname,
    mode: 'development',
    entry: './eodhp_web_presence/eodhp_web_presence/static/scss/main.scss',
    output: {
        filename: "[name]-[contenthash].js",
        path: path.resolve(__dirname, "assets/webpack_bundles/"),
        publicPath: DJANGO_ENV === 'development' ? 'http://localhost:3000/static/' : '/static/'
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
            {
                test: /\.(png|jpg|jpeg|gif|svg|eot|ttf|woff|woff2)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[name]-[contenthash].[ext]',
                            publicPath: DJANGO_ENV === 'development' ? 'http://localhost:3000/static/' : '/static/',
                            outputPath: 'images/',
                        },
                    },
                ],
            }
        ],
    },
};
