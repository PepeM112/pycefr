"""
CLASS PROGRAM TO ITERATE ON THE TREE
"""

import ast
import csv
import json
import backend.scripts.levels as levels


class IterTree:
    """Class to iterate tree."""

    # CSV header
    myDataCsv = [
        [
            "Repository",
            "File Name",
            "Class",
            "Start Line",
            "End Line",
            "Displacement",
            "Level",
        ]
    ]

    # JSON dictionary
    myDataJson = {}
    myDataJsonNew = {}

    def __init__(self, tree, attrib, file, dir_name):
        """Class constructor."""
        self.tree = tree
        self.attrib = attrib
        self.name = file
        self.dir_name = dir_name
        self.walk_tree()
        self.write_data_csv()
        self.write_data_json()


    def walk_tree(self):
        """Method iterating on the tree."""
        for self.node in ast.walk(self.tree):
            # Find attributes
            if type(self.node) == eval(self.attrib):
                self.level = ""
                self.clase = ""
                levels.asign_levels(self)
                self.to_csv()
                self.to_json()              


    def to_csv(self):
        """Create object list."""
        if (self.clase != "") and (self.level != ""):
            self.list = [
                self.dir_name,
                self.name,
                self.clase,
                self.node.lineno,
                self.node.end_lineno,
                self.node.col_offset,
                self.level,
            ]

            self.myDataCsv.append(self.list)


    def to_json(self):
        """Create object dictionary with instance counting."""
        if self.clase == "" or self.level == "":
            return

        # Crear la lista global si no existe
        if "elements" not in self.myDataJsonNew:
            self.myDataJsonNew["elements"] = []
        
        found = False
        # Buscar si ya existe una entrada con la misma clase y nivel
        for entry in self.myDataJsonNew["elements"]:
            if entry["class"] == self.clase and entry["level"] == self.level:
                entry["numberOfInstances"] += 1
                found = True
                break

        # Si no se encontró, agregar un nuevo registro
        if not found:
            self.myDataJsonNew["elements"].append({
                "class": str(self.clase),
                "level": str(self.level),
                "numberOfInstances": 1
            })



    def write_data_csv(self, file_csv=""):
        """Create and add data in the .csv file."""
        if not file_csv:
            with open("data.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerows(self.myDataCsv)
        else:
            with open("data.csv", "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.list)


    def write_data_json(self):
        with open("backend/tmp/data.json", "w") as file:
            json.dump(self.myDataJsonNew, file, indent=4)