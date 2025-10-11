import js from '@eslint/js';
import ts from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import vueParser from 'vue-eslint-parser';
import vuePlugin from 'eslint-plugin-vue';
import importPlugin from 'eslint-plugin-import';
import yamlPlugin from 'eslint-plugin-yaml';
import prettier from 'eslint-config-prettier';
import accessibilityPlugin from 'eslint-plugin-vuejs-accessibility';
import jsdocPlugin from 'eslint-plugin-jsdoc';
import jsoncPlugin from 'eslint-plugin-jsonc';

const config = [
  // Base config
  {
    ignores: [
      '.husky/',
      '.vscode/',
      '.yarn/',
      'coverage/',
      'dist/',
      'public/',
      'public/assets/',
      'tsconfig.*.json',
      'index.html',
      'node_modules/',
      '*.min.js',
      'dist/**/*'
    ],
  },

  // Basic ESLint
  js.configs.recommended,

  // TypeScript
  {
    files: ['**/*.ts', '**/*.vue'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: './tsconfig.eslint.json',
        extraFileExtensions: ['.vue'],
      },
    },
    plugins: {
      '@typescript-eslint': ts,
    },
    rules: {
      ...ts.configs['eslint-recommended'].rules,
      ...ts.configs['recommended'].rules,
      '@typescript-eslint/no-unused-vars': ['warn', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/prefer-const': 'error',
      'new-cap': 'off',
      'no-invalid-this': 'off',
    },
  },

  // Vue.js
  {
    files: ['**/*.vue'],
    ...vuePlugin.configs['flat/strongly-recommended'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        sourceType: 'module',
        ecmaVersion: 'latest',
      },
    },
    plugins: {
      vue: vuePlugin,
      'vuejs-accessibility': accessibilityPlugin,
    },
    rules: {
      ...accessibilityPlugin.configs.recommended.rules,
      'vue/html-self-closing': ['error', {
        html: { void: 'always', normal: 'always', component: 'always' },
        svg: 'always'
      }],
      'vue/multi-word-component-names': 'warn',
      'vue/component-tags-order': ['error', {
        order: ['template', 'script', 'style']
      }],
      'vuejs-accessibility/label-has-for': 'off', // Compatible with Vuetify
    },
  },

  // Imports
  {
    files: ['**/*.ts', '**/*.js', '**/*.vue'],
    plugins: {
      import: importPlugin,
    },
    settings: {
      'import/parsers': {
        '@typescript-eslint/parser': ['.ts', '.tsx', '.vue'],
      },
      'import/resolver': {
        typescript: {
          project: './tsconfig.eslint.json',
          alwaysTryTypes: true,
        },
        alias: {
          map: [['@', './src']],
          extensions: ['.js', '.ts', '.jsx', '.tsx', '.vue'],
        },
      },
    },
    rules: {
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/no-absolute-path': 'error',
      'import/no-cycle': 'warn',
      'import/no-self-import': 'error',
      'import/extensions': [
        'error',
        'ignorePackages',
        {
          js: 'never',
          ts: 'never',
          vue: 'always',
        },
      ],
      'import/order': [
        'error',
        {
          groups: [
            'builtin',
            'external',
            'internal',
            'parent',
            'sibling',
            'index',
            'object',
            'type'
          ],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
    },
  },

  // JSDoc
  {
    files: ['**/*.ts', '**/*.js'],
    plugins: {
      jsdoc: jsdocPlugin,
    },
    rules: {
      ...jsdocPlugin.configs.recommended.rules,
      'jsdoc/require-param-description': 'warn',
      'jsdoc/require-returns-description': 'warn',
      'jsdoc/require-jsdoc': 'off',
      'jsdoc/tag-lines': 'off',
    },
  },

  // JSON
  {
    files: ['**/*.json', '**/*.jsonc'],
    plugins: {
      jsonc: jsoncPlugin,
    },
    rules: {
      ...jsoncPlugin.configs['recommended-with-jsonc'].rules,
    },
  },

  // YAML
  {
    files: ['**/*.yaml', '**/*.yml'],
    plugins: {
      yaml: yamlPlugin,
    },
    rules: {
      ...yamlPlugin.configs.recommended.rules,
    },
  },

  // Global config
  {
    files: ['**/*.ts', '**/*.js', '**/*.vue'],
    languageOptions: {
      globals: {
        // Globals para browser
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        console: 'readonly',
        // Globals for Node.js
        process: 'readonly',
        module: 'readonly',
        require: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        // Timers
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
      },
      ecmaVersion: 'latest',
    },
    env: {
      browser: true,
      node: true,
      es2022: true
    },
    rules: {
      'require-jsdoc': 'off',
      'valid-jsdoc': 'off',
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },

  // Prettier
  prettier,
];

export default config;