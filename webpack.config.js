const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const StyleLintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const webpack = require('webpack');
const { GitRevisionPlugin } = require('git-revision-webpack-plugin')


module.exports = {
    context: __dirname,
    mode: process.env.NODE_ENV,
    entry: {
        // This is included on every page.
        'main': './eodhp_web_presence/eodhp_web_presence/js-src/entrypoint.js',

        'fake-catalogue': {
            import: ['./eodhp_web_presence/eodhp_web_presence/js-src/fake-catalogue/index.js'],
            dependOn: ['main'],
        },
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
            emitError: true,
            cache: true,
            customSyntax: 'postcss-sass'
        }),
        new ESLintPlugin({
            formatter: require('eslint-friendly-formatter'),
            cache: true,
            emitError: true,
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


// This adds a __VERSION__ variable (more like a search-and-replace than a variable)
// so that we can put the Git revision in the HTML in version.js.
if (process.env.GITHUB_REF_NAME) {
    module.exports.plugins.push(new webpack.DefinePlugin({
        __VERSION__: JSON.stringify(process.env.GITHUB_REF_NAME + "-" + process.env.GITHUB_SHA),
    }))
} else {
    const gitRevisionPlugin = new GitRevisionPlugin()

    module.exports.plugins.push(
        gitRevisionPlugin,

        new webpack.DefinePlugin({
            __VERSION__: JSON.stringify(gitRevisionPlugin.version()),
        }),
    )
}
