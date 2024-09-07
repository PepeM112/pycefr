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
                self.assign_List()
                self.assign_Dict()                


    def assign_List(self):
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


    def assign_Dict(self):
        """Create object dictionary."""
        if (self.clase != "") and (self.level != ""):
            if self.dir_name not in self.myDataJson:
                self.myDataJson[self.dir_name] = {}

            if self.name not in self.myDataJson[self.dir_name]:
                self.myDataJson[self.dir_name][self.name] = []

            self.myDataJson[self.dir_name][self.name].append(
                {
                    "Class": str(self.clase),
                    "Start Line": str(self.node.lineno),
                    "End Line": str(self.node.end_lineno),
                    "Displacement": str(self.node.col_offset),
                    "Level": str(self.level),
                }
            )


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
        """Create and add data in the .json file."""
        with open("data.json", "w") as file:
            json.dump(self.myDataJson, file, indent=4)
