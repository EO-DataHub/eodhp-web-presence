const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const StyleLintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const webpack = require('webpack');


module.exports = {
    context: __dirname,
    mode: process.env.NODE_ENV,
    entry: {
        // This is included on every page.
        'main': './eodhp_web_presence/eodhp_web_presence/js-src/entrypoint.js',

    },
    output: {
        filename: "[name]-[contenthash].js",
        path: path.resolve(__dirname, "assets/webpack_bundles/"),
        publicPath: process.env.NODE_ENV === 'development' ? 'http://localhost:3000/static/' : '/static/webpack_bundles/'
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
        new StyleLintPlugin({
            failOnError: false,
            configFile: '.stylelintrc',
            files: ['**/*.sass'],
            context: 'js-src',
            quiet: false,
            emitError: false,
            cache: true,
            customSyntax: 'postcss-sass'
        }),
        new ESLintPlugin({
            formatter: require('eslint-friendly-formatter'),
            cache: true,
            emitWarning: true,
            outputReport: {
                filePath: "../../target/checkstyle.xml",
                formatter: 'checkstyle'
            }
        }),
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
        ],
    },
};
