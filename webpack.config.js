const path = require("path");
const StyleLintPlugin = require("stylelint-webpack-plugin");
const ESLintPlugin = require("eslint-webpack-plugin");
const webpack = require("webpack");

module.exports = {
  context: __dirname,
  mode: process.env.NODE_ENV,
  entry: {
    // This is included on every page.
    main: "./assets/entrypoint.js",

    "fake-catalogue": {
      import: ["./assets/fake-catalogue/index.js"],
      dependOn: ["main"],
    },

    "fake-projects": {
      import: ["./assets/fake-projects/index.js"],
      dependOn: ["main"],
    },
  },
  output: {
    path: path.resolve(__dirname, "eodhp_web_presence/staticfiles/bundles"),
    publicPath: "/static/bundles/",
    filename: "[name].js",
  },
  devServer: {
    compress: true,
    port: 3000,
    hot: true,
    host: "0.0.0.0",
    headers: {"Access-Control-Allow-Origin": "*"},
    proxy: [
      {
        context: ["/"],
        target: "http://localhost:8000",
      },
    ],
    static: [],
    watchFiles: ["assets/**/*"],
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new StyleLintPlugin({
      failOnError: false,
      configFile: ".stylelintrc",
      files: ["**/*.sass"],
      context: "js-src",
      quiet: false,
      emitError: true,
      cache: true,
      customSyntax: "postcss-sass",
    }),
    new ESLintPlugin({
      formatter: require("eslint-friendly-formatter"),
      cache: true,
      emitError: true,
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(scss|css)$/,
        use: ["style-loader", "css-loader", "sass-loader"],
      },
      {
        test: /\.(?:js|mjs|cjs)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: [["@babel/preset-env", {targets: "defaults"}]],
          },
        },
      },
    ],
  },
};

// This adds a __VERSION__ variable (more like a search-and-replace than a variable)
// so that we can put the Git revision in the HTML in version.js.
if (process.env.GIT_REF_NAME) {
  module.exports.plugins.push(
    new webpack.DefinePlugin({
      __VERSION__: JSON.stringify(
        process.env.GIT_REF_NAME + "-" + process.env.GIT_SHA
      ),
    })
  );
}
