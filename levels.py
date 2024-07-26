"""
PROGRAM FOR THE LEVELS OF EACH ATTRIBUTE
"""

import ast

# Level dictionary global variable
dict_level = ""

# List of loop elements: break, continue, pass, for, while
LIST_ELEM_LOOP = ["ast.Break", "ast.Continue", "ast.Pass", "ast.While", "ast.For"]
# List of imports
LIST_IMPORT = ["ast.Import", "ast.ImportFrom"]

# Read file with levels
with open("dicc.txt", "r") as dict_file:
    dict_text = dict_file.read()
    dict_level = eval(dict_text)


def levels(self):
    """
    Assign levels to various AST nodes based on their types.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.attrib == "ast.List":
        level_list(self)
    elif self.attrib == "ast.ListComp":
        level_list_comp(self)
    elif self.attrib == "ast.Dict":
        level_dict(self)
    elif self.attrib == "ast.DictComp":
        level_dict_comp(self)
    elif self.attrib == "ast.Tuple":
        level_tuple(self)
    elif self.attrib == "ast.Call":
        type_call(self)
    elif self.attrib == "ast.Assign":
        level_assign(self)
    elif self.attrib == "ast.AugAssign":
        level_assign(self)
    elif self.attrib == "ast.If":
        level_if(self)
    elif self.attrib == "ast.if_exp":
        level_if(self)
    elif self.attrib in LIST_ELEM_LOOP:
        type_elem_loop(self)
    elif self.attrib == "ast.FunctionDef":
        level_function_def(self)
    elif self.attrib == "ast.Return":
        level_return(self)
    elif self.attrib == "ast.Lambda":
        level_lambda(self)
    elif self.attrib == "ast.Yield":
        level_generator_functions(self)
    elif self.attrib == "ast.GeneratorExp":
        level_generator_expressions(self)
    elif self.attrib in LIST_IMPORT:
        level_module(self)
    elif self.attrib == "ast.ClassDef":
        level_class(self)
    elif self.attrib == "ast.Attribute":
        level_attribute(self)
        special_class_attributes(self)
    elif self.attrib == "ast.Name":
        type_name(self)
    elif self.attrib == "ast.Try":
        level_try(self)
    elif self.attrib == "ast.Raise":
        level_raise(self)
    elif self.attrib == "ast.Assert":
        level_assert(self)
    elif self.attrib == "ast.With":
        level_with(self)

def level_list(self):
    """
    Determine the level of a list.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_list = 0
    num_dict = 0
    # Check for nested lists
    if "ast.List" in str(self.node.elts):
        num_list = str(self.node.elts).count("ast.List")
        self.level = dict_level["List"][1]["nested"]
        self.clase = f"{num_list} Nested List"
    # Check for lists containing dictionaries
    elif "ast.Dict" in str(self.node.elts):
        num_dict = str(self.node.elts).count("ast.Dict")
        self.level = dict_level["List"][2]["with-dict"]
        self.clase = f"{num_dict} Dictionary List"
    else:
        self.level = dict_level["List"][0]["simple"]
        self.clase = "Simple List"

def level_list_comp(self):
    """
    Determine the level of a list comprehension.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_comp = 0
    if_exp = 0
    self.level = dict_level["ListComp"][0]["simple"]
    self.clase = "Simple List Comprehension"
    for i in range(len(self.node.generators)):
        num_comp += 1
        if self.node.generators[i].ifs:
            if_exp += 1
            self.level = dict_level["ListComp"][2]["with-if"]
            self.clase = f"List Comprehension with {if_exp} If statements"
        if num_comp > 1:
            self.level = dict_level["ListComp"][1]["nested"]
            self.clase = f"{num_comp} Nested List Comprehension"

def level_dict(self):
    """
    Determine the level of a dictionary.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_list = 0
    num_dict = 0
    # Check for nested dictionaries
    if "ast.Dict" in str(self.node.values):
        num_dict = str(self.node.values).count("ast.Dict")
        self.level = dict_level["Dict"][1]["nested"]
        self.clase = f"{num_dict} Nested Dictionary"
        # Check for lists inside dictionary dictionaries
        for i in range(len(self.node.values)):
            try:
                if "ast.List" in str(self.node.values[i].values):
                    num_list += str(self.node.values[i].values).count("ast.List")
                    self.level = dict_level["Dict"][3]["with-dict-list"]
                    self.clase = (
                        f"{num_list} List in {num_dict} Dictionary of Dictionary"
                    )
            except AttributeError:
                pass
    # Check for dictionaries containing lists
    elif "ast.List" in str(self.node.values):
        num_list = str(self.node.values).count("ast.List")
        self.level = dict_level["Dict"][2]["with-list"]
        self.clase = f"{num_list} List Dictionary"
    else:
        self.level = dict_level["Dict"][0]["simple"]
        self.clase = "Simple Dictionary"


def level_dict_comp(self):
    """
    Determine the level of a dictionary comprehension.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_ifs = 0
    if_exp = 0
    num_dictComp = 0

    # Check for if statements in comprehension
    for i in self.node.generators:
        num_ifs += str(i.ifs).count("ast.Compare")
        if num_ifs > 0:
            self.level = dict_level["DictComp"][1]["with-if"]
            self.clase = f"Dictionary Comprehension with {num_ifs} If statements"
        else:
            self.level = dict_level["DictComp"][0]["simple"]
            self.clase = "Simple Dictionary Comprehension"
    
    # Check for if expressions and nested comprehensions
    if "ast.if_exp" in str(self.node.value):
        if_exp += str(self.node.value).count("ast.if_exp")
        self.level = dict_level["DictComp"][2]["with-if-else"]
        self.clase = f"Dictionary Comprehension with {if_exp} if expression (If-Else)"
    elif "ast.DictComp" in str(self.node.value):
        num_dictComp += str(self.node.value).count("ast.DictComp")
        self.level = dict_level["DictComp"][3]["nested"]
        self.clase = f"{num_dictComp} Nested Dictionary Comprehension"


def level_tuple(self):
    """
    Determine the level of a tuple.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_tuple = 0

    # Check for nested tuples
    for i in self.node.elts:
        num_tuple += str(self.node.elts).count("ast.Tuple")
        if num_tuple > 0:
            self.level = dict_level["Tuple"][1]["nested"]
            self.clase = f"{num_tuple} Nested Tuple"
        else:
            self.level = dict_level["Tuple"][0]["simple"]
            self.clase = "Simple Tuple"


# List of file attributes
list_file_attr = ["write", "read", "readline", "writelines"]
# List of tools for loop coding
list_loop_coding = ["range", "zip", "map", "enumerate"]
# List of static class methods
list_static_class = ["staticmethod", "classmethod"]


def type_call(self):
    """
    Determine the type of function calls and delegate to specific level functions.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    value = ""
    if "ast.Attribute" in str(self.node.func):
        if self.node.func.attr in list_file_attr:
            value = self.node.func.attr
            level_files(self, value)
    elif "ast.Name" in str(self.node.func):
        if self.node.func.id == "open":
            value = "open"
            level_files(self, value)
        elif self.node.func.id == "print":
            value = "print"
            level_Print(self, value)
        elif self.node.func.id in list_loop_coding:
            value = self.node.func.id
            level_loop_coding(self, value)
        elif self.node.func.id in list_static_class:
            value = self.node.func.id
            level_static_class(self, value)
        elif self.node.func.id == "super":
            level_super_function(self)


def level_files(self, value):
    """
    Determine the level for file-related function calls.
    
    Args:
        self: Object containing the AST node and its attributes.
        value (str): The file-related function being called.
    """
    if value == "open":
        self.level = dict_level["File"][0]["open"]
        self.clase = "Files --> 'open' call function"
    elif value in list_file_attr:
        level = dict_level["File"]
        for i in range(1, len(level)):
            keys = dict_level["File"][i].keys()
            for k in keys:
                if k == value:
                    self.level = dict_level["File"][i][k]
                    self.clase = f"Files --> '{value}' call function"


def level_Print(self, value):
    """
    Determine the level for print function calls.
    
    Args:
        self: Object containing the AST node and its attributes.
        value (str): The function being called ('print').
    """
    self.level = dict_level["Print"][0]["simple"]
    self.clase = "Print"


def level_assign(self):
    """
    Determine the level for assignment operations.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    op = ""
    if self.attrib == "ast.Assign":
        self.level = dict_level["Assign"][0]["simple"]
        self.clase = "Simple Assignment"
        if "ast.BinOp" in str(self.node.value):
            self.level = dict_level["Assign"][1]["with-sum"]
            self.clase = "Assignment with sum (total = total + 1)"
    else:
        self.level = dict_level["Assign"][2]["increments"]
        if "ast.Add" in str(self.node.op):
            op = "increase amount"
        elif "ast.Sub" in str(self.node.op):
            op = "decrease subtraction"
        elif "ast.Mult" in str(self.node.op):
            op = "increase multiplication"
        self.clase = f"Simplified incremental Assignment with {op}"



def level_name_main(self):
    """
    Determine if the expression is `if __name__ == '__main__'`.
    
    Args:
        self: Object containing the AST node and its attributes.
        
    Returns:
        bool: True if the expression is `if __name__ == '__main__'`, otherwise False.
    """
    name = False
    eq = False
    constant = False
    
    if "ast.Compare" in str(self.node.test):
        if "ast.Name" in str(self.node.test.left) and self.node.test.left.id == "__name__":
            name = True
        if "ast.Eq" in str(self.node.test.ops):
            eq = True
        for i in self.node.test.comparators:
            if "ast.Constant" in str(i) and i.value == "__main__":
                constant = True
        if name and eq and constant:
            return True
    return False


def level_if(self):
    """
    Determine the level of if statements.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.attrib == "ast.If":
        self.level = dict_level["If-Statements"][0]["simple"]
        self.clase = "Simple If statements"
        if level_name_main(self):
            self.level = dict_level["If-Statements"][2]["__name__"]
            self.clase = "If statements using → __name__ == ‘__main__’"
    elif self.attrib == "ast.if_exp":
        self.level = dict_level["If-Statements"][1]["expression"]
        self.clase = "If statements expression (else)"


def type_elem_loop(self):
    """
    Determine the type of loop elements.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.attrib == "ast.While":
        level_while(self)
    elif self.attrib == "ast.Break":
        level_break(self)
    elif self.attrib == "ast.Continue":
        level_continue(self)
    elif self.attrib == "ast.Pass":
        level_pass(self)
    elif self.attrib == "ast.For":
        level_for(self)


def level_while(self):
    """
    Determine the level of while loops.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.node.orelse == []:
        self.clase = "While with Else Loop"
        self.level = dict_level["Loop"][4]["while-else"]
    else:
        self.clase = "Simple While Loop"
        self.level = dict_level["Loop"][3]["while-simple"]


def level_break(self):
    """
    Determine the level of break statements.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Loop"][0]["break"]
    self.clase = "'break' statement"


def level_continue(self):
    """
    Determine the level of continue statements.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Loop"][1]["continue"]
    self.clase = "'continue' statement"


def level_pass(self):
    """
    Determine the level of pass statements.
    
    Args:
        self: Object containing the AST node and sus attributes.
    """
    self.level = dict_level["Loop"][2]["pass"]
    self.clase = "'pass' statement"


def level_for(self):
    """
    Determine the level of for loops.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    num_for = 0
    num_list = 0
    num_tuple_for_iterator = 0
    num_tuple_for_target = 0
    
    self.level = dict_level["Loop"][5]["for-simple"]
    self.clase = "Simple For Loop"
    
    if "ast.For" in str(self.node.body):
        num_for += str(self.node.body).count("ast.For")
        self.level = dict_level["Loop"][6]["for-nested"]
        self.clase = f"{num_for} Nested For Loop"
    
    if "ast.Tuple" in str(self.node.target):
        num_tuple_for_target += str(self.node.target).count("ast.Tuple")
        self.level = dict_level["Loop"][7]["for-tuple-name"]
        self.clase = "For Loop with Tuple as name"
    
    if "ast.List" in str(self.node.iter):
        num_list += str(self.node.iter).count("ast.List")
        self.level = dict_level["Loop"][8]["for-list-iterate"]
        self.clase = f"For Loop with {num_list} List to iterate"
    elif "ast.Tuple" in str(self.node.iter):
        num_tuple_for_iterator += str(self.node.iter).count("ast.Tuple")
        self.level = dict_level["Loop"][9]["for-tuple-iterate"]
        self.clase = f"For Loop with {num_tuple_for_iterator} Tuples to iterate"


def level_loop_coding(self, value):
    """
    Determine the level of loop coding techniques.
    
    Args:
        self: Object containing the AST node and its attributes.
        value (str): The loop coding technique being used (e.g., 'range', 'zip').
    """
    if value == "range":
        self.level = dict_level["Loop"][10]["range"]
    elif value == "zip":
        self.level = dict_level["Loop"][11]["zip"]
    elif value == "map":
        self.level = dict_level["Loop"][12]["map"]
    elif value == "enumerate":
        self.level = dict_level["Loop"][13]["enumerate"]
    self.clase = f"'{value}' call function"


def level_function_def(self):
    """
    Determine the level of function definitions.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["FunctionDef"][0]["simple"]
    self.clase = "Function"
    
    # Classify according to the arguments passed
    level_def_arguments(self)
    
    # Check for recursive function
    level_recursive_function(self)
    
    # Check for decorators
    level_decorators(self, "Function")


def level_def_arguments(self):
    """
    Determine the level of arguments passed to functions.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.node.args.args:
        self.clase += " with Simple argument"
    if self.node.args.defaults:
        self.level = dict_level["FunctionDef"][1]["argum-default"]
        self.clase += " with Default argument"
    if self.node.args.vararg is not None:
        self.level = dict_level["FunctionDef"][2]["argum-*"]
        self.clase += " with * argument"
    if self.node.args.kwonlyargs:
        self.level = dict_level["FunctionDef"][4]["argum-keyword-only"]
        self.clase += " with Keyword-Only argument"
    if self.node.args.kwarg is not None:
        self.level = dict_level["FunctionDef"][3]["argum-**"]
        self.clase += " with ** argument"


def level_return(self):
    """
    Determine the level of return statements.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Return"][0]["simple"]
    self.clase = "Return"


def level_lambda(self):
    """
    Determine the level of lambda expressions.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Lambda"][0]["simple"]
    self.clase = "Lambda"


def level_recursive_function(self):
    """
    Determine if the function is recursive.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    for node in ast.walk(self.node):
        if isinstance(node, ast.Call):
            try:
                if node.func.id == self.node.name:
                    self.level = dict_level["FunctionDef"][5]["recursive"]
                    self.clase = "Recursive Functions"
            except AttributeError:
                pass


def level_generator_functions(self):
    """
    Determine the level of generator functions (using yield).
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Generators"][0]["function"]
    self.clase = "Generator Function (yield)"


def level_generator_expressions(self):
    """
    Determine the level of generator expressions.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Generators"][1]["expression"]
    self.clase = "Generator Expression"


def name_modules(self, name):
    """
    Determine the level for important modules.
    
    Args:
        self: Object containing the AST node and its attributes.
        name (list): List of module names.
    """
    # List of important modules
    LIST_MODULES = ["struct", "pickle", "shelve", "dbm", "re", "importlib"]

    for module_name in name:
        if module_name in LIST_MODULES:
            for level in dict_level["Modules"]:
                if module_name in level:
                    self.level = level[module_name]
                    self.clase += f" '{module_name}' module"


def level_as_extension(self):
    """
    Determine the level for 'as' extension in imports.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    for alias in self.node.names:
        if alias.asname is not None:
            self.level = dict_level["Import"][4]["as-extension"]
            self.clase += " with 'as' extension"


def level_from(self):
    """
    Determine the level for 'from' imports.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.node.level in (1, 2):
        self.level = dict_level["Import"][2]["from-relative"]
        self.clase = "Relative From"
    
    for alias in self.node.names:
        if alias.name == "*":
            self.level = dict_level["Import"][3]["from-*statements"]
            self.clase += " with *statements"


def level_module(self):
    """
    Determine the level for module imports.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    name_module = []
    
    if self.attrib == "ast.Import":
        self.level = dict_level["Import"][0]["import"]
        self.clase = "Import"
        for alias in self.node.names:
            name_module.append(alias.name)
    else:
        self.level = dict_level["Import"][1]["from-simple"]
        self.clase = "From"
        level_from(self)
        name_module.append(self.node.module)
    
    level_as_extension(self)
    name_modules(self, name_module)


def level_private_class(self):
    """
    Determine the level for private class methods and attributes.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    for funct in self.node.body:
        if funct.name.startswith("__") and not funct.name.endswith("__"):
            self.level = dict_level["Class"][5]["private"]
            self.clase += f" Private Methods {funct.name} of the class"
        
        for node in ast.walk(funct):
            if isinstance(node, ast.Attribute):
                if node.attr.startswith("__") and not node.attr.endswith("__"):
                    self.level = dict_level["Class"][5]["private"]
                    self.clase += f" Private Attributes {node.attr} of the class"


def level_constructor(self):
    """
    Determine the level of the constructor method (__init__).
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    for node in self.node.body:
        if node.name == "__init__":
            self.level = dict_level["Class"][2]["__init__"]
            self.clase += " Using the constructor method --> " + str(node.name)




def level_descriptors(self):
    """
    Determine the descriptor level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    # List of descriptors
    LIST_DESCRIPTORS = ["__get__", "__set__", "__delete__"]

    for elem in self.node.body:
        if elem.name in LIST_DESCRIPTORS:
            self.level = dict_level["Class"][3]["descriptors"]
            self.clase += " with Descriptors " + str(elem.name)


def level_properties(self):
    """
    Determine the properties level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    for node in self.node.body:
        for elem in ast.walk(node):
            if isinstance(elem, ast.Call):
                try:
                    if elem.func.id == "property":
                        self.level = dict_level["Class"][4]["properties"]
                        self.clase += " with Class Properties "
                except AttributeError:
                    pass


def level_class(self):
    """
    Determine the class level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Class"][0]["simple"]
    self.clase = "Simple Class "
    
    # Check for inherited class
    for base in self.node.bases:
        try:
            self.level = dict_level["Class"][1]["inherited"]
            self.clase = "Inherited Class from " + str(base.id)
        except AttributeError:
            pass
    
    # Check for properties
    level_properties(self)
    
    # Check for special methods and attributes in the class body
    for node in self.node.body:
        if isinstance(node, ast.FunctionDef):
            try:
                level_constructor(self)
                level_descriptors(self)
                level_private_class(self)
                level_metaclass(self, "function")
            except AttributeError:
                pass
    
    # Check for class decorators
    level_decorators(self, "Class")
    
    # Check for metaclasses in the class header
    level_metaclass(self, "header")




def level_attribute(self):
    """
    Determine the level of simple attributes.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Attributes"][0]["simple"]
    self.clase = "Simple Attribute"


def special_class_attributes(self):
    """
    Determine the level of special class attributes.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    # List of special attributes of classes
    LIST_CLASS_ATTRIBUTES = ["__class__", "__dict__"]

    if self.node.attr in LIST_CLASS_ATTRIBUTES:
        for level in dict_level["Attributes"][1:]:
            if self.node.attr in level:
                self.level = level[self.node.attr]
                self.clase = "Special Class Attribute " + str(self.node.attr)


def level_static_class(self, value):
    """
    Determine the level of static and class methods.
    
    Args:
        self: Object containing the AST node and its attributes.
        value (str): The type of method (static or class).
    """
    for level in dict_level["Static"]:
        if value in level:
            self.level = level[value]
            self.clase = value


def level_decorators(self, type):
    """
    Determine the level of decorators for functions and classes.
    
    Args:
        self: Object containing the AST node and its attributes.
        type (str): The type of the node ('Function' or 'Class').
    """
    for decorator in self.node.decorator_list:
        for level in dict_level["Decorators"]:
            if type in level:
                self.level = level[type]
                self.clase = "Decorator " + type


def type_name(self):
    """
    Determine the type of AST name.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    if self.node.id == "__metaclass__":
        level_metaclass(self, "attrib")
    elif self.node.id == "__slots__":
        level_slots(self)


def level_metaclass(self, pos):
    """
    Determine the metaclass level.
    
    Args:
        self: Object containing the AST node and its attributes.
        pos (str): The position or context of the metaclass ('function', 'header', or 'attrib').
    """
    if pos == "function":
        for node in self.node.body:
            if node.name == "__new__":
                for arg in node.args.args:
                    if arg.arg == "meta":
                        self.level = dict_level["Metaclass"][0]["__new__"]
                        self.clase += " Metaclass (3.X) created with --> __new__"
    elif pos == "header":
        for keyword in self.node.keywords:
            if keyword.arg == "metaclass":
                self.level = dict_level["Metaclass"][1]["metaclass"]
                self.clase += " Metaclass created in the class header --> 'metaclass = '" + keyword.value.id
    elif pos == "attrib":
        self.level = dict_level["Metaclass"][2]["__metaclass__"]
        self.clase = "Metaclass (2.X) created as attribute with --> __metaclass__"


def level_slots(self):
    """
    Determine the __slots__ level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Slots"][0]["__slots__"]
    self.clase = "Attribute statements __slots__"


def level_super_function(self):
    """
    Determine the level of the super built-in function.
    
    Args:
        self: Object containing the AST node and sues attributes.
    """
    self.level = dict_level["SuperFunction"][0]["simple"]
    self.clase = "Super Function"


def level_try(self):
    """
    Determine the try statement level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.clase = "Exception --> try"
    if any(isinstance(node, ast.Try) for node in self.node.body):
        self.level = dict_level["Exception"][2]["try/try"]
        self.clase += "/try"
    if self.node.handlers:
        self.level = dict_level["Exception"][0]["try/except"]
        self.clase += "/except"
    if self.node.orelse:
        self.level = dict_level["Exception"][1]["try/else/except"]
        self.clase += "/else"
    if self.node.finalbody:
        self.level = dict_level["Exception"][4]["try/except/finally"]
        self.clase += "/finally"


def level_raise(self):
    """
    Determine the raise statement level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Exception"][6]["raise"]
    self.clase = "'raise' exception"


def level_assert(self):
    """
    Determine the assert statement level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["Exception"][7]["assert"]
    self.clase = "'assert' exception"


def level_with(self):
    """
    Determine the with statement level.
    
    Args:
        self: Object containing the AST node and its attributes.
    """
    self.level = dict_level["With"][0]["simple"]
    self.clase = "With"
