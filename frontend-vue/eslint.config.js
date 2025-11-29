// eslint.config.js
import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import prettier from 'eslint-config-prettier';
import vueParser from 'vue-eslint-parser';
import globals from 'globals';
import importPlugin from 'eslint-plugin-import';
export default [
  { ignores: ['dist/', 'node_modules/'] },

  js.configs.recommended,

  // TypeScript + Vue
  {
    files: ['**/*.ts', '**/*.vue'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.eslint.json', // ← AQUÍ
        extraFileExtensions: ['.vue'],
      },
      globals: globals.browser,
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', { varsIgnorePattern: '^_' }],
    },
  },

  // Vue base
  ...vue.configs['flat/recommended'],

  // Vue específico
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        extraFileExtensions: ['.vue'],
      },
    },
    rules: {
      'vue/html-self-closing': [
        'error',
        {
          html: {
            void: 'always',
            normal: 'always',
            component: 'always',
          },
          svg: 'always',
          math: 'always',
        },
      ],
      'vue/block-order': ['error', { order: ['template', 'script', 'style'] }],
      'vue/multi-word-component-names': 'warn',
      'vuejs-accessibility/label-has-for': 'off',
    },
  },
  importPlugin.flatConfigs.recommended,
  {
    files: ['**/*.ts', '**/*.js', '**/*.vue'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    extends: [
      "eslint:recommended",
      "plugin:import/recommended",
      "plugin:import/typescript",
    ],
    settings: {
      'import/parsers': {
        [tsParser]: ['.ts', '.tsx'],
        [vueParser]: ['.vue'],
      },
      'import/resolver': {
        typescript: {
          project: './tsconfig.eslint.json',
          alwaysTryTypes: true,
        },
      },
    },
    rules: {
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/no-cycle': 'warn',
      'import/no-self-import': 'error',
      'import/extensions': ['error', 'ignorePackages', { js: 'never', ts: 'never', vue: 'always' }],
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'object', 'type'],
          'newlines-between': 'always',
        },
      ],
    },
  },

  prettier,
];

// Funciona todo menos lo de los imports, creo. Cuidado con qué se toca