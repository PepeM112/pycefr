import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import prettier from 'eslint-config-prettier';
import vueParser from 'vue-eslint-parser';
import globals from 'globals';
import importPlugin from 'eslint-plugin-import';
import vuePrettier from '@vue/eslint-config-prettier';
import yamlPlugin from 'eslint-plugin-yaml';
import jsoncPlugin from 'eslint-plugin-jsonc';
import accessibility from 'eslint-plugin-vuejs-accessibility';
import { defineConfig } from 'eslint/config';

export default defineConfig([
  { ignores: ['dist/', 'node_modules/'] },

  // JS
  {
    ...js.configs.recommended,
    files: ['**/*.js', '**/*.mjs'],
    rules: {
      ...js.configs.recommended.rules,
      'require-jsdoc': 'off',
      'valid-jsdoc': 'off',
      'new-cap': 'off',
      'no-invalid-this': 'off',
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
  },

  // Vue
  ...vue.configs['flat/recommended'],

  // Imports
  {
    files: ['**/*.{js,ts,tsx,vue}'],
    plugins: { import: importPlugin },
    settings: {
      'import/parsers': {
        '@typescript-eslint/parser': ['.ts', '.tsx'],
        'vue-eslint-parser': ['.vue'],
      },
      'import/resolver': {
        typescript: {
          project: './tsconfig.eslint.json',
          alwaysTryTypes: true,
        },
        node: true,
      },
    },
    rules: {
      ...importPlugin.configs.recommended.rules,
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/no-cycle': 'warn',
      'import/no-self-import': 'error',
      'import/extensions': ['error', 'ignorePackages', { js: 'never', ts: 'never', vue: 'always' }],
      'import/order': [
        'warn',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'object', 'type'],
        },
      ],
    },
  },

  {
    files: ['**/*.vue'],
    rules: {
      'import/default': 'off',
    },
  },

  // TypeScript
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.eslint.json',
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals: globals.browser,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      'no-undef': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },

  // Vue
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        project: './tsconfig.eslint.json',
        extraFileExtensions: ['.vue'],
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals: globals.browser,
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      'vuejs-accessibility': accessibility,
    },
    rules: {
      // TS
      ...tsPlugin.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      'no-undef': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',

      // Vue

      'vuejs-accessibility/alt-text': 'error',
      'vuejs-accessibility/anchor-has-content': 'error',
      'vuejs-accessibility/mouse-events-have-key-events': 'error',
      'vuejs-accessibility/click-events-have-key-events': 'error',
      'vuejs-accessibility/label-has-for': 'off',

      // Vue Rules overrides
      'vue/html-self-closing': [
        'error',
        {
          html: { void: 'always', normal: 'always', component: 'always' },
          svg: 'always',
          math: 'always',
        },
      ],
      'vue/block-order': ['error', { order: ['template', 'script', 'style'] }],
      'vue/multi-word-component-names': 'warn',
    },
  },

  // YAML
  {
    files: ['**/*.yml', '**/*.yaml'],
    ...yamlPlugin.configs['flat/recommended'],
  },

  // JSON
  {
    files: ['**/*.json', '**/*.jsonc'],
    ...jsoncPlugin.configs['flat/recommended'],
  },

  vuePrettier,
  prettier,
]);
