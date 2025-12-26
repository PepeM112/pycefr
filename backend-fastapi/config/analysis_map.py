from models.class_model import ClassID
from models.common import Level

CODE_CLASS_DETAILS = {
    # --- LIST ---
    ClassID.LIST_SIMPLE: {"name": "List: Sintaxis Simple", "level": Level.A1},
    ClassID.LIST_NESTED: {"name": "List: Anidada", "level": Level.A2},
    ClassID.LIST_WITH_DICT: {"name": "List: Con Diccionario", "level": Level.B1},

    # --- LISTCOMP ---
    ClassID.LISTCOMP_SIMPLE: {"name": "ListComp: Simple", "level": Level.A2},
    ClassID.LISTCOMP_NESTED: {"name": "ListComp: Anidada", "level": Level.B1},
    ClassID.LISTCOMP_WITH_IF: {"name": "ListComp: Con Condicional", "level": Level.B1},

    # --- DICT ---
    ClassID.DICT_SIMPLE: {"name": "Dict: Sintaxis Simple", "level": Level.A2},
    ClassID.DICT_NESTED: {"name": "Dict: Anidado", "level": Level.B1},
    ClassID.DICT_WITH_LIST: {"name": "Dict: Con Lista", "level": Level.B1},
    ClassID.DICT_WITH_DICT_LIST: {"name": "Dict: Estructura Compleja", "level": Level.B2},

    # --- DICTCOMP ---
    ClassID.DICTCOMP_SIMPLE: {"name": "DictComp: Simple", "level": Level.B1},
    ClassID.DICTCOMP_WITH_IF: {"name": "DictComp: Con Condicional", "level": Level.B1},
    ClassID.DICTCOMP_WITH_IF_ELSE: {"name": "DictComp: Con If-Else", "level": Level.B1},
    ClassID.DICTCOMP_NESTED: {"name": "DictComp: Anidado", "level": Level.B2},

    # --- TUPLE ---
    ClassID.TUPLE_SIMPLE: {"name": "Tuple: Sintaxis Simple", "level": Level.A1},
    ClassID.TUPLE_NESTED: {"name": "Tuple: Anidada", "level": Level.A2},

    # --- FILE ---
    ClassID.FILE_OPEN: {"name": "File: Apertura (open)", "level": Level.A2},
    ClassID.FILE_WRITE: {"name": "File: Escritura (write)", "level": Level.A2},
    ClassID.FILE_WRITELINES: {"name": "File: Escritura Múltiple", "level": Level.B1},
    ClassID.FILE_READ: {"name": "File: Lectura Completa", "level": Level.A2},
    ClassID.FILE_READLINE: {"name": "File: Lectura por Línea", "level": Level.A2},

    # --- PRINT ---
    ClassID.PRINT_SIMPLE: {"name": "Print: Salida estándar", "level": Level.A1},

    # --- ASSIGN ---
    ClassID.ASSIGN_SIMPLE: {"name": "Assign: Simple", "level": Level.A1},
    ClassID.ASSIGN_WITH_SUM: {"name": "Assign: Con Operación", "level": Level.A1},
    ClassID.ASSIGN_INCREMENTS: {"name": "Assign: Incremento (+=)", "level": Level.A1},

    # --- IF-STATEMENTS ---
    ClassID.IF_SIMPLE: {"name": "If: Condicional Simple", "level": Level.A1},
    ClassID.IF_EXPRESSION: {"name": "If: Operador Ternario", "level": Level.A2},
    ClassID.IF_NAME_MAIN: {"name": "If: Script Entry Point (__main__)", "level": Level.A2},

    # --- LOOP ---
    ClassID.LOOP_BREAK: {"name": "Loop: Control break", "level": Level.A2},
    ClassID.LOOP_CONTINUE: {"name": "Loop: Control continue", "level": Level.A2},
    ClassID.LOOP_PASS: {"name": "Loop: Placeholder pass", "level": Level.A1},
    ClassID.LOOP_WHILE_SIMPLE: {"name": "Loop: While", "level": Level.A2},
    ClassID.LOOP_WHILE_ELSE: {"name": "Loop: While-Else", "level": Level.B1},
    ClassID.LOOP_FOR_SIMPLE: {"name": "Loop: For simple", "level": Level.A1},
    ClassID.LOOP_FOR_NESTED: {"name": "Loop: For anidado", "level": Level.A2},
    ClassID.LOOP_FOR_TUPLE_NAME: {"name": "Loop: For con desempaquetado", "level": Level.A2},
    ClassID.LOOP_FOR_LIST_ITERATE: {"name": "Loop: For sobre lista", "level": Level.A1},
    ClassID.LOOP_FOR_TUPLE_ITERATE: {"name": "Loop: For sobre tupla", "level": Level.A1},
    ClassID.LOOP_RANGE: {"name": "Loop: Uso de range()", "level": Level.A1},
    ClassID.LOOP_ZIP: {"name": "Loop: Uso de zip()", "level": Level.B1},
    ClassID.LOOP_MAP: {"name": "Loop: Uso de map()", "level": Level.B1},
    ClassID.LOOP_ENUMERATE: {"name": "Loop: Uso de enumerate()", "level": Level.A2},

    # --- FUNCTIONDEF ---
    ClassID.FUNC_SIMPLE: {"name": "Func: Definición simple", "level": Level.A2},
    ClassID.FUNC_ARGUM_DEFAULT: {"name": "Func: Argumentos por defecto", "level": Level.B1},
    ClassID.FUNC_ARGUM_STAR: {"name": "Func: Argumentos variables (*args)", "level": Level.B1},
    ClassID.FUNC_ARGUM_DBL_STAR: {"name": "Func: Argumentos clave (**kwargs)", "level": Level.B1},
    ClassID.FUNC_ARGUM_KEYWORD_ONLY: {"name": "Func: Keyword-only arguments", "level": Level.B2},
    ClassID.FUNC_RECURSIVE: {"name": "Func: Recursividad", "level": Level.B2},

    # --- RETURN ---
    ClassID.RETURN_SIMPLE: {"name": "Return: Retorno simple", "level": Level.A2},

    # --- LAMBDA ---
    ClassID.LAMBDA_SIMPLE: {"name": "Lambda: Funciones anónimas", "level": Level.B1},

    # --- GENERATORS ---
    ClassID.GEN_FUNCTION: {"name": "Gen: Función generadora (yield)", "level": Level.B2},
    ClassID.GEN_EXPRESSION: {"name": "Gen: Expresión generadora", "level": Level.B2},

    # --- IMPORT ---
    ClassID.IMPORT_SIMPLE: {"name": "Import: Módulo completo", "level": Level.A1},
    ClassID.IMPORT_FROM_SIMPLE: {"name": "Import: Atributo específico", "level": Level.A1},
    ClassID.IMPORT_FROM_RELATIVE: {"name": "Import: Relativo", "level": Level.B1},
    ClassID.IMPORT_FROM_STAR: {"name": "Import: Comodín (*)", "level": Level.A2},
    ClassID.IMPORT_AS_EXTENSION: {"name": "Import: Alias (as)", "level": Level.A1},

    # --- MODULES ---
    ClassID.MOD_STRUCT: {"name": "Mod: struct (Binary data)", "level": Level.B2},
    ClassID.MOD_PICKLE: {"name": "Mod: pickle (Serialization)", "level": Level.B2},
    ClassID.MOD_SHELVE: {"name": "Mod: shelve (Persistence)", "level": Level.B2},
    ClassID.MOD_DBM: {"name": "Mod: dbm (Database)", "level": Level.B2},
    ClassID.MOD_RE: {"name": "Mod: re (RegEx)", "level": Level.B1},
    ClassID.MOD_IMPORTLIB: {"name": "Mod: importlib (Dynamic imports)", "level": Level.C1},

    # --- CLASS ---
    ClassID.CLASS_SIMPLE: {"name": "Class: Definición simple", "level": Level.B1},
    ClassID.CLASS_INHERITED: {"name": "Class: Herencia", "level": Level.B2},
    ClassID.CLASS_INIT: {"name": "Class: Constructor (__init__)", "level": Level.B1},
    ClassID.CLASS_DESCRIPTORS: {"name": "Class: Descriptores", "level": Level.C1},
    ClassID.CLASS_PROPERTIES: {"name": "Class: Propiedades (@property)", "level": Level.B2},
    ClassID.CLASS_PRIVATE: {"name": "Class: Atributos privados (__attr)", "level": Level.B2},

    # --- STATIC ---
    ClassID.STATIC_CLASSMETHOD: {"name": "Static: @classmethod", "level": Level.B2},
    ClassID.STATIC_STATICMETHOD: {"name": "Static: @staticmethod", "level": Level.B2},

    # --- DECORATORS ---
    ClassID.DECO_FUNCTION: {"name": "Deco: Decorador de función", "level": Level.B2},
    ClassID.DECO_CLASS: {"name": "Deco: Decorador de clase", "level": Level.C1},

    # --- METACLASS ---
    ClassID.META_NEW: {"name": "Meta: Método __new__", "level": Level.C2},
    ClassID.META_METACLASS: {"name": "Meta: Definición de Metaclase", "level": Level.C2},
    ClassID.META_ATTR_METACLASS: {"name": "Meta: Atributo __metaclass__", "level": Level.C2},

    # --- SUPERFUNCTION ---
    ClassID.SUPER_SIMPLE: {"name": "Super: Uso de super()", "level": Level.B2},

    # --- SLOTS ---
    ClassID.SLOTS_ATTR: {"name": "Slots: Optimización __slots__", "level": Level.C1},

    # --- ATTRIBUTES ---
    ClassID.ATTR_SIMPLE: {"name": "Attr: Acceso a atributos", "level": Level.A2},
    ClassID.ATTR_CLASS_REF: {"name": "Attr: Referencia __class__", "level": Level.C1},
    ClassID.ATTR_DICT_REF: {"name": "Attr: Referencia __dict__", "level": Level.C1},

    # --- EXCEPTION ---
    ClassID.EXC_TRY_EXCEPT: {"name": "Exc: try-except", "level": Level.A2},
    ClassID.EXC_TRY_ELSE_EXCEPT: {"name": "Exc: try-except-else", "level": Level.B1},
    ClassID.EXC_TRY_TRY: {"name": "Exc: try-try anidado", "level": Level.B1},
    ClassID.EXC_TRY_FINALLY: {"name": "Exc: try-finally", "level": Level.B1},
    ClassID.EXC_TRY_EXCEPT_FINALLY: {"name": "Exc: try-except-finally", "level": Level.B1},
    ClassID.EXC_TRY_EXCEPT_ELSE_FINALLY: {"name": "Exc: Flujo completo try", "level": Level.B2},
    ClassID.EXC_RAISE: {"name": "Exc: Lanzamiento (raise)", "level": Level.B1},
    ClassID.EXC_ASSERT: {"name": "Exc: Aserción (assert)", "level": Level.B1},

    # --- WITH ---
    ClassID.WITH_SIMPLE: {"name": "With: Context Manager", "level": Level.B1},
}
