import os
import json
from tabulate import tabulate
from collections import defaultdict

def read_data(file_path):
    """
    Read JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The parsed JSON data.
    """
    with open(file_path, "r") as file:
        return json.load(file)

def display_author_info(data):
    """
    Display author information in a formatted table.

    Args:
        data (dict): The JSON data containing commit and contributor information.
    """
    # Initialize a dictionary to combine data by github_user
    combined_commits_data = defaultdict(lambda: {
        'commits': 0,
        'total_hours': 0,
        'loc': 0,
        'total_files_modified': 0
    })
    
    # Extract commit information
    for commit in data['commits']:
        github_user = commit['github_user']
        combined_commits_data[github_user]['commits'] += commit['commits']
        combined_commits_data[github_user]['total_hours'] += commit['total_hours']
        combined_commits_data[github_user]['loc'] += commit['loc']
        combined_commits_data[github_user]['total_files_modified'] += commit['total_files_modified']
    
    # Extract contributor information
    contributors = data["contributors"]
    table = []
    for contributor in contributors:
        # Get commit data for the corresponding GitHub user
        commit_info = combined_commits_data.get(contributor["profile_url"].split('/')[-1], {})
        
        table.append(
            [
                contributor["name"],
                contributor.get('commits', 'N/A'),
                commit_info.get('total_hours', 'N/A'),
                commit_info.get('loc', 'N/A'),
                commit_info.get('total_files_modified', 'N/A')
            ]
        )
    
    headers = ["Author", "Commits", "Hours", "LOC", "Files Modified"]
    
    # Create the table with tabulate to calculate the width
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "center", "center", "center"))
    
    # Calculate the table width
    table_lines = table_str.split('\n')
    if table_lines:
        table_width = len(table_lines[0])
    else:
        table_width = 80  # Default value if the table is empty

    # Calculate totals
    total_commits = sum(row[1] if isinstance(row[1], int) else 0 for row in table)
    total_hours = sum(row[2] if isinstance(row[2], int) else 0 for row in table)
    total_loc = sum(row[3] if isinstance(row[3], int) else 0 for row in table)

    # Print the centered header
    print("\n|" + "-" * (table_width - 2) + "|")
    print("|" + "AUTHOR INFORMATION".center(table_width - 2, " ") + "|")
    print("|" + "-" * (table_width - 2) + "|")
    
    # Print the table with subheaders
    print(table_str)
    print("|" + "-" * (table_width - 2) + "|")
    
    # Print totals
    print(f"| Total commits".ljust(table_width - len(str(total_commits)) - 4) + f"  {total_commits:>{len(str(total_commits))}} |")
    print(f"| Total hours".ljust(table_width - len(str(total_hours)) - 4) + f"  {total_hours:>{len(str(total_hours))}} |")
    print(f"| Total loc".ljust(table_width - len(str(total_loc)) - 4) + f"  {total_loc:>{len(str(total_loc))}} |")
    print("|" + "-" * (table_width - 2) + "|")

def display_analysis(elements):
    """
    Display analysis data in a formatted table.

    Args:
        elements (list): A list of dictionaries containing element information.
    """
    # Compute totals per level
    totals = {}
    for element in elements:
        level = element["level"]
        number = element["numberOfInstances"]
        if level not in totals:
            totals[level] = 0
        totals[level] += number

    # Create table with elements
    table = []
    for element in elements:
        table.append(
            [
                element["class"],
                element["level"],
                element["numberOfInstances"],
            ]
        )
    
    headers = ["Element", "Level", "Number"]
    
    # Create the table with tabulate for calculating width
    table_str = tabulate(table, headers, tablefmt="pipe", colalign=("left", "center", "right"))

    # Calculate the table width
    table_lines = table_str.split('\n')
    if table_lines:
        table_width = len(table_lines[0])
    else:
        table_width = 80  # Default value if the table is empty

    # Print centered header
    print("\n|" + "-" * (table_width - 2) + "|")
    print("|" + "ANALYSIS".center(table_width - 2, " ") + "|")
    print("|" + "-" * (table_width - 2) + "|")
    
    # Print table with subheaders
    print(table_str)
    
    # Print totals
    max_total = max(totals.values(), default=0)
    print("|" + "-" * (table_width - 2) + "|")
    for level, total in sorted(totals.items()):
        print(f"| Total {level}".ljust(table_width - len(str(max_total)) - 2) + f"{total:>{len(str(max_total))}} |")
    print("|" + "-" * (table_width - 2) + "|")

def main(file_path):
    """
    Main function to read data and display tables.

    Args:
        file_path (str): The path to the JSON file.
    """
    data = read_data(file_path)
    display_analysis(data['elements'])
    print()
    if not file_path.endswith("_local.json"):
        display_author_info(data['repoInfo'])


if __name__ == "__main__":
    filePath = os.path.abspath('results/pycefr.json')
    main(filePath)
