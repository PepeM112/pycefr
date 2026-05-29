import json
import os
import sys
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from backend.models.schemas.analysis import AnalysisPublic
from backend.models.schemas.common import Level
from backend.models.schemas.repo import RepoPublic
from backend.services.analyzer.levels import get_default_class_level

_LEVEL_ANSI: dict[int, str] = {
    1: "\033[38;5;204m",  # A1 — pink
    2: "\033[38;5;208m",  # A2 — orange
    3: "\033[38;5;220m",  # B1 — yellow
    4: "\033[38;5;43m",  # B2 — teal
    5: "\033[38;5;39m",  # C1 — blue
    6: "\033[38;5;135m",  # C2 — purple
}
_RESET = "\033[0m"


def _colorize_levels(text: str) -> str:
    if not sys.stdout.isatty():
        return text
    for level_val, ansi in _LEVEL_ANSI.items():
        label = Level(level_val).name
        text = text.replace(f" {label} ", f" {ansi}{label}{_RESET} ")
    return text


def read_data(file_path: str) -> AnalysisPublic:
    """
    Read JSON data from a file and validate it.

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

        # Local analysis do not have id but is required by the model
        if not data.get("id"):
            data["id"] = 0

        return AnalysisPublic.model_validate(data)


def display_repo_summary(repo: RepoPublic) -> None:
    total_commits = sum(c.commits for c in repo.commits)
    total_hours = sum(c.estimated_hours for c in repo.commits)
    total_loc = sum(c.loc for c in repo.commits)

    min_width = 50
    rows: List[Tuple[str, Any]] = []

    if repo.name:
        rows.append(("Name:", repo.name))
    if repo.url:
        rows.append(("URL:", repo.url))
    if repo.description:
        rows.append(("Description:", repo.description))
    if repo.created_at:
        rows.append(("Created:", repo.created_at.strftime("%Y-%m-%d")))
    if repo.last_updated_at:
        rows.append(("Last updated:", repo.last_updated_at.strftime("%Y-%m-%d")))

    info_str = tabulate(rows, tablefmt="plain") if rows else ""
    info_lines = info_str.split("\n") if info_str else []

    stat_rows = [
        ["Contributors:", str(len(repo.contributors))],
        ["Total commits:", str(total_commits)],
        ["Estimated hours:", f"{total_hours:.1f}"],
        ["Total LOC:", str(total_loc)],
    ]
    stat_str = tabulate(stat_rows, tablefmt="plain", disable_numparse=True)
    stat_lines = stat_str.split("\n")

    all_content = info_lines + stat_lines
    width = max((len(line) + 4 for line in all_content), default=min_width)
    width = max(width, min_width)

    separator = "|" + "-" * (width - 2) + "|"

    print(f"\n{separator}")
    print("|" + "REPOSITORY SUMMARY".center(width - 2) + "|")
    print(separator)

    if info_lines:
        for line in info_lines:
            print("| " + line.ljust(width - 4) + " |")
        print(separator)

    for line in stat_lines:
        print("| " + line.ljust(width - 4) + " |")

    print(separator)


def _display_level_distribution(aggregated: Dict[Tuple[str, int], int], width: int) -> None:
    total = sum(aggregated.values())
    if total == 0:
        return

    counts_by_level: Dict[int, int] = defaultdict(int)
    for (_, level), count in aggregated.items():
        counts_by_level[level] += count

    pairs = [(1, 2), (3, 4), (5, 6)]
    max_count_len = max((len(str(counts_by_level[v])) for v in range(1, 7)), default=1)
    separator = "|" + "-" * (width - 2) + "|"

    print(separator)
    print("|" + "LEVEL DISTRIBUTION".center(width - 2) + "|")
    print(separator)

    for left_val, right_val in pairs:
        left_label = Level(left_val).name
        right_label = Level(right_val).name
        left_count = counts_by_level[left_val]
        right_count = counts_by_level[right_val]
        left_pct = (left_count / total * 100) if total else 0.0
        right_pct = (right_count / total * 100) if total else 0.0

        n = max_count_len
        left_cell = f"{left_label}: {left_count:>{n}} ({left_pct:>5.1f}%)"
        right_cell = f"{right_label}: {right_count:>{n}} ({right_pct:>5.1f}%)"
        row = f"  {left_cell}    {right_cell}"
        line = _colorize_levels("| " + row.ljust(width - 4) + " |")
        print(line)

    print(separator)


def _display_top_patterns(aggregated: Dict[Tuple[str, int], int], width: int) -> None:
    top10 = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)[:10]
    if not top10:
        return

    table = [[name, Level(level).name, count] for (name, level), count in top10]
    headers = ["Element", "Level", "Instances"]
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "right"))

    separator = "|" + "-" * (width - 2) + "|"

    # Pad each table line to box width before colorizing
    padded_lines = [line.ljust(width) for line in table_str.split("\n")]
    padded_str = "\n".join(padded_lines)

    print(separator)
    print("|" + "TOP PATTERNS".center(width - 2) + "|")
    print(separator)
    print(_colorize_levels(padded_str))
    print(separator)


def display_analysis(analysis: AnalysisPublic) -> None:
    """
    Display code analysis data in a formatted table grouped by levels.

    Args:
        analysis (AnalysisPublic): The analysis data to display.
    """
    aggregated: Dict[Tuple[str, int], int] = defaultdict(int)

    for f_class in analysis.file_classes:
        for cls in f_class.classes:
            name = cls.class_id.name
            level = get_default_class_level(cls.class_id)
            aggregated[(name, level)] += cls.instances

    if not aggregated:
        print("\nNo analysis data found in the file.")
        return

    table: List[List[Any]] = []
    totals_by_level: Dict[int, int] = defaultdict(int)

    sorted_items = sorted(aggregated.items(), key=lambda x: (x[0][1], x[0][0]))

    for (name, level), count in sorted_items:
        table.append([name, Level(level).name, count])
        totals_by_level[level] += count

    headers = ["Element", "Level", "Instances"]
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "right"))

    lines = table_str.split("\n")
    width = len(lines[0]) if lines else 80

    print("\n|" + "-" * (width - 2) + "|")
    print("|" + "PYTHON LEVEL ANALYSIS".center(width - 2, " ") + "|")
    print("|" + "-" * (width - 2) + "|")
    print(_colorize_levels(table_str))
    print("|" + "-" * (width - 2) + "|")

    for level, total in sorted(totals_by_level.items()):
        label = f"Total {Level(level).name}:"
        print(f"| {label.ljust(width - 11)} {str(total).rjust(6)} |")
    print("|" + "-" * (width - 2) + "|")

    _display_level_distribution(aggregated, width)
    _display_top_patterns(aggregated, width)


def display_footer() -> None:
    print("\n  See web for full results (insights, graphs, per-file breakdown).")


def main(file_path: str) -> None:
    """
    Main function to read data and display results.

    Args:
        file_path (str): The path to the JSON file.
    """
    try:
        data = read_data(file_path)

        if not data:
            print("\nCouldn't read analysis data from the file.")
            return

        display_analysis(data)

        if data.repo and (data.repo.commits or data.repo.contributors):
            display_repo_summary(data.repo)

        display_footer()

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")


if __name__ == "__main__":
    file_path = os.path.abspath("results/pycefr.json")
    main(file_path)
