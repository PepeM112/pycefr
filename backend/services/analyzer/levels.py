import ast
from typing import Dict

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Level


def get_class_from_ast_node(node: ast.AST) -> ClassId:
    if isinstance(node, ast.List):
        return get_level_list(node)
    if isinstance(node, ast.ListComp):
        return get_level_list_comp(node)
    if isinstance(node, ast.Dict):
        return get_level_dict(node)
    if isinstance(node, ast.DictComp):
        return get_level_dict_comp(node)
    if isinstance(node, ast.Tuple):
        return get_level_tuple(node)
    if isinstance(node, ast.Call):
        return get_level_call(node)
    if isinstance(node, (ast.Assign, ast.AugAssign)):
        return get_level_assign(node)
    if isinstance(node, ast.If):
        return get_level_if(node)
    if isinstance(node, ast.IfExp):
        return ClassId.IF_EXPRESSION
    if isinstance(node, ast.For):
        return get_level_for(node)
    if isinstance(node, ast.While):
        return get_level_while(node)
    if isinstance(node, ast.Break):
        return ClassId.LOOP_BREAK
    if isinstance(node, ast.Continue):
        return ClassId.LOOP_CONTINUE
    if isinstance(node, ast.Pass):
        return ClassId.LOOP_PASS
    if isinstance(node, ast.FunctionDef):
        return get_level_function(node)
    if isinstance(node, ast.ClassDef):
        return get_level_class(node)
    if isinstance(node, ast.Return):
        return ClassId.RETURN_SIMPLE
    if isinstance(node, ast.Lambda):
        return ClassId.LAMBDA_SIMPLE
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return get_level_import(node)
    if isinstance(node, ast.Try):
        return get_level_try(node)
    if isinstance(node, ast.Raise):
        return ClassId.EXCEPTION_RAISE
    if isinstance(node, ast.Assert):
        return ClassId.EXCEPTION_ASSERT
    if isinstance(node, ast.With):
        return ClassId.WITH_SIMPLE
    return ClassId.UNKNOWN


def get_level_list(node: ast.List) -> ClassId:
    has_nested_list = any(isinstance(e, ast.List) for e in node.elts)
    if has_nested_list:
        return ClassId.LIST_NESTED
    has_dict = any(isinstance(e, ast.Dict) for e in node.elts)
    if has_dict:
        return ClassId.LIST_WITH_DICT
    return ClassId.LIST_SIMPLE


def get_level_list_comp(node: ast.ListComp) -> ClassId:
    if len(node.generators) > 1:
        return ClassId.LISTCOMP_NESTED
    if any(gen.ifs for gen in node.generators):
        return ClassId.LISTCOMP_WITH_IF
    return ClassId.LISTCOMP_SIMPLE


def get_level_dict(node: ast.Dict) -> ClassId:
    has_dict_inside = any(isinstance(v, ast.Dict) for v in node.values)
    has_list_inside = any(isinstance(v, ast.List) for v in node.values)
    if has_dict_inside:
        for v in node.values:
            if isinstance(v, ast.Dict) and any(isinstance(inner_v, ast.List) for inner_v in v.values):
                return ClassId.DICT_WITH_DICT_LIST
        return ClassId.DICT_NESTED
    if has_list_inside:
        return ClassId.DICT_WITH_LIST
    return ClassId.DICT_SIMPLE


def get_level_dict_comp(node: ast.DictComp) -> ClassId:
    if isinstance(node.value, ast.DictComp):
        return ClassId.DICTCOMP_NESTED
    if isinstance(node.value, ast.IfExp):
        return ClassId.DICTCOMP_WITH_IF_ELSE
    if any(gen.ifs for gen in node.generators):
        return ClassId.DICTCOMP_WITH_IF
    return ClassId.DICTCOMP_SIMPLE


def get_level_tuple(node: ast.Tuple) -> ClassId:
    has_nested_tuple = any(isinstance(e, ast.Tuple) for e in node.elts)
    if has_nested_tuple:
        return ClassId.TUPLE_NESTED
    return ClassId.TUPLE_SIMPLE


def get_level_call(node: ast.Call) -> ClassId:
    if isinstance(node.func, ast.Name):
        func_id = node.func.id
        mapper = {
            "print": ClassId.PRINT_SIMPLE,
            "open": ClassId.FILE_OPEN,
            "range": ClassId.LOOP_RANGE,
            "zip": ClassId.LOOP_ZIP,
            "map": ClassId.LOOP_MAP,
            "enumerate": ClassId.LOOP_ENUMERATE,
            "super": ClassId.SUPERFUNCTION_SIMPLE,
        }
        return mapper.get(func_id, ClassId.UNKNOWN)

    if isinstance(node.func, ast.Attribute):
        attr_name = node.func.attr
        mapper = {
            "write": ClassId.FILE_WRITE,
            "read": ClassId.FILE_READ,
            "readline": ClassId.FILE_READLINE,
            "writelines": ClassId.FILE_WRITELINES,
        }
        return mapper.get(attr_name, ClassId.UNKNOWN)

    return ClassId.UNKNOWN


def get_level_assign(node: ast.AST) -> ClassId:
    if isinstance(node, ast.AugAssign):
        return ClassId.ASSIGN_INCREMENTS
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.BinOp):
        return ClassId.ASSIGN_WITH_OPERATOR
    return ClassId.ASSIGN_SIMPLE


def get_level_if(node: ast.If) -> ClassId:
    if (
        isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and isinstance(node.test.ops[0], ast.Eq)
        and isinstance(node.test.comparators[0], ast.Constant)
        and node.test.comparators[0].value == "__main__"
    ):
        return ClassId.IF_NAME_MAIN
    return ClassId.IF_SIMPLE


def get_level_for(node: ast.For) -> ClassId:
    has_nested_for = any(isinstance(e, ast.For) for e in node.body)
    if has_nested_for:
        return ClassId.LOOP_FOR_NESTED
    if isinstance(node.target, ast.Tuple):
        return ClassId.LOOP_FOR_TUPLE_NAME
    if isinstance(node.iter, ast.List):
        return ClassId.LOOP_FOR_LIST_ITERATE
    if isinstance(node.iter, ast.Tuple):
        return ClassId.LOOP_FOR_TUPLE_ITERATE
    return ClassId.LOOP_FOR_SIMPLE


def get_level_while(node: ast.While) -> ClassId:
    if node.orelse:
        return ClassId.LOOP_WHILE_ELSE
    return ClassId.LOOP_WHILE_SIMPLE


def get_level_function(node: ast.FunctionDef) -> ClassId:
    # Decorators
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
            return ClassId.STATIC_CLASSMETHOD
        if isinstance(decorator, ast.Name) and decorator.id == "classmethod":
            return ClassId.STATIC_STATICMETHOD

    # Recursion
    for subnode in ast.walk(node):
        if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name) and subnode.func.id == node.name:
            return ClassId.FUNCTIONDEF_RECURSIVE

    # Generators (contains yield)
    for subnode in node.body:
        for depth_node in ast.walk(subnode):
            if isinstance(depth_node, (ast.Yield, ast.YieldFrom)):
                return ClassId.GENERATORS_FUNCTION

    # Arguments
    if node.args.kwonlyargs:
        return ClassId.FUNCTIONDEF_ARGUM_KEYWORD_ONLY
    if node.args.kwarg:
        return ClassId.FUNCTIONDEF_ARGUM_DBL_STAR
    if node.args.vararg:
        return ClassId.FUNCTIONDEF_ARGUM_STAR
    if node.args.defaults:
        return ClassId.FUNCTIONDEF_ARGUM_DEFAULT

    return ClassId.FUNCTIONDEF_SIMPLE


def get_level_class(node: ast.ClassDef) -> ClassId:
    if node.bases:
        return ClassId.CLASS_INHERITED
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            # Constructor
            if item.name == "__init__":
                return ClassId.CLASS_INIT
            # Has private attributes/methods
            if item.name.startswith("__") and not item.name.endswith("__"):
                return ClassId.CLASS_PRIVATE
            # Descriptors
            if item.name in ["__get__", "__set__", "__delete__"]:
                return ClassId.CLASS_DESCRIPTORS

        # Properties (e.g., @property)
        for decorator in getattr(item, "decorator_list", []):
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return ClassId.CLASS_PROPERTIES

    return ClassId.CLASS_SIMPLE


def get_level_import(node: ast.AST) -> ClassId:
    modules = {
        "re": ClassId.MODULES_RE,
        "pickle": ClassId.MODULES_PICKLE,
        "struct": ClassId.MODULES_STRUCT,
        "importlib": ClassId.MODULES_IMPORTLIB,
    }
    if isinstance(node, ast.Import):
        if any(alias.asname for alias in node.names):
            return ClassId.IMPORT_AS_EXTENSION
        for alias in node.names:
            if alias.name in modules:
                return modules[alias.name]
        return ClassId.IMPORT_SIMPLE

    if isinstance(node, ast.ImportFrom):
        if node.level > 0:
            return ClassId.IMPORT_FROM_RELATIVE
        if any(alias.name == "*" for alias in node.names):
            return ClassId.IMPORT_FROM_STAR
        if node.module in modules:
            return modules[node.module]
        return ClassId.IMPORT_FROM_SIMPLE

    return ClassId.UNKNOWN


def get_level_try(node: ast.Try) -> ClassId:
    if node.finalbody:
        return ClassId.EXCEPTION_TRY_EXCEPT_FINALLY
    if node.orelse:
        return ClassId.EXCEPTION_TRY_ELSE_EXCEPT
    if any(isinstance(n, ast.Try) for n in node.body):
        return ClassId.EXCEPTION_TRY_TRY
    return ClassId.EXCEPTION_TRY_EXCEPT


def get_default_class_level(class_id: ClassId) -> int:
    """
    Returns the default CEFR level associated with a given ClassId based on a predefined mapping.
    """
    default_levels: Dict[ClassId, Level] = {
        ClassId.LIST_SIMPLE: Level.A1,
        ClassId.LIST_NESTED: Level.A2,
        ClassId.LIST_WITH_DICT: Level.B1,
        ClassId.LISTCOMP_SIMPLE: Level.A2,
        ClassId.LISTCOMP_NESTED: Level.B1,
        ClassId.LISTCOMP_WITH_IF: Level.B1,
        ClassId.DICT_SIMPLE: Level.A2,
        ClassId.DICT_NESTED: Level.B1,
        ClassId.DICT_WITH_LIST: Level.B1,
        ClassId.DICT_WITH_DICT_LIST: Level.B2,
        ClassId.DICTCOMP_SIMPLE: Level.B1,
        ClassId.DICTCOMP_WITH_IF: Level.B1,
        ClassId.DICTCOMP_WITH_IF_ELSE: Level.B1,
        ClassId.DICTCOMP_NESTED: Level.B2,
        ClassId.TUPLE_SIMPLE: Level.A1,
        ClassId.TUPLE_NESTED: Level.A2,
        ClassId.FILE_OPEN: Level.A2,
        ClassId.FILE_WRITE: Level.A2,
        ClassId.FILE_WRITELINES: Level.B1,
        ClassId.FILE_READ: Level.A2,
        ClassId.FILE_READLINE: Level.A2,
        ClassId.PRINT_SIMPLE: Level.A1,
        ClassId.ASSIGN_SIMPLE: Level.A1,
        ClassId.ASSIGN_WITH_OPERATOR: Level.A1,
        ClassId.ASSIGN_INCREMENTS: Level.A1,
        ClassId.IF_SIMPLE: Level.A1,
        ClassId.IF_EXPRESSION: Level.A2,
        ClassId.IF_NAME_MAIN: Level.A2,
        ClassId.LOOP_BREAK: Level.A2,
        ClassId.LOOP_CONTINUE: Level.A2,
        ClassId.LOOP_PASS: Level.A1,
        ClassId.LOOP_WHILE_SIMPLE: Level.A2,
        ClassId.LOOP_WHILE_ELSE: Level.B1,
        ClassId.LOOP_FOR_SIMPLE: Level.A1,
        ClassId.LOOP_FOR_NESTED: Level.A2,
        ClassId.LOOP_FOR_TUPLE_NAME: Level.A2,
        ClassId.LOOP_FOR_LIST_ITERATE: Level.A1,
        ClassId.LOOP_FOR_TUPLE_ITERATE: Level.A1,
        ClassId.LOOP_RANGE: Level.A1,
        ClassId.LOOP_ZIP: Level.B1,
        ClassId.LOOP_MAP: Level.B1,
        ClassId.LOOP_ENUMERATE: Level.A2,
        ClassId.FUNCTIONDEF_SIMPLE: Level.A2,
        ClassId.FUNCTIONDEF_ARGUM_DEFAULT: Level.B1,
        ClassId.FUNCTIONDEF_ARGUM_STAR: Level.B1,
        ClassId.FUNCTIONDEF_ARGUM_DBL_STAR: Level.B1,
        ClassId.FUNCTIONDEF_ARGUM_KEYWORD_ONLY: Level.B2,
        ClassId.FUNCTIONDEF_RECURSIVE: Level.B2,
        ClassId.RETURN_SIMPLE: Level.A2,
        ClassId.LAMBDA_SIMPLE: Level.B1,
        ClassId.GENERATORS_FUNCTION: Level.B2,
        ClassId.GENERATORS_EXPRESSION: Level.B2,
        ClassId.IMPORT_SIMPLE: Level.A1,
        ClassId.IMPORT_FROM_SIMPLE: Level.A1,
        ClassId.IMPORT_FROM_RELATIVE: Level.B1,
        ClassId.IMPORT_FROM_STAR: Level.A2,
        ClassId.IMPORT_AS_EXTENSION: Level.A1,
        ClassId.MODULES_STRUCT: Level.B2,
        ClassId.MODULES_PICKLE: Level.B2,
        ClassId.MODULES_SHELVE: Level.B2,
        ClassId.MODULES_DBM: Level.B2,
        ClassId.MODULES_RE: Level.B1,
        ClassId.MODULES_IMPORTLIB: Level.C1,
        ClassId.CLASS_SIMPLE: Level.B1,
        ClassId.CLASS_INHERITED: Level.B2,
        ClassId.CLASS_INIT: Level.B1,
        ClassId.CLASS_DESCRIPTORS: Level.C1,
        ClassId.CLASS_PROPERTIES: Level.B2,
        ClassId.CLASS_PRIVATE: Level.B2,
        ClassId.STATIC_CLASSMETHOD: Level.B2,
        ClassId.STATIC_STATICMETHOD: Level.B2,
        ClassId.DECORATORS_FUNCTION: Level.B2,
        ClassId.DECORATORS_CLASS: Level.C1,
        ClassId.METACLASS_NEW: Level.C2,
        ClassId.METACLASS_METACLASS: Level.C2,
        ClassId.METACLASS_ATTR_METACLASS: Level.C2,
        ClassId.SUPERFUNCTION_SIMPLE: Level.B2,
        ClassId.SLOTS_ATTR: Level.C1,
        ClassId.ATTRIBUTES_SIMPLE: Level.A2,
        ClassId.ATTRIBUTES_CLASS_REF: Level.C1,
        ClassId.ATTRIBUTES_DICT_REF: Level.C1,
        ClassId.EXCEPTION_TRY_EXCEPT: Level.A2,
        ClassId.EXCEPTION_TRY_ELSE_EXCEPT: Level.B1,
        ClassId.EXCEPTION_TRY_TRY: Level.B1,
        ClassId.EXCEPTION_TRY_FINALLY: Level.B1,
        ClassId.EXCEPTION_TRY_EXCEPT_FINALLY: Level.B1,
        ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY: Level.B2,
        ClassId.EXCEPTION_RAISE: Level.B1,
        ClassId.EXCEPTION_ASSERT: Level.B1,
        ClassId.WITH_SIMPLE: Level.B1,
    }

    return default_levels.get(class_id, Level.UNKNOWN)
