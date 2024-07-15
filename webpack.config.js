const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const StyleLintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const webpack = require('webpack');
const { GitRevisionPlugin } = require('git-revision-webpack-plugin')

const gitRevisionPlugin = new GitRevisionPlugin()


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

        // This allows us to use git-revision-version, git-revision-hash and git-revision-branch
        // in path substitutions later.
        gitRevisionPlugin,

        // This defines constants which are replaced in the generated JS bundle.
        // This is more similar to a search-and-replace than setting a variable.
        new webpack.DefinePlugin({
            __VERSION__: JSON.stringify(gitRevisionPlugin.version()),
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
