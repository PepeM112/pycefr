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
    },
  }),
  createEnumsLabelsItem({
    enum: ClassId,
    labels: {
      // List
      [ClassId._1]: 'analysis_rules.list_simple',
      [ClassId._2]: 'analysis_rules.list_nested',
      [ClassId._3]: 'analysis_rules.list_with_dict',
      [ClassId._4]: 'analysis_rules.listcomp_simple',
      [ClassId._5]: 'analysis_rules.listcomp_nested',
      [ClassId._6]: 'analysis_rules.listcomp_with_if',
      // Dict
      [ClassId._7]: 'analysis_rules.dict_simple',
      [ClassId._8]: 'analysis_rules.dict_nested',
      [ClassId._9]: 'analysis_rules.dict_with_list',
      [ClassId._10]: 'analysis_rules.dict_with_dict_list',
      // DictComp
      [ClassId._11]: 'analysis_rules.dictcomp_simple',
      [ClassId._12]: 'analysis_rules.dictcomp_with_if',
      [ClassId._13]: 'analysis_rules.dictcomp_with_if_else',
      [ClassId._14]: 'analysis_rules.dictcomp_nested',
      // Tuple
      [ClassId._15]: 'analysis_rules.tuple_simple',
      [ClassId._16]: 'analysis_rules.tuple_nested',
      // File
      [ClassId._17]: 'analysis_rules.file_open',
      [ClassId._18]: 'analysis_rules.file_write',
      [ClassId._19]: 'analysis_rules.file_writelines',
      [ClassId._20]: 'analysis_rules.file_read',
      [ClassId._21]: 'analysis_rules.file_readline',
      // Print
      [ClassId._22]: 'analysis_rules.print_simple',
      // Assign
      [ClassId._23]: 'analysis_rules.assign_simple',
      [ClassId._24]: 'analysis_rules.assign_with_operator',
      [ClassId._25]: 'analysis_rules.assign_increments',
      // If
      [ClassId._26]: 'analysis_rules.if_simple',
      [ClassId._27]: 'analysis_rules.if_expression',
      [ClassId._28]: 'analysis_rules.if_name_main',
      // Loops
      [ClassId._29]: 'analysis_rules.loop_break',
      [ClassId._30]: 'analysis_rules.loop_continue',
      [ClassId._31]: 'analysis_rules.loop_pass',
      [ClassId._32]: 'analysis_rules.loop_while_simple',
      [ClassId._33]: 'analysis_rules.loop_while_else',
      [ClassId._34]: 'analysis_rules.loop_for_simple',
      [ClassId._35]: 'analysis_rules.loop_for_nested',
      [ClassId._36]: 'analysis_rules.loop_for_tuple_name',
      [ClassId._37]: 'analysis_rules.loop_for_list_iterate',
      [ClassId._38]: 'analysis_rules.loop_for_tuple_iterate',
      [ClassId._39]: 'analysis_rules.loop_range',
      [ClassId._40]: 'analysis_rules.loop_zip',
      [ClassId._41]: 'analysis_rules.loop_map',
      [ClassId._42]: 'analysis_rules.loop_enumerate',
      // Functions
      [ClassId._43]: 'analysis_rules.functiondef_simple',
      [ClassId._44]: 'analysis_rules.functiondef_argum_default',
      [ClassId._45]: 'analysis_rules.functiondef_argum_star',
      [ClassId._46]: 'analysis_rules.functiondef_argum_dbl_star',
      [ClassId._47]: 'analysis_rules.functiondef_argum_keyword_only',
      [ClassId._48]: 'analysis_rules.functiondef_recursive',
      // Return
      [ClassId._49]: 'analysis_rules.return_simple',
      // Lambda
      [ClassId._50]: 'analysis_rules.lambda_simple',
      // Generators
      [ClassId._51]: 'analysis_rules.generators_function',
      [ClassId._52]: 'analysis_rules.generators_expression',
      // Imports
      [ClassId._53]: 'analysis_rules.import_simple',
      [ClassId._54]: 'analysis_rules.import_from_simple',
      [ClassId._55]: 'analysis_rules.import_from_relative',
      [ClassId._56]: 'analysis_rules.import_from_star',
      [ClassId._57]: 'analysis_rules.import_as_extension',
      // Modules
      [ClassId._58]: 'analysis_rules.modules_struct',
      [ClassId._59]: 'analysis_rules.modules_pickle',
      [ClassId._60]: 'analysis_rules.modules_shelve',
      [ClassId._61]: 'analysis_rules.modules_dbm',
      [ClassId._62]: 'analysis_rules.modules_re',
      [ClassId._63]: 'analysis_rules.modules_importlib',
      // Class
      [ClassId._64]: 'analysis_rules.class_simple',
      [ClassId._65]: 'analysis_rules.class_inherited',
      [ClassId._66]: 'analysis_rules.class_init',
      [ClassId._67]: 'analysis_rules.class_descriptors',
      [ClassId._68]: 'analysis_rules.class_properties',
      [ClassId._69]: 'analysis_rules.class_private',
      // Static/Class methods
      [ClassId._70]: 'analysis_rules.static_classmethod',
      [ClassId._71]: 'analysis_rules.static_staticmethod',
      // Decorators
      [ClassId._72]: 'analysis_rules.decorators_function',
      [ClassId._73]: 'analysis_rules.decorators_class',
      // Metaclasses
      [ClassId._74]: 'analysis_rules.metaclass_new',
      [ClassId._75]: 'analysis_rules.metaclass_metaclass',
      [ClassId._76]: 'analysis_rules.metaclass_attr_metaclass',
      // Super
      [ClassId._77]: 'analysis_rules.superfunction_simple',
      // Slots
      [ClassId._78]: 'analysis_rules.slots_attr',
      // Attributes
      [ClassId._79]: 'analysis_rules.attributes_simple',
      [ClassId._80]: 'analysis_rules.attributes_class_ref',
      [ClassId._81]: 'analysis_rules.attributes_dict_ref',
      // Exceptions
      [ClassId._82]: 'analysis_rules.exception_try_except',
      [ClassId._83]: 'analysis_rules.exception_try_else_except',
      [ClassId._84]: 'analysis_rules.exception_try_try',
      [ClassId._85]: 'analysis_rules.exception_try_finally',
      [ClassId._86]: 'analysis_rules.exception_try_except_finally',
      [ClassId._87]: 'analysis_rules.exception_try_except_else_finally',
      [ClassId._88]: 'analysis_rules.exception_raise',
      [ClassId._89]: 'analysis_rules.exception_assert',
      // With
      [ClassId._90]: 'analysis_rules.with_simple',
    },
  }),
];

export { enumsLabels };
