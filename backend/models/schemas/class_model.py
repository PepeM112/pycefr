from enum import IntEnum

from pydantic import BaseModel

from backend.models.schemas.common import BaseSchema, Level, NamedIntEnum


class ClassId(NamedIntEnum):
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
    # --- DictComp ---
    DICTCOMP_SIMPLE = 11
    DICTCOMP_WITH_IF = 12
    DICTCOMP_WITH_IF_ELSE = 13
    DICTCOMP_NESTED = 14
    # --- Tuple ---
    TUPLE_SIMPLE = 15
    TUPLE_NESTED = 16
    # --- File ---
    FILE_OPEN = 17
    FILE_WRITE = 18
    FILE_WRITELINES = 19
    FILE_READ = 20
    FILE_READLINE = 21
    # --- Print ---
    PRINT_SIMPLE = 22
    # --- Assign ---
    ASSIGN_SIMPLE = 23
    ASSIGN_WITH_OPERATOR = 24
    ASSIGN_INCREMENTS = 25
    # --- If-Statements ---
    IF_SIMPLE = 26
    IF_EXPRESSION = 27
    IF_NAME_MAIN = 28  # For if __name__ == "__main__"
    # --- Loop ---
    LOOP_BREAK = 29
    LOOP_CONTINUE = 30
    LOOP_PASS = 31
    LOOP_WHILE_SIMPLE = 32
    LOOP_WHILE_ELSE = 33
    LOOP_FOR_SIMPLE = 34
    LOOP_FOR_NESTED = 35
    LOOP_FOR_TUPLE_NAME = 36
    LOOP_FOR_LIST_ITERATE = 37
    LOOP_FOR_TUPLE_ITERATE = 38
    LOOP_RANGE = 39
    LOOP_ZIP = 40
    LOOP_MAP = 41
    LOOP_ENUMERATE = 42
    # --- FunctionDef ---
    FUNCTIONDEF_SIMPLE = 43
    FUNCTIONDEF_ARGUM_DEFAULT = 44
    FUNCTIONDEF_ARGUM_STAR = 45  # *args
    FUNCTIONDEF_ARGUM_DBL_STAR = 46  # **kwargs
    FUNCTIONDEF_ARGUM_KEYWORD_ONLY = 47
    FUNCTIONDEF_RECURSIVE = 48
    # --- Return ---
    RETURN_SIMPLE = 49
    # --- Lambda ---
    LAMBDA_SIMPLE = 50
    # --- Generators ---
    GENERATORS_FUNCTION = 51
    GENERATORS_EXPRESSION = 52
    # --- Import ---
    IMPORT_SIMPLE = 53
    IMPORT_FROM_SIMPLE = 54
    IMPORT_FROM_RELATIVE = 55
    IMPORT_FROM_STAR = 56
    IMPORT_AS_EXTENSION = 57
    # --- Modules ---
    MODULES_STRUCT = 58
    MODULES_PICKLE = 59
    MODULES_SHELVE = 60
    MODULES_DBM = 61
    MODULES_RE = 62
    MODULES_IMPORTLIB = 63
    # --- Class ---
    CLASS_SIMPLE = 64
    CLASS_INHERITED = 65
    CLASS_INIT = 66
    CLASS_DESCRIPTORS = 67
    CLASS_PROPERTIES = 68
    CLASS_PRIVATE = 69
    # --- Static ---
    STATIC_CLASSMETHOD = 70
    STATIC_STATICMETHOD = 71
    # --- Decorators ---
    DECORATORS_FUNCTION = 72
    DECORATORS_CLASS = 73
    # --- Metaclass ---
    METACLASS_NEW = 74
    METACLASS_METACLASS = 75
    METACLASS_ATTR_METACLASS = 76
    # --- Superfunction ---
    SUPERFUNCTION_SIMPLE = 77
    # --- Slots ---
    SLOTS_ATTR = 78
    # --- Attributes ---
    ATTRIBUTES_SIMPLE = 79
    ATTRIBUTES_CLASS_REF = 80  # __class__
    ATTRIBUTES_DICT_REF = 81  # __dict__
    # --- Exception ---
    EXCEPTION_TRY_EXCEPT = 82
    EXCEPTION_TRY_ELSE_EXCEPT = 83
    EXCEPTION_TRY_TRY = 84
    EXCEPTION_TRY_FINALLY = 85
    EXCEPTION_TRY_EXCEPT_FINALLY = 86
    EXCEPTION_TRY_EXCEPT_ELSE_FINALLY = 87
    EXCEPTION_RAISE = 88
    EXCEPTION_ASSERT = 89
    # --- With ---
    WITH_SIMPLE = 90


class ClassBase(BaseModel):
    id: ClassId
    level: Level


class ClassPublic(BaseSchema, ClassBase):
    pass
