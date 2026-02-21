import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from backend.models.schemas.analysis import AnalysisPublic
from backend.models.schemas.repo import RepoPublic
from backend.services.analyzer.levels import get_default_class_level


def read_data(file_path: str) -> AnalysisPublic:
    """
    Read JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        AnalysisPublic: The parsed JSON data as an AnalysisPublic object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Couldn't find file '{file_path.replace('results/', '')}'.")

    with open(file_path, "r") as file:
        data = json.load(file)
        print(data)

        # Local analysis do not have id but is required by the model
        if not data.get("id"):
            data["id"] = 0

        return AnalysisPublic.model_validate(data)


def display_author_info(repo: RepoPublic) -> None:
    """
    Display author information in a formatted table.

    Args:
        repo (RepoPublic): The repository data containing commit and contributor information.
    """
    # Map commits by user to cross-reference with contributors
    stats_map = {c.github_user: c for c in repo.commits}

    table: List[List[Any]] = []
    for contributor in repo.contributors:
        s = stats_map.get(contributor.github_user)

        table.append(
            [
                contributor.name or contributor.github_user,
                s.commits if s else 0,
                f"{s.estimated_hours:.1f}" if s else "0.0",
                s.loc if s else 0,
                s.total_files_modified if s else 0,
            ]
        )

    if not table:
        return

    headers = ["Author", "Commits", "Hours", "LOC", "Files Modified"]
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "center", "center", "center"))
    width = len(table_str.split("\n")[0])

    print("\n|" + "-" * (width - 2) + "|")
    print("|" + "AUTHOR INFORMATION".center(width - 2, " ") + "|")
    print("|" + "-" * (width - 2) + "|")
    print(table_str)


def display_analysis(analysis: AnalysisPublic) -> None:
    """
    Display analysis data in a formatted table.

    Args:
        analysis (AnalysisPublic): The analysis data to display.

        information.
    """
    # Aggregate data across all files
    aggregated: Dict[Tuple[str, int], int] = defaultdict(int)

    # Navegación correcta por los objetos Pydantic
    for f_class in analysis.file_classes:
        for cls in f_class.classes:
            # Acceso directo a atributos del objeto ClassId
            name = cls.class_id.name
            level = get_default_class_level(cls.class_id)
            aggregated[(name, level)] += cls.instances

    if not aggregated:
        print("\nNo analysis data found in the file.")
        return

    table: List[List[Any]] = []
    totals_by_level: Dict[str, int] = defaultdict(int)

    # Ordenamos por Level and then by Name
    sorted_items = sorted(aggregated.items(), key=lambda x: (x[0][1], x[0][0]))

    for (name, level), count in sorted_items:
        table.append([name, level, count])
        totals_by_level[str(level)] += count

    headers = ["Element", "Level", "Instances"]
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "right"))

    # Compute width based on the first line of the table for consistent formatting
    lines = table_str.split("\n")
    width = len(lines[0]) if lines else 80

    print("\n|" + "-" * (width - 2) + "|")
    print("|" + "PYTHON LEVEL ANALYSIS".center(width - 2, " ") + "|")
    print("|" + "-" * (width - 2) + "|")
    print(table_str)
    print("|" + "-" * (width - 2) + "|")

    for level, total in sorted(totals_by_level.items()):
        label = f"Total Level {level}:"
        print(f"| {label.ljust(width - 11)} {str(total).rjust(6)} |")
    print("|" + "-" * (width - 2) + "|")


def main(file_path: str) -> None:
    """
    Main function to read data and display tables.

    Args:
        file_path (str): The path to the JSON file.
    """
    try:
        data = read_data(file_path)

        if data:
            display_analysis(data)
        else:
            print("\nCouldn't read analysis data from the file.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")


if __name__ == "__main__":
    file_path = os.path.abspath("results/pycefr.json")
    main(file_path)
