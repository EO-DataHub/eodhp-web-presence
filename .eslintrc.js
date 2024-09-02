module.exports = {
  root: true,
  extends: ['@tpzdsp/eslint-config-dsp'],
  ignorePatterns: ['dist', '.eslintrc.js'],
  rules: {
    'import/no-unassigned-import': ['error', { allow: ['**/*.scss', '**/*.css'] }],
  },
};
