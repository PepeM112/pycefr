import ast
import logging
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List

from backend.config.settings import settings
from backend.models.schemas.analysis import AnalysisClassPublic, AnalysisFilePublic, AnalysisPublic, AnalysisStatus
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Origin
from backend.services.analyzer.levels import get_class_from_ast_node

logger = logging.getLogger(__name__)


class Analyzer:
    """
    Core engine for analyzing Python source code files within a project.

    Attributes:
        root_path (str): The base directory path to analyze.
        is_cli (bool): Flag to enable console-specific output like progress bars.
        analysis_result (AnalysisPublic): The object storing gathered analysis data.
    """

    def __init__(self, root_path: str, is_cli: bool = True) -> None:
        """
        Initialize the Analyzer with a path and display settings.

        Args:
            root_path (str): The directory path to be scanned.
            is_cli (bool): If True, progress will be printed to stdout.
        """
        self.root_path = root_path
        self.is_cli = is_cli
        self.analysis_result = AnalysisPublic(
            id=0,
            name="",
            origin=Origin.LOCAL,
            status=AnalysisStatus.IN_PROGRESS,
            created_at=datetime.now(),
            file_classes=[],
        )
        self._file_count = 0
        self._processed_files = 0

    def analyse_project(self) -> None:
        """
        Walk through the project directory and perform AST analysis on all Python files.

        Raises:
            FileNotFoundError: If the root_path does not exist.
            ValueError: If the root_path is not a directory.
        """
        if self.is_cli:
            print("[ ] Analysing code", end=" ", flush=True)

        root_path = os.path.abspath(self.root_path)

        if not os.path.exists(root_path):
            raise FileNotFoundError(f"Path {root_path} does not exist")
        if not os.path.isdir(root_path):
            raise ValueError(f"Path {root_path} is not a directory")

        self._file_count = self._count_python_files(root_path)
        self._processed_files = 0

        self._analyse_directory(root_path)

        if self.is_cli:
            print("\r[✓] Analysing code\033[K")

        logger.info(f"Analysis completed for {root_path}")

    def _analyse_directory(self, path: str) -> None:
        """
        Recursively scan a directory for Python files to analyze.

        Args:
            path (str): The current directory path being scanned.
        """
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)

                if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
                    self._update_progress()
                    self._analyse_file(item_path)
                    self._processed_files += 1

                elif os.path.isdir(item_path):
                    if self._should_ignore(item_path):
                        continue
                    self._analyse_directory(item_path)

        except PermissionError:
            logger.error(f"Permission denied: {path}")
        except Exception as e:
            logger.error(f"Error reading directory {path}: {e}")

    def _update_progress(self) -> None:
        """
        Update and display the analysis progress bar or log message.
        """
        if self._file_count == 0:
            return

        percent = int((self._processed_files / self._file_count) * 100)

        if self.is_cli:
            bar_length = 40
            block = int(round(bar_length * self._processed_files / self._file_count))
            progress = "█" * block + "-" * (bar_length - block)
            print(f"\r[ ] Analysing code [{progress}] {percent}%\033[K", end="", flush=True)
        else:
            if self._processed_files % max(1, (self._file_count // 4)) == 0:
                logger.info(f"Analysis progress: {percent}%")

    def _analyse_file(self, file_path: str) -> None:
        """
        Read a file, parse its AST, and append the results to the analysis.

        Args:
            file_path (str): The absolute path of the Python file to analyze.
        """
        try:
            with open(file_path, encoding="utf-8") as fp:
                my_code = fp.read()
                relative_path = os.path.relpath(file_path, start=self.root_path)

                tree = ast.parse(my_code)
                file_classes = self._analyse_ast(tree)
                self.analysis_result.file_classes.append(
                    AnalysisFilePublic(filename=relative_path, classes=file_classes)
                )
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Could not analyse file {file_path}: {e}")

    def _analyse_ast(self, tree: ast.AST) -> List[AnalysisClassPublic]:
        """
        Walk through an AST tree to identify and count Python CEFR classes.

        Args:
            tree (ast.AST): The parsed AST of a file.

        Returns:
            List[AnalysisClassPublic]: A list of identified classes and their instance counts.
        """
        counter: defaultdict[ClassId, int] = defaultdict(int)
        for node in ast.walk(tree):
            class_id = get_class_from_ast_node(node)

            if class_id != ClassId.UNKNOWN:
                counter[class_id] += 1

        elements: List[AnalysisClassPublic] = []
        for class_id, count in counter.items():
            elements.append(
                AnalysisClassPublic(
                    class_id=class_id,
                    instances=count,
                )
            )
        elements.sort(key=lambda x: x.class_id.value)
        return elements

    def _should_ignore(self, path: str) -> bool:
        """
        Determine if a path should be ignored based on settings.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        ignore_folders = settings.ignore_folders
        path_norm = path.replace("\\", "/")

        for folder in ignore_folders:
            folder = folder.rstrip("/\\")
            if f"/{folder}/" in f"/{path_norm}/":
                return True
        return False

    def _count_python_files(self, directory: str) -> int:
        """
        Count total number of Python files in a directory for progress tracking.

        Args:
            directory (str): The root directory to start counting from.

        Returns:
            int: The total count of .py files.
        """
        count = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]
            count += sum(1 for f in files if f.endswith((".py", ".PY")))
        return count

    def get_results(self) -> AnalysisPublic:
        """
        Get the final analysis results.

        Returns:
            AnalysisPublic: The completed analysis data object.
        """
        return self.analysis_result

    @staticmethod
    def delete_tmp_files() -> None:
        """
        Remove the temporary directory used during analysis.

        Note:
            Logs an error if the directory cannot be deleted.
        """
        tmp_path = Path("backend/tmp")
        if tmp_path.exists():
            try:
                shutil.rmtree(tmp_path)
            except Exception as e:
                logger.error(f"Could not delete temporary directory {tmp_path}: {e}")
