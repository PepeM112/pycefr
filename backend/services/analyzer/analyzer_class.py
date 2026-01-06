import ast
import json
import os
import sys
from collections import defaultdict
from typing import Any, Dict, List

from constants.analysis_rules import get_class_level
from models.schemas.analysis import AnalysisClass, AnalysisResult
from models.schemas.class_model import ClassId
from services.analyzer.levels import get_class_from_ast_node

DEFAULT_SETTINGS: Dict[str, Any] = {
    "ignoreFolders": ["node_modules/", ".git/", "__pycache__/"],
    "API-KEY": "",
    "addLocalSuffix": True,
    "autoDisplayConsole": True,
}


class Analyzer:
    def __init__(self, root_path: str) -> None:
        self.root_path = root_path
        self.settings: Dict[str, Any] = {}
        self.analysis_result: AnalysisResult = AnalysisResult(elements={})
        self._load_settings()

    def analyse_project(self) -> None:
        print("[ ] Analysing code", end=" ")
        root_path = os.path.abspath(self.root_path)

        if not os.path.exists(root_path):
            sys.exit(f"ERROR: Path {root_path} does not exist")
        if not os.path.isdir(root_path):
            sys.exit(f"ERROR: Path {root_path} is not a directory")

        file_count = self._count_python_files(root_path)

        self._analyse_directory(root_path, file_count)
        print("\r[✓] Analysing code" + " " * 50)

    def _analyse_directory(self, path: str, file_count: int = 0, current_file: int = 0) -> None:
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                # Item is a python file
                if os.path.isfile(item_path) and item.endswith(".py"):
                    self.print_progress(current_file + 1, file_count)
                    self._analyse_file(item_path)
                    current_file += 1
                # Item is a directory
                elif os.path.isdir(item_path):
                    if self._should_ignore(item_path):
                        continue

                    # Recursively analyse the directory if not ignored
                    self._analyse_directory(item_path, file_count, current_file)

        except FileNotFoundError:
            print(f"\nERROR: Directory {path} not found")
        except PermissionError:
            print(f"\nERROR: Permission denied to access {path}")
        except Exception:
            print(f"\nERROR: Couldn't read {path}")

    def _analyse_file(self, file_path: str) -> None:
        with open(file_path) as fp:
            my_code = fp.read()
            relative_path = os.path.relpath(file_path, start=self.root_path)
            try:
                tree = ast.parse(my_code)

                self.analysis_result.elements[relative_path] = self._analyse_ast(tree)
            except SyntaxError as e:
                print(f"\nERROR: Syntax error in file {file_path}: {e}")
                self.analysis_result.elements[relative_path] = []
                return

    def _analyse_ast(self, tree: ast.AST) -> List[AnalysisClass]:
        counter: defaultdict[ClassId, int] = defaultdict(int)
        for node in ast.walk(tree):
            class_id = get_class_from_ast_node(node)

            if class_id != ClassId.UNKNOWN:
                counter[class_id] += 1

        elements: List[AnalysisClass] = []
        for class_id, count in counter.items():
            elements.append(
                AnalysisClass(
                    class_id=class_id,
                    level=get_class_level(class_id),
                    instances=count,
                )
            )
        elements.sort(key=lambda x: x.class_id.value)
        return elements

    def _load_settings(self) -> None:
        if not os.path.isfile("settings.json"):
            with open("settings.json", "w") as file:
                json.dump(DEFAULT_SETTINGS, file, indent=4)
        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        self.settings["ignoreFolders"] = [folder.rstrip("/") for folder in self.settings.get("ignoreFolders", [])]

    @staticmethod
    def print_progress(current: int, total: int) -> None:
        """
        Print a simple progress bar in the console.

        Args:
            current: The current progress.
            total: The total amount of work.
        """
        percent = int((current / total) * 100)
        bar_length = 40
        block = int(round(bar_length * current / total))
        progress = "█" * block + "-" * (bar_length - block)
        print(f"\r[ ] Analysing code [{progress}] {percent}%", end="")

    def _should_ignore(self, path: str) -> bool:
        ignore_folders = self.settings.get("ignoreFolders", [])
        path_norm = path.replace("\\", "/")

        for folder in ignore_folders:
            folder = folder.rstrip("/\\")
            # Búsqueda más específica
            folder_with_sep = f"/{folder}/"
            if folder_with_sep in path_norm or path_norm.endswith(f"/{folder}"):
                return True

        return False

    def _count_python_files(self, directory: str) -> int:
        count = 0

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]

            count += sum(1 for f in files if f.endswith((".py", ".PY")))

        return count

    def get_results(self) -> AnalysisResult:
        return self.analysis_result
