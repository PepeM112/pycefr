from pydantic import BaseModel
from common import Level
from enum import Enum


class ClassEnum(Enum):
    UNKNOWN = 0
    # --- List ---
    LIST_SIMPLE = 1
    LIST_NESTED = 2
    LIST_WITH_DICT = 3
    # --- ListComp ---
    LISTCOMP_SIMPLE = 4
    LISTCOMP_NESTED = 5
    LISTCOMP_WITH_IF = 6
    # --- Dict ---
    DICT_SIMPLE = 7
    DICT_NESTED = 8
    DICT_WITH_LIST = 9
    DICT_WITH_DICT_LIST = 10
    # --- Tuple ---
    TUPLE_SIMPLE = 11
    TUPLE_NESTED = 12
    # --- File ---
    FILE_OPEN = 13
    FILE_WRITE = 14
    FILE_WRITELINES = 15
    FILE_READ = 16
    FILE_READLINE = 17
    # --- Print ---
    PRINT_SIMPLE = 18
    # --- Assign ---
    ASSIGN_SIMPLE = 19
    ASSIGN_WITH_SUM = 20
    ASSIGN_INCREMENTS = 21
    # --- If-Statements ---
    IF_SIMPLE = 22
    IF_EXPRESSION = 23
    IF___NAME__ = 24
    # --- Loop ---
    LOOP_BREAK = 25
    LOOP_CONTINUE = 26
    LOOP_PASS = 27
    LOOP_WHILE_SIMPLE = 28
    LOOP_WHILE_ELSE = 29
    LOOP_FOR_SIMPLE = 30
    LOOP_FOR_NESTED = 31
    LOOP_FOR_TUPLE_NAME = 32
    LOOP_FOR_LIST_ITERATE = 33
    LOOP_FOR_TUPLE_ITERATE = 34
    LOOP_RANGE = 35
    LOOP_ZIP = 36
    LOOP_MAP = 37
    LOOP_ENUMERATE = 38
    # --- FunctionDef ---
    FUNCTIONDEF_SIMPLE = 39
    FUNCTIONDEF_ARGUM_DEFAULT = 40
    FUNCTIONDEF_ARGUM_STAR = 41
    FUNCTIONDEF_ARGUM_DOUBLESTAR = 42
    FUNCTIONDEF_ARGUM_KEYWORD_ONLY = 43
    FUNCTIONDEF_RECURSIVE = 44
    # --- Return ---
    RETURN_SIMPLE = 45
    # --- Lambda ---
    LAMBDA_SIMPLE = 46
    # --- Generators ---
    GENERATORS_FUNCTION = 47
    GENERATORS_EXPRESSION = 48
    # --- Import ---
    IMPORT_IMPORT = 49
    IMPORT_FROM_SIMPLE = 50
    IMPORT_FROM_RELATIVE = 51
    IMPORT_FROM_STAR_STATEMENTS = 52
    IMPORT_AS_EXTENSION = 53
    # --- Modules ---
    MODULES_STRUCT = 54
    MODULES_PICKLE = 55
    MODULES_SHELVE = 56
    MODULES_DBM = 57
    MODULES_RE = 58
    MODULES_IMPORTLIB = 59
    # --- Class ---
    CLASS_SIMPLE = 60
    CLASS_INHERITED = 61
    CLASS___INIT__ = 62
    CLASS_DESCRIPTORS = 63
    CLASS_PROPERTIES = 64
    CLASS_PRIVATE = 65
    # --- Static ---
    STATIC_CLASSMETHODSS = 66
    STATIC_STATICMETHOD = 67
    # --- Decorators ---
    DECORATORS_FUNCTION = 68
    DECORATORS_CLASS = 69
    # --- Metaclass ---
    METACLASS___NEW__ = 70
    METACLASS_METACLASS = 71
    METACLASS___METACLASS__ = 72
    # --- SuperFunction ---
    SUPERFUNCTION_SIMPLE = 73
    # --- Slots ---
    SLOTS___SLOTS__ = 74
    # --- Attributes ---
    ATTRIBUTES_SIMPLE = 75
    ATTRIBUTES___CLASS__ = 76
    ATTRIBUTES___DICT__ = 77
    # --- Exception ---
    EXCEPTION_TRY_EXCEPT = 78
    EXCEPTION_TRY_ELSE_EXCEPT = 79
    EXCEPTION_TRY_TRY = 80
    EXCEPTION_TRY_FINALLY = 81
    EXCEPTION_TRY_EXCEPT_FINALLY = 82
    EXCEPTION_TRY_EXCEPT_ELSE_FINALLY = 83
    EXCEPTION_RAISE = 84
    EXCEPTION_ASSERT = 85
    # --- With ---
    WITH_SIMPLE = 86


class ClassItem(BaseModel):
    id: int
    name: str
    level: Level
