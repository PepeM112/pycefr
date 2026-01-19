from typing import Optional, TypedDict

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Level


class ClassDetails(TypedDict):
    name: str
    level: Level


CODE_CLASS_DETAILS: dict[ClassId, ClassDetails] = {
    # --- LIST ---
    ClassId.LIST_SIMPLE: {"name": "List: Simple", "level": Level.A1},
    ClassId.LIST_NESTED: {"name": "List: Anidada", "level": Level.A2},
    ClassId.LIST_WITH_DICT: {"name": "List: Con Diccionario", "level": Level.B1},
    # --- LISTCOMP ---
    ClassId.LISTCOMP_SIMPLE: {"name": "ListComp: Simple", "level": Level.A2},
    ClassId.LISTCOMP_NESTED: {"name": "ListComp: Anidada", "level": Level.B1},
    ClassId.LISTCOMP_WITH_IF: {"name": "ListComp: Con Condicional", "level": Level.B1},
    # --- DICT ---
    ClassId.DICT_SIMPLE: {"name": "Dict: Simple", "level": Level.A2},
    ClassId.DICT_NESTED: {"name": "Dict: Anidado", "level": Level.B1},
    ClassId.DICT_WITH_LIST: {"name": "Dict: Con Lista", "level": Level.B1},
    ClassId.DICT_WITH_DICT_LIST: {"name": "Dict: Estructura Compleja", "level": Level.B2},
    # --- DICTCOMP ---
    ClassId.DICTCOMP_SIMPLE: {"name": "DictComp: Simple", "level": Level.B1},
    ClassId.DICTCOMP_WITH_IF: {"name": "DictComp: Con Condicional", "level": Level.B1},
    ClassId.DICTCOMP_WITH_IF_ELSE: {"name": "DictComp: Con If-Else", "level": Level.B1},
    ClassId.DICTCOMP_NESTED: {"name": "DictComp: Anidado", "level": Level.B2},
    # --- TUPLE ---
    ClassId.TUPLE_SIMPLE: {"name": "Tuple: Simple", "level": Level.A1},
    ClassId.TUPLE_NESTED: {"name": "Tuple: Anidada", "level": Level.A2},
    # --- FILE ---
    ClassId.FILE_OPEN: {"name": "File: Apertura (open)", "level": Level.A2},
    ClassId.FILE_WRITE: {"name": "File: Escritura (write)", "level": Level.A2},
    ClassId.FILE_WRITELINES: {"name": "File: Escritura Múltiple", "level": Level.B1},
    ClassId.FILE_READ: {"name": "File: Lectura Completa", "level": Level.A2},
    ClassId.FILE_READLINE: {"name": "File: Lectura por Línea", "level": Level.A2},
    # --- PRINT ---
    ClassId.PRINT_SIMPLE: {"name": "Print: Salida estándar", "level": Level.A1},
    # --- ASSIGN ---
    ClassId.ASSIGN_SIMPLE: {"name": "Assign: Simple", "level": Level.A1},
    ClassId.ASSIGN_WITH_OPERATOR: {"name": "Assign: Con Operación", "level": Level.A1},
    ClassId.ASSIGN_INCREMENTS: {"name": "Assign: Incremento (+=)", "level": Level.A1},
    # --- IF-STATEMENTS ---
    ClassId.IF_SIMPLE: {"name": "If: Condicional Simple", "level": Level.A1},
    ClassId.IF_EXPRESSION: {"name": "If: Operador Ternario", "level": Level.A2},
    ClassId.IF_NAME_MAIN: {"name": "If: Script Entry Point (__main__)", "level": Level.A2},
    # --- LOOP ---
    ClassId.LOOP_BREAK: {"name": "Loop: Control break", "level": Level.A2},
    ClassId.LOOP_CONTINUE: {"name": "Loop: Control continue", "level": Level.A2},
    ClassId.LOOP_PASS: {"name": "Loop: Placeholder pass", "level": Level.A1},
    ClassId.LOOP_WHILE_SIMPLE: {"name": "Loop: While", "level": Level.A2},
    ClassId.LOOP_WHILE_ELSE: {"name": "Loop: While-Else", "level": Level.B1},
    ClassId.LOOP_FOR_SIMPLE: {"name": "Loop: For simple", "level": Level.A1},
    ClassId.LOOP_FOR_NESTED: {"name": "Loop: For anidado", "level": Level.A2},
    ClassId.LOOP_FOR_TUPLE_NAME: {"name": "Loop: For con desempaquetado", "level": Level.A2},
    ClassId.LOOP_FOR_LIST_ITERATE: {"name": "Loop: For sobre lista", "level": Level.A1},
    ClassId.LOOP_FOR_TUPLE_ITERATE: {"name": "Loop: For sobre tupla", "level": Level.A1},
    ClassId.LOOP_RANGE: {"name": "Loop: Uso de range()", "level": Level.A1},
    ClassId.LOOP_ZIP: {"name": "Loop: Uso de zip()", "level": Level.B1},
    ClassId.LOOP_MAP: {"name": "Loop: Uso de map()", "level": Level.B1},
    ClassId.LOOP_ENUMERATE: {"name": "Loop: Uso de enumerate()", "level": Level.A2},
    # --- FUNCTIONDEF ---
    ClassId.FUNCTIONDEF_SIMPLE: {"name": "Func: Definición simple", "level": Level.A2},
    ClassId.FUNCTIONDEF_ARGUM_DEFAULT: {"name": "Func: Argumentos por defecto", "level": Level.B1},
    ClassId.FUNCTIONDEF_ARGUM_STAR: {"name": "Func: Argumentos variables (*args)", "level": Level.B1},
    ClassId.FUNCTIONDEF_ARGUM_DBL_STAR: {"name": "Func: Argumentos clave (**kwargs)", "level": Level.B1},
    ClassId.FUNCTIONDEF_ARGUM_KEYWORD_ONLY: {"name": "Func: Keyword-only arguments", "level": Level.B2},
    ClassId.FUNCTIONDEF_RECURSIVE: {"name": "Func: Recursividad", "level": Level.B2},
    # --- RETURN ---
    ClassId.RETURN_SIMPLE: {"name": "Return: Retorno simple", "level": Level.A2},
    # --- LAMBDA ---
    ClassId.LAMBDA_SIMPLE: {"name": "Lambda: Funciones anónimas", "level": Level.B1},
    # --- GENERATORS ---
    ClassId.GENERATORS_FUNCTION: {"name": "Gen: Función generadora (yield)", "level": Level.B2},
    ClassId.GENERATORS_EXPRESSION: {"name": "Gen: Expresión generadora", "level": Level.B2},
    # --- IMPORT ---
    ClassId.IMPORT_SIMPLE: {"name": "Import: Módulo completo", "level": Level.A1},
    ClassId.IMPORT_FROM_SIMPLE: {"name": "Import: Atributo específico", "level": Level.A1},
    ClassId.IMPORT_FROM_RELATIVE: {"name": "Import: Relativo", "level": Level.B1},
    ClassId.IMPORT_FROM_STAR: {"name": "Import: Comodín (*)", "level": Level.A2},
    ClassId.IMPORT_AS_EXTENSION: {"name": "Import: Alias (as)", "level": Level.A1},
    # --- MODULES ---
    ClassId.MODULES_STRUCT: {"name": "Mod: struct (Binary data)", "level": Level.B2},
    ClassId.MODULES_PICKLE: {"name": "Mod: pickle (Serialization)", "level": Level.B2},
    ClassId.MODULES_SHELVE: {"name": "Mod: shelve (Persistence)", "level": Level.B2},
    ClassId.MODULES_DBM: {"name": "Mod: dbm (Database)", "level": Level.B2},
    ClassId.MODULES_RE: {"name": "Mod: re (RegEx)", "level": Level.B1},
    ClassId.MODULES_IMPORTLIB: {"name": "Mod: importlib (Dynamic imports)", "level": Level.C1},
    # --- CLASS ---
    ClassId.CLASS_SIMPLE: {"name": "Class: Definición simple", "level": Level.B1},
    ClassId.CLASS_INHERITED: {"name": "Class: Herencia", "level": Level.B2},
    ClassId.CLASS_INIT: {"name": "Class: Constructor (__init__)", "level": Level.B1},
    ClassId.CLASS_DESCRIPTORS: {"name": "Class: Descriptores", "level": Level.C1},
    ClassId.CLASS_PROPERTIES: {"name": "Class: Propiedades (@property)", "level": Level.B2},
    ClassId.CLASS_PRIVATE: {"name": "Class: Atributos privados (__attr)", "level": Level.B2},
    # --- STATIC ---
    ClassId.STATIC_CLASSMETHOD: {"name": "Static: @classmethod", "level": Level.B2},
    ClassId.STATIC_STATICMETHOD: {"name": "Static: @staticmethod", "level": Level.B2},
    # --- DECORATORS ---
    ClassId.DECORATORS_FUNCTION: {"name": "Deco: Decorador de función", "level": Level.B2},
    ClassId.DECORATORS_CLASS: {"name": "Deco: Decorador de clase", "level": Level.C1},
    # --- METACLASS ---
    ClassId.METACLASS_NEW: {"name": "Meta: Método __new__", "level": Level.C2},
    ClassId.METACLASS_METACLASS: {"name": "Meta: Definición de Metaclase", "level": Level.C2},
    ClassId.METACLASS_ATTR_METACLASS: {"name": "Meta: Atributo __metaclass__", "level": Level.C2},
    # --- SUPERFUNCTION ---
    ClassId.SUPERFUNCTION_SIMPLE: {"name": "Super: Uso de super()", "level": Level.B2},
    # --- SLOTS ---
    ClassId.SLOTS_ATTR: {"name": "Slots: Optimización __slots__", "level": Level.C1},
    # --- ATTRIBUTES ---
    ClassId.ATTRIBUTES_SIMPLE: {"name": "Attr: Acceso a atributos", "level": Level.A2},
    ClassId.ATTRIBUTES_CLASS_REF: {"name": "Attr: Referencia __class__", "level": Level.C1},
    ClassId.ATTRIBUTES_DICT_REF: {"name": "Attr: Referencia __dict__", "level": Level.C1},
    # --- EXCEPTION ---
    ClassId.EXCEPTION_TRY_EXCEPT: {"name": "Exc: try-except", "level": Level.A2},
    ClassId.EXCEPTION_TRY_ELSE_EXCEPT: {"name": "Exc: try-except-else", "level": Level.B1},
    ClassId.EXCEPTION_TRY_TRY: {"name": "Exc: try-try anidado", "level": Level.B1},
    ClassId.EXCEPTION_TRY_FINALLY: {"name": "Exc: try-finally", "level": Level.B1},
    ClassId.EXCEPTION_TRY_EXCEPT_FINALLY: {"name": "Exc: try-except-finally", "level": Level.B1},
    ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY: {"name": "Exc: Flujo completo try", "level": Level.B2},
    ClassId.EXCEPTION_RAISE: {"name": "Exc: Lanzamiento (raise)", "level": Level.B1},
    ClassId.EXCEPTION_ASSERT: {"name": "Exc: Aserción (assert)", "level": Level.B1},
    # --- WITH ---
    ClassId.WITH_SIMPLE: {"name": "With: Context Manager", "level": Level.B1},
}


def get_class_level(class_id: ClassId) -> Level:
    """
    Retrieves the CEFR level associated with a given ClassId.
    Args:
        class_id (ClassId): The unique identifier of the code construct.
    Returns:
        Level: The CEFR level corresponding to the code construct.
    """
    details: Optional[ClassDetails] = CODE_CLASS_DETAILS.get(class_id)
    if details:
        return details["level"]
    return Level.UNKNOWN


def get_class_name(class_id: ClassId) -> str:
    """
    Retrieves the name associated with a given ClassId.
    Args:
        class_id (ClassId): The unique identifier of the code construct.
    Returns:
        str: The name corresponding to the code construct.
    """
    details: Optional[ClassDetails] = CODE_CLASS_DETAILS.get(class_id)
    if details:
        return details["name"]
    return ""
