import js from '@eslint/js';
import ts from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import vueParser from 'vue-eslint-parser';
import vuePlugin from 'eslint-plugin-vue';
import importPlugin from 'eslint-plugin-import';
import yamlPlugin from 'eslint-plugin-yaml';
import prettier from 'eslint-config-prettier';
import accessibilityPlugin from 'eslint-plugin-vuejs-accessibility';

const config = [
  // Configuración base
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
    ],
  },

  // Configuración básica de ESLint
  js.configs.recommended,

  // TypeScript
  {
    files: ['**/*.ts', '**/*.vue'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: "./tsconfig.eslint.json",
        extraFileExtensions: ['.vue'],
      },
    },
    plugins: {
      '@typescript-eslint': ts,
    },
    rules: {
      ...ts.configs['eslint-recommended'].rules,
      ...ts.configs['recommended'].rules,
      '@typescript-eslint/no-unused-vars': 'warn',
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
      'vue/html-self-closing': ['error', { html: { void: 'always' } }],
      'vue/multi-word-component-names': 'warn',
    },
  },

  // Imports
  {
    plugins: {
      import: importPlugin,
    },
    settings: {
      'import/parsers': {
        '@typescript-eslint/parser': ['.ts', '.tsx', '.vue']
      },
      'import/resolver': {
        typescript: {
          project: './tsconfig.eslint.json',
          alwaysTryTypes: true
        },
        alias: {
          map: [['@', './src']],
          extensions: ['.js', '.ts', '.jsx', '.tsx', '.vue']
        }
      }
    },
    rules: {
      'import/no-unresolved': 'error',
      'import/extensions': ['error', 'ignorePackages', {
        js: 'never',
        ts: 'never',
        vue: 'always'
      }]
    }
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

  // Configuración global
  {
    languageOptions: {
      globals: {
        browser: true,
        node: true,
        es6: true,
      },
    },
    rules: {
      'require-jsdoc': 'off',
      'valid-jsdoc': 'off',
    },
  },

  // Prettier (debe ir último)
  prettier,
];

export default config;
