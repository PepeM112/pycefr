import path from 'node:path';
import { fileURLToPath } from 'node:url';
import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import prettier from 'eslint-config-prettier';
import vueParser from 'vue-eslint-parser';
import globals from 'globals';
import importPlugin from 'eslint-plugin-import';
import vuePrettier from '@vue/eslint-config-prettier';
import yamlPlugin from 'eslint-plugin-yaml';
import jsoncPlugin from 'eslint-plugin-jsonc';
import accessibility from 'eslint-plugin-vuejs-accessibility';
import { defineConfig } from 'eslint/config';
import { configs, parser, plugin } from 'typescript-eslint';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig([
  { ignores: ['dist/', 'node_modules/'] },

  js.configs.recommended,
  ...configs.recommendedTypeChecked,
  ...vue.configs['flat/recommended'],
  // JS
  {
    files: ['**/*.js', '**/*.mjs'],
    rules: {
      'require-jsdoc': 'off',
      'valid-jsdoc': 'off',
      'new-cap': 'off',
      'no-invalid-this': 'off',
    },
  },
  {
    files: ['**/*.ts', '**/*.tsx', '**/*.vue', '**/*.js', '**/*.mjs'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: parser,
        project: ['./tsconfig.eslint.json'],
        tsconfigRootDir: __dirname,
        extraFileExtensions: ['.vue'],
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    plugins: {
      '@typescript-eslint': plugin,
      import: importPlugin,
      'vuejs-accessibility': accessibility,
    },
    settings: {
      'import/resolver': {
        typescript: { project: './tsconfig.eslint.json', alwaysTryTypes: true },
        node: true,
      },
    },
    rules: {
      ...importPlugin.configs.recommended.rules,
      ...accessibility.configs.recommended.rules,
      // TS
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-unused-vars': 'off',
      'no-undef': 'off',

      // Import
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/no-cycle': 'off',
      'import/no-self-import': 'error',
      'import/extensions': ['error', 'ignorePackages', { js: 'never', ts: 'never', vue: 'always' }],
      'import/order': [
        'warn',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'object', 'type'],
        },
      ],
      // Vue
      'vue/html-self-closing': ['error', { html: { void: 'always', normal: 'always', component: 'always' } }],
      'vue/block-order': ['error', { order: ['template', 'script', 'style'] }],
      'vue/multi-word-component-names': 'off',
      'vue/no-required-prop-with-default': 'off',
      'vue/attributes-order': [
        'error',
        {
          order: [
            'DEFINITION', // ej: is, v-is
            'CONDITIONALS', // ej: v-if, v-else-if, v-else, v-show, v-cloak
            'LIST_RENDERING', // ej: v-for
            'RENDER_MODIFIERS', // ej: v-once, v-pre
            'GLOBAL', // ej: id
            'UNIQUE', // ej: ref, key
            'SLOT', // ej: v-slot, slot
            'TWO_WAY_BINDING', // ej: v-model
            'OTHER_DIRECTIVES', // ej: v-custom-directive
            'OTHER_ATTR', // ej: custom-prop="foo", class, style
            'CONTENT', // ej: v-text, v-html
            'EVENTS', // ej: @click, v-on="foo"
          ],
          alphabetical: false,
        },
      ],
    },
  },

  {
    files: ['**/*.vue'],
    rules: {
      'import/default': 'off', // Disabled to prevent false positives when importing .vue files
    },
  },

  {
    files: ['vite.config.ts'],
    rules: {
      '@typescript-eslint/no-unsafe-call': 'off', // vite-plugin-vuetify types unresolvable by eslint parser
    },
  },

  // YAML
  { files: ['**/*.yml', '**/*.yaml'], ...yamlPlugin.configs['flat/recommended'] },

  // JSON
  { files: ['**/*.json', '**/*.jsonc'], ...jsoncPlugin.configs['flat/recommended'] },

  vuePrettier,
  prettier,
]);
