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
        self.write_data_json()


    def walk_tree(self):
        """Method iterating on the tree."""
        for self.node in ast.walk(self.tree):
            # Find attributes
            if type(self.node) == eval(self.attrib):
                self.level = ""
                self.clase = ""
                levels.asign_levels(self)
                self.to_json()              


    def to_json(self):
        """Create object dictionary with instance counting."""
        if self.clase == "" or self.level == "":
            return

        # Create list if not existing
        if "elements" not in self.myDataJsonNew:
            self.myDataJsonNew["elements"] = []
        
        entry_found = False
        # Search for entry of that class
        for entry in self.myDataJsonNew["elements"]:
            if entry["class"] == self.clase:
                entry["numberOfInstances"] += 1
                entry_found = True
                break

        # If not found add new entry
        if not entry_found:
            self.myDataJsonNew["elements"].append({
                "class": str(self.clase),
                "level": str(self.level),
                "numberOfInstances": 1
            })


    def write_data_json(self):
        with open("backend/tmp/data.json", "w") as file:
            json.dump(self.myDataJsonNew, file, indent=4)