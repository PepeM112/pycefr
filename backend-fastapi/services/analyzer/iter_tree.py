"""
CLASS PROGRAM TO ITERATE ON THE TREE
"""

import ast
import json
from typing import Any, Dict

import backend.scripts.levels as levels


class IterTree:
    """Class to iterate tree."""

    # JSON dictionary
    my_data_json: Dict[str, Any] = {}
    my_data_json_new: Dict[str, Any] = {}

    def __init__(self, tree: ast.AST, attrib: str, relative_path: str) -> None:
        """Class constructor."""
        self.tree = tree
        self.attrib = attrib
        self.name = relative_path
        self.walk_tree()
        self.write_data_json()

    def walk_tree(self) -> None:
        """Method iterating on the tree."""
        for node in ast.walk(self.tree):
            self.node = node
            # Find attributes
            if isinstance(self.node, eval(self.attrib)):
                self.level = ""
                self.clase = ""
                levels.asign_levels(self)
                self.to_json()

    def to_json(self) -> None:
        """Create object dictionary with instance counting."""
        if self.clase == "" or self.level == "":
            return

        # Ensure 'elements' key exists
        if "elements" not in self.my_data_json_new:
            self.my_data_json_new["elements"] = {}

        # Ensure file entry exists in 'elements'
        if self.name not in self.my_data_json_new["elements"]:
            self.my_data_json_new["elements"][self.name] = []

        # Check if an entry for the current class and level exists
        entry_found = False
        for entry in self.my_data_json_new["elements"][self.name]:
            if entry["class"] == self.clase:
                entry["numberOfInstances"] += 1
                entry_found = True
                break

        # If not found, add a new entry
        if not entry_found:
            self.my_data_json_new["elements"][self.name].append(
                {"class": str(self.clase), "level": str(self.level), "numberOfInstances": 1}
            )

    def write_data_json(self) -> None:
        with open("backend/tmp/data.json", "w") as file:
            json.dump(self.my_data_json_new, file, indent=4)
