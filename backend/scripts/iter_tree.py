"""
CLASS PROGRAM TO ITERATE ON THE TREE
"""

import ast
import json
import backend.scripts.levels as levels


class IterTree:
    """Class to iterate tree."""

    # JSON dictionary
    myDataJson = {}
    myDataJsonNew = {}

    def __init__(self, tree, attrib, relative_path):
        """Class constructor."""
        self.tree = tree
        self.attrib = attrib
        self.name = relative_path
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

        # Ensure 'elements' key exists
        if "elements" not in self.myDataJsonNew:
            self.myDataJsonNew["elements"] = {}

        # Ensure file entry exists in 'elements'
        if self.name not in self.myDataJsonNew["elements"]:
            self.myDataJsonNew["elements"][self.name] = []

        # Check if an entry for the current class and level exists
        entry_found = False
        for entry in self.myDataJsonNew["elements"][self.name]:
            if entry["class"] == self.clase:
                entry["numberOfInstances"] += 1
                entry_found = True
                break

        # If not found, add a new entry
        if not entry_found:
            self.myDataJsonNew["elements"][self.name].append({
                "class": str(self.clase),
                "level": str(self.level),
                "numberOfInstances": 1
            })


    def write_data_json(self):
        with open("backend/tmp/data.json", "w") as file:
            json.dump(self.myDataJsonNew, file, indent=4)