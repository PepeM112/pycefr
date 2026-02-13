import { AnalysisStatus, ClassId } from '@/client';

type Enum = typeof AnalysisStatus | typeof ClassId;

interface EnumsLabelsItem<T extends Record<string | number, string | number> = any> {
  enum: T;
  labels: Record<Exclude<T[keyof T], 0>, string>;
}

function createEnumsLabelsItem<T extends Record<keyof T, string | number>>(
  item: EnumsLabelsItem<T>
): EnumsLabelsItem<T> {
  return item;
}

const enumsLabels: EnumsLabelsItem<Enum>[] = [
  createEnumsLabelsItem({
    enum: AnalysisStatus,
    labels: {
      [AnalysisStatus.IN_PROGRESS]: 'in_progress',
      [AnalysisStatus.COMPLETED]: 'completed',
      [AnalysisStatus.FAILED]: 'failed',
      [AnalysisStatus.DELETED]: 'deleted',
    },
  }),
  createEnumsLabelsItem({
    enum: ClassId,
    labels: {
      // List
      [ClassId.LIST_SIMPLE]: 'analysis_rules.list_simple',
      [ClassId.LIST_NESTED]: 'analysis_rules.list_nested',
      [ClassId.LIST_WITH_DICT]: 'analysis_rules.list_with_dict',
      [ClassId.LISTCOMP_SIMPLE]: 'analysis_rules.listcomp_simple',
      [ClassId.LISTCOMP_NESTED]: 'analysis_rules.listcomp_nested',
      [ClassId.LISTCOMP_WITH_IF]: 'analysis_rules.listcomp_with_if',
      // Dict
      [ClassId.DICT_SIMPLE]: 'analysis_rules.dict_simple',
      [ClassId.DICT_NESTED]: 'analysis_rules.dict_nested',
      [ClassId.DICT_WITH_LIST]: 'analysis_rules.dict_with_list',
      [ClassId.DICT_WITH_DICT_LIST]: 'analysis_rules.dict_with_dict_list',
      // DictComp
      [ClassId.DICTCOMP_SIMPLE]: 'analysis_rules.dictcomp_simple',
      [ClassId.DICTCOMP_WITH_IF]: 'analysis_rules.dictcomp_with_if',
      [ClassId.DICTCOMP_WITH_IF_ELSE]: 'analysis_rules.dictcomp_with_if_else',
      [ClassId.DICTCOMP_NESTED]: 'analysis_rules.dictcomp_nested',
      // Tuple
      [ClassId.TUPLE_SIMPLE]: 'analysis_rules.tuple_simple',
      [ClassId.TUPLE_NESTED]: 'analysis_rules.tuple_nested',
      // File
      [ClassId.FILE_OPEN]: 'analysis_rules.file_open',
      [ClassId.FILE_WRITE]: 'analysis_rules.file_write',
      [ClassId.FILE_WRITELINES]: 'analysis_rules.file_writelines',
      [ClassId.FILE_READ]: 'analysis_rules.file_read',
      [ClassId.FILE_READLINE]: 'analysis_rules.file_readline',
      // Print
      [ClassId.PRINT_SIMPLE]: 'analysis_rules.print_simple',
      // Assign
      [ClassId.ASSIGN_SIMPLE]: 'analysis_rules.assign_simple',
      [ClassId.ASSIGN_WITH_OPERATOR]: 'analysis_rules.assign_with_operator',
      [ClassId.ASSIGN_INCREMENTS]: 'analysis_rules.assign_increments',
      // If
      [ClassId.IF_SIMPLE]: 'analysis_rules.if_simple',
      [ClassId.IF_EXPRESSION]: 'analysis_rules.if_expression',
      [ClassId.IF_NAME_MAIN]: 'analysis_rules.if_name_main',
      // Loops
      [ClassId.LOOP_BREAK]: 'analysis_rules.loop_break',
      [ClassId.LOOP_CONTINUE]: 'analysis_rules.loop_continue',
      [ClassId.LOOP_PASS]: 'analysis_rules.loop_pass',
      [ClassId.LOOP_WHILE_SIMPLE]: 'analysis_rules.loop_while_simple',
      [ClassId.LOOP_WHILE_ELSE]: 'analysis_rules.loop_while_else',
      [ClassId.LOOP_FOR_SIMPLE]: 'analysis_rules.loop_for_simple',
      [ClassId.LOOP_FOR_NESTED]: 'analysis_rules.loop_for_nested',
      [ClassId.LOOP_FOR_TUPLE_NAME]: 'analysis_rules.loop_for_tuple_name',
      [ClassId.LOOP_FOR_LIST_ITERATE]: 'analysis_rules.loop_for_list_iterate',
      [ClassId.LOOP_FOR_TUPLE_ITERATE]: 'analysis_rules.loop_for_tuple_iterate',
      [ClassId.LOOP_RANGE]: 'analysis_rules.loop_range',
      [ClassId.LOOP_ZIP]: 'analysis_rules.loop_zip',
      [ClassId.LOOP_MAP]: 'analysis_rules.loop_map',
      [ClassId.LOOP_ENUMERATE]: 'analysis_rules.loop_enumerate',
      // Functions
      [ClassId.FUNCTIONDEF_SIMPLE]: 'analysis_rules.functiondef_simple',
      [ClassId.FUNCTIONDEF_ARGUM_DEFAULT]: 'analysis_rules.functiondef_argum_default',
      [ClassId.FUNCTIONDEF_ARGUM_STAR]: 'analysis_rules.functiondef_argum_star',
      [ClassId.FUNCTIONDEF_ARGUM_DBL_STAR]: 'analysis_rules.functiondef_argum_dbl_star',
      [ClassId.FUNCTIONDEF_ARGUM_KEYWORD_ONLY]: 'analysis_rules.functiondef_argum_keyword_only',
      [ClassId.FUNCTIONDEF_RECURSIVE]: 'analysis_rules.functiondef_recursive',
      // Return
      [ClassId.RETURN_SIMPLE]: 'analysis_rules.return_simple',
      // Lambda
      [ClassId.LAMBDA_SIMPLE]: 'analysis_rules.lambda_simple',
      // Generators
      [ClassId.GENERATORS_FUNCTION]: 'analysis_rules.generators_function',
      [ClassId.GENERATORS_EXPRESSION]: 'analysis_rules.generators_expression',
      // Imports
      [ClassId.IMPORT_SIMPLE]: 'analysis_rules.import_simple',
      [ClassId.IMPORT_FROM_SIMPLE]: 'analysis_rules.import_from_simple',
      [ClassId.IMPORT_FROM_RELATIVE]: 'analysis_rules.import_from_relative',
      [ClassId.IMPORT_FROM_STAR]: 'analysis_rules.import_from_star',
      [ClassId.IMPORT_AS_EXTENSION]: 'analysis_rules.import_as_extension',
      // Modules
      [ClassId.MODULES_STRUCT]: 'analysis_rules.modules_struct',
      [ClassId.MODULES_PICKLE]: 'analysis_rules.modules_pickle',
      [ClassId.MODULES_SHELVE]: 'analysis_rules.modules_shelve',
      [ClassId.MODULES_DBM]: 'analysis_rules.modules_dbm',
      [ClassId.MODULES_RE]: 'analysis_rules.modules_re',
      [ClassId.MODULES_IMPORTLIB]: 'analysis_rules.modules_importlib',
      // Class
      [ClassId.CLASS_SIMPLE]: 'analysis_rules.class_simple',
      [ClassId.CLASS_INHERITED]: 'analysis_rules.class_inherited',
      [ClassId.CLASS_INIT]: 'analysis_rules.class_init',
      [ClassId.CLASS_DESCRIPTORS]: 'analysis_rules.class_descriptors',
      [ClassId.CLASS_PROPERTIES]: 'analysis_rules.class_properties',
      [ClassId.CLASS_PRIVATE]: 'analysis_rules.class_private',
      // Static/Class methods
      [ClassId.STATIC_CLASSMETHOD]: 'analysis_rules.static_classmethod',
      [ClassId.STATIC_STATICMETHOD]: 'analysis_rules.static_staticmethod',
      // Decorators
      [ClassId.DECORATORS_FUNCTION]: 'analysis_rules.decorators_function',
      [ClassId.DECORATORS_CLASS]: 'analysis_rules.decorators_class',
      // Metaclasses
      [ClassId.METACLASS_NEW]: 'analysis_rules.metaclass_new',
      [ClassId.METACLASS_METACLASS]: 'analysis_rules.metaclass_metaclass',
      [ClassId.METACLASS_ATTR_METACLASS]: 'analysis_rules.metaclass_attr_metaclass',
      // Super
      [ClassId.SUPERFUNCTION_SIMPLE]: 'analysis_rules.superfunction_simple',
      // Slots
      [ClassId.SLOTS_ATTR]: 'analysis_rules.slots_attr',
      // Attributes
      [ClassId.ATTRIBUTES_SIMPLE]: 'analysis_rules.attributes_simple',
      [ClassId.ATTRIBUTES_CLASS_REF]: 'analysis_rules.attributes_class_ref',
      [ClassId.ATTRIBUTES_DICT_REF]: 'analysis_rules.attributes_dict_ref',
      // Exceptions
      [ClassId.EXCEPTION_TRY_EXCEPT]: 'analysis_rules.exception_try_except',
      [ClassId.EXCEPTION_TRY_ELSE_EXCEPT]: 'analysis_rules.exception_try_else_except',
      [ClassId.EXCEPTION_TRY_TRY]: 'analysis_rules.exception_try_try',
      [ClassId.EXCEPTION_TRY_FINALLY]: 'analysis_rules.exception_try_finally',
      [ClassId.EXCEPTION_TRY_EXCEPT_FINALLY]: 'analysis_rules.exception_try_except_finally',
      [ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY]: 'analysis_rules.exception_try_except_else_finally',
      [ClassId.EXCEPTION_RAISE]: 'analysis_rules.exception_raise',
      [ClassId.EXCEPTION_ASSERT]: 'analysis_rules.exception_assert',
      // With
      [ClassId.WITH_SIMPLE]: 'analysis_rules.with_simple',
    },
  }),
];

export { enumsLabels };
