import ast
from typing import Type, TypeVar

import pytest

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Level
from backend.services.analyzer.levels import (
    get_class_from_ast_node,
    get_default_class_level,
    get_level_assign,
    get_level_call,
    get_level_class,
    get_level_dict,
    get_level_dict_comp,
    get_level_for,
    get_level_function,
    get_level_if,
    get_level_import,
    get_level_list,
    get_level_list_comp,
    get_level_try,
    get_level_tuple,
    get_level_while,
)

T = TypeVar("T", bound=ast.AST)


def parse_first(code: str, node_type: Type[T]) -> T:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, node_type):
            return node
    raise ValueError(f"No {node_type.__name__} found in: {code}")


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------


class TestGetLevelList:
    def test_simple(self) -> None:
        node = parse_first("[1, 2, 3]", ast.List)
        assert get_level_list(node) == [ClassId.LIST_SIMPLE]

    def test_nested(self) -> None:
        node = parse_first("[[1, 2], [3, 4]]", ast.List)
        assert get_level_list(node) == [ClassId.LIST_NESTED]

    def test_with_dict(self) -> None:
        node = parse_first("[{'a': 1}]", ast.List)
        assert get_level_list(node) == [ClassId.LIST_WITH_DICT]

    def test_nested_takes_precedence_over_dict(self) -> None:
        node = parse_first("[[1], {'a': 1}]", ast.List)
        assert get_level_list(node) == [ClassId.LIST_NESTED]


# ---------------------------------------------------------------------------
# List comprehensions
# ---------------------------------------------------------------------------


class TestGetLevelListComp:
    def test_simple(self) -> None:
        node = parse_first("[x for x in items]", ast.ListComp)
        assert get_level_list_comp(node) == [ClassId.LISTCOMP_SIMPLE]

    def test_nested(self) -> None:
        node = parse_first("[x for x in items for y in other]", ast.ListComp)
        assert get_level_list_comp(node) == [ClassId.LISTCOMP_NESTED]

    def test_with_if(self) -> None:
        node = parse_first("[x for x in items if x > 0]", ast.ListComp)
        assert get_level_list_comp(node) == [ClassId.LISTCOMP_WITH_IF]


# ---------------------------------------------------------------------------
# Dicts
# ---------------------------------------------------------------------------


class TestGetLevelDict:
    def test_simple(self) -> None:
        node = parse_first("{'a': 1, 'b': 2}", ast.Dict)
        assert get_level_dict(node) == [ClassId.DICT_SIMPLE]

    def test_nested(self) -> None:
        node = parse_first("{'a': {'b': 1}}", ast.Dict)
        assert get_level_dict(node) == [ClassId.DICT_NESTED]

    def test_with_list(self) -> None:
        node = parse_first("{'a': [1, 2]}", ast.Dict)
        assert get_level_dict(node) == [ClassId.DICT_WITH_LIST]

    def test_with_dict_list(self) -> None:
        node = parse_first("{'a': {'b': [1, 2]}}", ast.Dict)
        assert get_level_dict(node) == [ClassId.DICT_WITH_DICT_LIST]

    def test_nested_dict_without_inner_list(self) -> None:
        node = parse_first("{'a': {'b': 1}}", ast.Dict)
        assert get_level_dict(node) == [ClassId.DICT_NESTED]


# ---------------------------------------------------------------------------
# Dict comprehensions
# ---------------------------------------------------------------------------


class TestGetLevelDictComp:
    def test_simple(self) -> None:
        node = parse_first("{k: v for k, v in items}", ast.DictComp)
        assert get_level_dict_comp(node) == [ClassId.DICTCOMP_SIMPLE]

    def test_with_if(self) -> None:
        node = parse_first("{k: v for k, v in items if k > 0}", ast.DictComp)
        assert get_level_dict_comp(node) == [ClassId.DICTCOMP_WITH_IF]

    def test_with_if_else(self) -> None:
        node = parse_first("{k: v if v > 0 else 0 for k, v in items}", ast.DictComp)
        assert get_level_dict_comp(node) == [ClassId.DICTCOMP_WITH_IF_ELSE]

    def test_nested(self) -> None:
        node = parse_first("{k: {i: i for i in v} for k, v in items}", ast.DictComp)
        assert get_level_dict_comp(node) == [ClassId.DICTCOMP_NESTED]


# ---------------------------------------------------------------------------
# Tuples
# ---------------------------------------------------------------------------


class TestGetLevelTuple:
    def test_simple(self) -> None:
        node = parse_first("(1, 2, 3)", ast.Tuple)
        assert get_level_tuple(node) == [ClassId.TUPLE_SIMPLE]

    def test_nested(self) -> None:
        node = parse_first("((1, 2), (3, 4))", ast.Tuple)
        assert get_level_tuple(node) == [ClassId.TUPLE_NESTED]


# ---------------------------------------------------------------------------
# Function calls
# ---------------------------------------------------------------------------


class TestGetLevelCall:
    @pytest.mark.parametrize(
        "code, expected",
        [
            ("print('hello')", ClassId.PRINT_SIMPLE),
            ("open('file.txt')", ClassId.FILE_OPEN),
            ("range(10)", ClassId.LOOP_RANGE),
            ("zip(a, b)", ClassId.LOOP_ZIP),
            ("map(str, items)", ClassId.LOOP_MAP),
            ("enumerate(items)", ClassId.LOOP_ENUMERATE),
            ("super()", ClassId.SUPERFUNCTION_SIMPLE),
        ],
    )
    def test_builtin_by_name(self, code: str, expected: ClassId) -> None:
        node = parse_first(code, ast.Call)
        assert get_level_call(node) == [expected]

    @pytest.mark.parametrize(
        "code, expected",
        [
            ("f.write('data')", ClassId.FILE_WRITE),
            ("f.read()", ClassId.FILE_READ),
            ("f.readline()", ClassId.FILE_READLINE),
            ("f.writelines(lines)", ClassId.FILE_WRITELINES),
        ],
    )
    def test_attribute_call(self, code: str, expected: ClassId) -> None:
        node = parse_first(code, ast.Call)
        assert get_level_call(node) == [expected]

    def test_unknown_function_name(self) -> None:
        node = parse_first("foo()", ast.Call)
        assert get_level_call(node) == [ClassId.UNKNOWN]

    def test_unknown_attribute_method(self) -> None:
        node = parse_first("obj.foo()", ast.Call)
        assert get_level_call(node) == [ClassId.UNKNOWN]


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------


class TestGetLevelAssign:
    def test_simple(self) -> None:
        node = parse_first("x = 5", ast.Assign)
        assert get_level_assign(node) == [ClassId.ASSIGN_SIMPLE]

    def test_with_operator(self) -> None:
        node = parse_first("x = a + b", ast.Assign)
        assert get_level_assign(node) == [ClassId.ASSIGN_WITH_OPERATOR]

    def test_augmented(self) -> None:
        node = parse_first("x += 1", ast.AugAssign)
        assert get_level_assign(node) == [ClassId.ASSIGN_INCREMENTS]

    def test_string_assign_is_simple(self) -> None:
        node = parse_first("x = 'hello'", ast.Assign)
        assert get_level_assign(node) == [ClassId.ASSIGN_SIMPLE]


# ---------------------------------------------------------------------------
# If statements
# ---------------------------------------------------------------------------


class TestGetLevelIf:
    def test_simple(self) -> None:
        node = parse_first("if x > 0:\n    pass", ast.If)
        assert get_level_if(node) == [ClassId.IF_SIMPLE]

    def test_name_main(self) -> None:
        node = parse_first('if __name__ == "__main__":\n    pass', ast.If)
        assert get_level_if(node) == [ClassId.IF_NAME_MAIN]

    def test_if_else_still_simple(self) -> None:
        node = parse_first("if x:\n    pass\nelse:\n    pass", ast.If)
        assert get_level_if(node) == [ClassId.IF_SIMPLE]


# ---------------------------------------------------------------------------
# For loops
# ---------------------------------------------------------------------------


class TestGetLevelFor:
    def test_simple(self) -> None:
        node = parse_first("for x in items:\n    pass", ast.For)
        assert get_level_for(node) == [ClassId.LOOP_FOR_SIMPLE]

    def test_nested(self) -> None:
        code = "for x in items:\n    for y in other:\n        pass"
        node = parse_first(code, ast.For)
        assert get_level_for(node) == [ClassId.LOOP_FOR_NESTED]

    def test_tuple_unpacking(self) -> None:
        node = parse_first("for k, v in items:\n    pass", ast.For)
        assert get_level_for(node) == [ClassId.LOOP_FOR_TUPLE_NAME]

    def test_list_iterate(self) -> None:
        node = parse_first("for x in [1, 2, 3]:\n    pass", ast.For)
        assert get_level_for(node) == [ClassId.LOOP_FOR_LIST_ITERATE]

    def test_tuple_iterate(self) -> None:
        node = parse_first("for x in (1, 2, 3):\n    pass", ast.For)
        assert get_level_for(node) == [ClassId.LOOP_FOR_TUPLE_ITERATE]


# ---------------------------------------------------------------------------
# While loops
# ---------------------------------------------------------------------------


class TestGetLevelWhile:
    def test_simple(self) -> None:
        node = parse_first("while True:\n    pass", ast.While)
        assert get_level_while(node) == [ClassId.LOOP_WHILE_SIMPLE]

    def test_while_else(self) -> None:
        node = parse_first("while True:\n    pass\nelse:\n    pass", ast.While)
        assert get_level_while(node) == [ClassId.LOOP_WHILE_ELSE]


# ---------------------------------------------------------------------------
# Function definitions
# ---------------------------------------------------------------------------


class TestGetLevelFunction:
    def test_simple(self) -> None:
        node = parse_first("def foo():\n    pass", ast.FunctionDef)
        assert get_level_function(node) == [ClassId.FUNCTIONDEF_SIMPLE]

    def test_staticmethod(self) -> None:
        code = "class A:\n    @staticmethod\n    def foo():\n        pass"
        node = parse_first(code, ast.FunctionDef)
        assert ClassId.STATIC_STATICMETHOD in get_level_function(node)

    def test_classmethod(self) -> None:
        code = "class A:\n    @classmethod\n    def foo(cls):\n        pass"
        node = parse_first(code, ast.FunctionDef)
        assert ClassId.STATIC_CLASSMETHOD in get_level_function(node)

    def test_recursive(self) -> None:
        code = "def factorial(n):\n    return n * factorial(n - 1)"
        node = parse_first(code, ast.FunctionDef)
        assert ClassId.FUNCTIONDEF_RECURSIVE in get_level_function(node)

    def test_default_args(self) -> None:
        node = parse_first("def foo(x=1):\n    pass", ast.FunctionDef)
        assert ClassId.FUNCTIONDEF_ARGUM_DEFAULT in get_level_function(node)

    def test_star_args(self) -> None:
        node = parse_first("def foo(*args):\n    pass", ast.FunctionDef)
        assert ClassId.FUNCTIONDEF_ARGUM_STAR in get_level_function(node)

    def test_double_star_kwargs(self) -> None:
        node = parse_first("def foo(**kwargs):\n    pass", ast.FunctionDef)
        assert ClassId.FUNCTIONDEF_ARGUM_DBL_STAR in get_level_function(node)

    def test_keyword_only_args(self) -> None:
        node = parse_first("def foo(*, key):\n    pass", ast.FunctionDef)
        assert ClassId.FUNCTIONDEF_ARGUM_KEYWORD_ONLY in get_level_function(node)

    def test_multiple_features_combined(self) -> None:
        node = parse_first("def foo(*args, **kwargs):\n    pass", ast.FunctionDef)
        result = get_level_function(node)
        assert ClassId.FUNCTIONDEF_ARGUM_STAR in result
        assert ClassId.FUNCTIONDEF_ARGUM_DBL_STAR in result
        assert ClassId.FUNCTIONDEF_SIMPLE not in result

    def test_no_features_yields_simple(self) -> None:
        node = parse_first("def foo(x, y):\n    return x + y", ast.FunctionDef)
        assert get_level_function(node) == [ClassId.FUNCTIONDEF_SIMPLE]


# ---------------------------------------------------------------------------
# Class definitions
# ---------------------------------------------------------------------------


class TestGetLevelClass:
    def test_simple(self) -> None:
        node = parse_first("class Foo:\n    pass", ast.ClassDef)
        assert get_level_class(node) == [ClassId.CLASS_SIMPLE]

    def test_inherited(self) -> None:
        node = parse_first("class Foo(Bar):\n    pass", ast.ClassDef)
        assert ClassId.CLASS_INHERITED in get_level_class(node)

    def test_init(self) -> None:
        code = "class Foo:\n    def __init__(self):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_INIT in get_level_class(node)

    def test_private_method(self) -> None:
        code = "class Foo:\n    def __secret(self):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_PRIVATE in get_level_class(node)

    def test_dunder_not_classified_as_private(self) -> None:
        code = "class Foo:\n    def __init__(self):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_PRIVATE not in get_level_class(node)

    def test_descriptor_get(self) -> None:
        code = "class Foo:\n    def __get__(self, obj, objtype):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_DESCRIPTORS in get_level_class(node)

    def test_descriptor_set(self) -> None:
        code = "class Foo:\n    def __set__(self, obj, value):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_DESCRIPTORS in get_level_class(node)

    def test_descriptor_delete(self) -> None:
        code = "class Foo:\n    def __delete__(self, obj):\n        pass"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_DESCRIPTORS in get_level_class(node)

    def test_property_decorator(self) -> None:
        code = "class Foo:\n    @property\n    def bar(self):\n        return self._bar"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.CLASS_PROPERTIES in get_level_class(node)

    def test_metaclass_keyword(self) -> None:
        node = parse_first("class Foo(metaclass=Meta):\n    pass", ast.ClassDef)
        assert ClassId.METACLASS_METACLASS in get_level_class(node)

    def test_slots(self) -> None:
        code = "class Foo:\n    __slots__ = ['x', 'y']"
        node = parse_first(code, ast.ClassDef)
        assert ClassId.SLOTS_ATTR in get_level_class(node)

    def test_multiple_features(self) -> None:
        code = "class Foo(Bar):\n    __slots__ = ['x']\n    def __init__(self):\n        pass"
        node = parse_first(code, ast.ClassDef)
        result = get_level_class(node)
        assert ClassId.CLASS_INHERITED in result
        assert ClassId.SLOTS_ATTR in result
        assert ClassId.CLASS_INIT in result
        assert ClassId.CLASS_SIMPLE not in result


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------


class TestGetLevelImport:
    def test_simple_import(self) -> None:
        node = parse_first("import os", ast.Import)
        assert get_level_import(node) == [ClassId.IMPORT_SIMPLE]

    def test_import_as(self) -> None:
        node = parse_first("import numpy as np", ast.Import)
        assert get_level_import(node) == [ClassId.IMPORT_AS_EXTENSION]

    def test_from_import(self) -> None:
        node = parse_first("from os import path", ast.ImportFrom)
        assert get_level_import(node) == [ClassId.IMPORT_FROM_SIMPLE]

    def test_from_relative(self) -> None:
        node = parse_first("from . import module", ast.ImportFrom)
        assert get_level_import(node) == [ClassId.IMPORT_FROM_RELATIVE]

    def test_from_star(self) -> None:
        node = parse_first("from os import *", ast.ImportFrom)
        assert get_level_import(node) == [ClassId.IMPORT_FROM_STAR]

    @pytest.mark.parametrize(
        "code, expected",
        [
            ("import re", ClassId.MODULES_RE),
            ("import pickle", ClassId.MODULES_PICKLE),
            ("import struct", ClassId.MODULES_STRUCT),
            ("import importlib", ClassId.MODULES_IMPORTLIB),
        ],
    )
    def test_special_module_import(self, code: str, expected: ClassId) -> None:
        node = parse_first(code, ast.Import)
        assert get_level_import(node) == [expected]

    def test_special_module_from_import(self) -> None:
        node = parse_first("from re import match", ast.ImportFrom)
        assert get_level_import(node) == [ClassId.MODULES_RE]


# ---------------------------------------------------------------------------
# Try / except
# ---------------------------------------------------------------------------


class TestGetLevelTry:
    def test_basic_try_except(self) -> None:
        code = "try:\n    pass\nexcept:\n    pass"
        node = parse_first(code, ast.Try)
        assert get_level_try(node) == [ClassId.EXCEPTION_TRY_EXCEPT]

    def test_try_except_else(self) -> None:
        code = "try:\n    pass\nexcept:\n    pass\nelse:\n    pass"
        node = parse_first(code, ast.Try)
        assert get_level_try(node) == [ClassId.EXCEPTION_TRY_ELSE_EXCEPT]

    def test_try_except_finally(self) -> None:
        code = "try:\n    pass\nexcept:\n    pass\nfinally:\n    pass"
        node = parse_first(code, ast.Try)
        assert get_level_try(node) == [ClassId.EXCEPTION_TRY_EXCEPT_FINALLY]

    def test_try_except_else_finally_returns_finally_variant(self) -> None:
        code = "try:\n    pass\nexcept:\n    pass\nelse:\n    pass\nfinally:\n    pass"
        node = parse_first(code, ast.Try)
        assert get_level_try(node) == [ClassId.EXCEPTION_TRY_EXCEPT_FINALLY]

    def test_nested_try(self) -> None:
        code = "try:\n    try:\n        pass\n    except:\n        pass\nexcept:\n    pass"
        node = parse_first(code, ast.Try)
        assert get_level_try(node) == [ClassId.EXCEPTION_TRY_TRY]


# ---------------------------------------------------------------------------
# Dispatcher — get_class_from_ast_node
# ---------------------------------------------------------------------------


class TestGetClassFromAstNode:
    def test_routes_list(self) -> None:
        node = parse_first("[1, 2]", ast.List)
        assert get_class_from_ast_node(node) == [ClassId.LIST_SIMPLE]

    def test_routes_list_comp(self) -> None:
        node = parse_first("[x for x in y]", ast.ListComp)
        assert get_class_from_ast_node(node) == [ClassId.LISTCOMP_SIMPLE]

    def test_routes_dict(self) -> None:
        node = parse_first("{'a': 1}", ast.Dict)
        assert get_class_from_ast_node(node) == [ClassId.DICT_SIMPLE]

    def test_routes_dict_comp(self) -> None:
        node = parse_first("{k: v for k, v in x}", ast.DictComp)
        assert get_class_from_ast_node(node) == [ClassId.DICTCOMP_SIMPLE]

    def test_routes_tuple(self) -> None:
        node = parse_first("(1, 2)", ast.Tuple)
        assert get_class_from_ast_node(node) == [ClassId.TUPLE_SIMPLE]

    def test_routes_call(self) -> None:
        node = parse_first("print('hi')", ast.Call)
        assert get_class_from_ast_node(node) == [ClassId.PRINT_SIMPLE]

    def test_routes_assign(self) -> None:
        node = parse_first("x = 5", ast.Assign)
        assert get_class_from_ast_node(node) == [ClassId.ASSIGN_SIMPLE]

    def test_routes_aug_assign(self) -> None:
        node = parse_first("x += 1", ast.AugAssign)
        assert get_class_from_ast_node(node) == [ClassId.ASSIGN_INCREMENTS]

    def test_routes_if(self) -> None:
        node = parse_first("if x:\n    pass", ast.If)
        assert get_class_from_ast_node(node) == [ClassId.IF_SIMPLE]

    def test_routes_for(self) -> None:
        node = parse_first("for x in y:\n    pass", ast.For)
        assert get_class_from_ast_node(node) == [ClassId.LOOP_FOR_SIMPLE]

    def test_routes_while(self) -> None:
        node = parse_first("while True:\n    pass", ast.While)
        assert get_class_from_ast_node(node) == [ClassId.LOOP_WHILE_SIMPLE]

    def test_routes_function(self) -> None:
        node = parse_first("def f():\n    pass", ast.FunctionDef)
        assert get_class_from_ast_node(node) == [ClassId.FUNCTIONDEF_SIMPLE]

    def test_routes_class(self) -> None:
        node = parse_first("class C:\n    pass", ast.ClassDef)
        assert get_class_from_ast_node(node) == [ClassId.CLASS_SIMPLE]

    def test_routes_import(self) -> None:
        node = parse_first("import os", ast.Import)
        assert get_class_from_ast_node(node) == [ClassId.IMPORT_SIMPLE]

    def test_routes_import_from(self) -> None:
        node = parse_first("from os import path", ast.ImportFrom)
        assert get_class_from_ast_node(node) == [ClassId.IMPORT_FROM_SIMPLE]

    def test_routes_try(self) -> None:
        node = parse_first("try:\n    pass\nexcept:\n    pass", ast.Try)
        assert get_class_from_ast_node(node) == [ClassId.EXCEPTION_TRY_EXCEPT]

    # --- Direct-return nodes (no sub-function) ---

    def test_if_expression(self) -> None:
        node = parse_first("x = a if True else b", ast.IfExp)
        assert get_class_from_ast_node(node) == [ClassId.IF_EXPRESSION]

    def test_break(self) -> None:
        node = parse_first("for x in y:\n    break", ast.Break)
        assert get_class_from_ast_node(node) == [ClassId.LOOP_BREAK]

    def test_continue(self) -> None:
        node = parse_first("for x in y:\n    continue", ast.Continue)
        assert get_class_from_ast_node(node) == [ClassId.LOOP_CONTINUE]

    def test_pass(self) -> None:
        node = parse_first("pass", ast.Pass)
        assert get_class_from_ast_node(node) == [ClassId.LOOP_PASS]

    def test_return(self) -> None:
        node = parse_first("def f():\n    return 1", ast.Return)
        assert get_class_from_ast_node(node) == [ClassId.RETURN_SIMPLE]

    def test_lambda(self) -> None:
        node = parse_first("f = lambda x: x", ast.Lambda)
        assert get_class_from_ast_node(node) == [ClassId.LAMBDA_SIMPLE]

    def test_raise(self) -> None:
        node = parse_first("raise ValueError()", ast.Raise)
        assert get_class_from_ast_node(node) == [ClassId.EXCEPTION_RAISE]

    def test_assert(self) -> None:
        node = parse_first("assert True", ast.Assert)
        assert get_class_from_ast_node(node) == [ClassId.EXCEPTION_ASSERT]

    def test_with(self) -> None:
        node = parse_first("with open('f') as x:\n    pass", ast.With)
        assert get_class_from_ast_node(node) == [ClassId.WITH_SIMPLE]

    def test_yield(self) -> None:
        node = parse_first("def f():\n    yield 1", ast.Yield)
        assert get_class_from_ast_node(node) == [ClassId.GENERATORS_FUNCTION]

    def test_yield_from(self) -> None:
        node = parse_first("def f():\n    yield from [1]", ast.YieldFrom)
        assert get_class_from_ast_node(node) == [ClassId.GENERATORS_FUNCTION]

    def test_async_function(self) -> None:
        node = parse_first("async def f():\n    pass", ast.AsyncFunctionDef)
        assert get_class_from_ast_node(node) == [ClassId.ASYNC_AWAIT]

    def test_await(self) -> None:
        node = parse_first("async def f():\n    await g()", ast.Await)
        assert get_class_from_ast_node(node) == [ClassId.ASYNC_AWAIT]

    def test_match(self) -> None:
        node = parse_first("match x:\n    case 1:\n        pass", ast.Match)
        assert get_class_from_ast_node(node) == [ClassId.PATTERN_MATCHING]

    def test_type_hinting(self) -> None:
        node = parse_first("x: int = 5", ast.AnnAssign)
        assert get_class_from_ast_node(node) == [ClassId.TYPE_HINTING]

    def test_unknown_node(self) -> None:
        node = parse_first("x = 5", ast.Constant)
        assert get_class_from_ast_node(node) == [ClassId.UNKNOWN]


# ---------------------------------------------------------------------------
# Level mapping — get_default_class_level
# ---------------------------------------------------------------------------


class TestGetDefaultClassLevel:
    def test_unknown_returns_unknown_level(self) -> None:
        assert get_default_class_level(ClassId.UNKNOWN) == Level.UNKNOWN

    def test_every_non_unknown_classid_has_a_level(self) -> None:
        unmapped = [
            cid
            for cid in ClassId
            if cid != ClassId.UNKNOWN and get_default_class_level(cid) == Level.UNKNOWN
        ]
        assert unmapped == [], f"ClassIds without level mapping: {[c.name for c in unmapped]}"

    @pytest.mark.parametrize(
        "class_id, expected_level",
        [
            (ClassId.LIST_SIMPLE, Level.A1),
            (ClassId.PRINT_SIMPLE, Level.A1),
            (ClassId.ASSIGN_SIMPLE, Level.A1),
            (ClassId.LOOP_FOR_SIMPLE, Level.A1),
            (ClassId.IMPORT_SIMPLE, Level.A1),
            (ClassId.LIST_NESTED, Level.A2),
            (ClassId.FUNCTIONDEF_SIMPLE, Level.A2),
            (ClassId.EXCEPTION_TRY_EXCEPT, Level.A2),
            (ClassId.DICT_SIMPLE, Level.A2),
            (ClassId.CLASS_SIMPLE, Level.B1),
            (ClassId.IMPORT_FROM_RELATIVE, Level.B1),
            (ClassId.WITH_SIMPLE, Level.B1),
            (ClassId.LAMBDA_SIMPLE, Level.B2),
            (ClassId.CLASS_INHERITED, Level.B2),
            (ClassId.FUNCTIONDEF_RECURSIVE, Level.B2),
            (ClassId.GENERATORS_FUNCTION, Level.C1),
            (ClassId.CLASS_DESCRIPTORS, Level.C1),
            (ClassId.MODULES_IMPORTLIB, Level.C1),
            (ClassId.METACLASS_METACLASS, Level.C2),
            (ClassId.METACLASS_NEW, Level.C2),
        ],
    )
    def test_spot_check_levels(self, class_id: ClassId, expected_level: Level) -> None:
        assert get_default_class_level(class_id) == expected_level
