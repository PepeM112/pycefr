from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ast
import json
import shlex
import subprocess
import requests
import argparse
from backend.scripts.ClassIterTree import IterTree
from scripts.getjson import read_Json
from scripts.getcsv import read_FileCsv
from urllib.parse import urlparse

# Lists with attributes
LITERALS = ["ast.List", "ast.Tuple", "ast.Dict"]
VARIABLES = ["ast.Name"]
EXPRESSIONS = ["ast.Call", "ast.IfExp", "ast.Attribute"]
COMPREHENSIONS = ["ast.ListComp", "ast.GeneratorExp", "ast.DictComp"]
STATEMENTS = ["ast.Assign", "ast.AugAssign", "ast.Raise", "ast.Assert", "ast.Pass"]
IMPORTS = ["ast.Import", "ast.ImportFrom"]
CONTROL_FLOW = [
    "ast.If",
    "ast.For",
    "ast.While",
    "ast.Break",
    "ast.Continue",
    "ast.Try",
    "ast.With",
]
CLASS_FUNCTIONS = [
    "ast.FunctionDef",
    "ast.Lambda",
    "ast.Return",
    "ast.Yield",
    "ast.ClassDef",
]

# Define final list
ATTRIBUTES = [
    LITERALS,
    VARIABLES,
    EXPRESSIONS,
    COMPREHENSIONS,
    STATEMENTS,
    IMPORTS,
    CONTROL_FLOW,
    CLASS_FUNCTIONS,
]

REPO_URL = ""
REPO_NAME = ""
API_KEY = ""

def request_url(url):
    """
    Handle a repository URL by splitting it, checking its validity, and analyzing its language response.

    Args:
        url: The URL of the repository to be analyzed.

    Raises:
        SystemExit:
            If the URL is incorrectly formatted. For option -r (repository URL), use:
            https://github.com/USER/REPO.git
            If the URL does not use the 'https' protocol.
            If the URL is not from 'github.com'.
            If the repository does not meet the language criteria.
    """
    global REPO_URL, REPO_NAME, API_KEY
    API_KEY = get_api_token()
    # Parse the repository URL
    print("Validating URL\t\t[ ]", end="")
    parsed_url = urlparse(url)

    if parsed_url.scheme != 'https':
        sys.exit("ERROR: URL must use the 'https' protocol.")
    if parsed_url.netloc != 'github.com':
        sys.exit("ERROR: URL must  be from 'github.com'.")

    path_segments = parsed_url.path.strip('/').split('/')
    user_name = path_segments[0]
    REPO_NAME = path_segments[1].replace(".git", "")
    
    REPO_URL = url

    if not path_segments:
        sys.exit(
            "ERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO.git"
        )

    if not is_python_language(parsed_url.scheme, parsed_url.netloc, user_name, REPO_NAME):
        sys.exit("ERROR: The repository does not contain at least 50% of Python.")
    
    print("\rValidating URL\t\t[✓]")
    print("Cloning repository\t[ ]", end="")
    cloned_repo = clone_repo(REPO_URL)
    print("\rCloning repository\t[✓]")
    print("Code analysis\t\t[ ]", end="")
    # Count number of files
    file_count = 0
    for root, dirs, files in os.walk(cloned_repo):
        for file in files:
            if file.endswith(".py"):
                file_count += 1
    
    current_file = [0]
    analyse_directory(cloned_repo, cloned_repo.split("/")[-1], file_count, current_file)
    print("\n\rCode analysis\t\t[✓]")
    repo_info = get_repo_data(user_name, REPO_NAME)
    print("Saving data\t\t[ ]", end="")
    save_data(repo_info)
    print("\rSaving data\t\t[✓]")
    print("Success")



def is_python_language(protocol, type_git, user_name, repo_name):
    """
    Check if the repository's primary language is Python and if it constitutes at least 50% of the code.

    Args:
        protocol: The protocol part of the URL.
        type_git: The domain part of the URL.
        user_name: The GitHub username.
        repo_name: The repository name.

    Returns:
        bool: True is repo contains enough Python, False otherwise

    Raises:
        SystemExit: If the repository does not meet the language criteria.
    """
    repo_url = f"{protocol}://api.{type_git}/repos/{user_name}/{repo_name}/languages"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    # Decode JSON response into a Python dict:
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 403:
        print("You've reached the limit of API calls. You can further continue by adding a personal access token or by loging in GitHub")
    elif response.status_code != 200:
        sys.exit(f"ERROR validating language [{response.status_code}]")
    # Calculate total elements and check Python presence
    total_elem = sum(response.json().values())
    python_quantity = response.json().get("Python", 0)

    return python_quantity >= total_elem / 2


def clone_repo(url):
    """
    Clone the repository from the provided URL.

    Args:
        url: The URL of the repository to be cloned.

    Returns:
        str: The absolute path to the directory where the repository has been cloned.
    """
    clone_dir = os.path.join(os.path.dirname(__file__), "tmp")
    clone_path = os.path.join(clone_dir, REPO_NAME)

    # Delete folder if already exists
    if os.path.exists(clone_dir):
        subprocess.call(["rm", "-rf", clone_dir])

    os.makedirs(clone_dir)

    command_line = shlex.split(f"git clone {url} {clone_path}")

    # Redirigir la salida estándar y la salida de errores a subprocess.PIPE
    subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    return clone_path



def run_user(user):
    """
    Analyze the repositories of a specified GitHub user.

    Args:
        user: The GitHub username.

    Raises:
        SystemExit: If the user is not found or if the repositories cannot be analyzed.
    """
    # Create the URL of the API
    user_url = "https://api.github.com/users/" + user
    print(user_url)
    print("Analyzing user...\n")
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    try:
        # Extract headers
        response = requests.get(user_url, headers=headers)
        response.raise_for_status()
        # Decode JSON response into a Python dict:
        response = response.json()
        # Get repository URL
        repo_url = response["repos_url"]
    except requests.exceptions.HTTPError:
        sys.exit(f"ERROR: User '{user}' not found. Please check the username.")
    except KeyError:
        sys.exit("ERROR: Unable to retrieve repository information for the user.")
    except Exception as e:
        sys.exit(f"ERROR: An unexpected error occurred: {e}")

    print("Analyzing repositories...\n")
    # Extract repository names
    try:
        names = requests.get(repo_url, headers=headers)
        names.raise_for_status()
        # Decode JSON response into a Python dict:
        response = names.json()
        # Show repository names
        for repository in response:
            print("\nRepository: " + str(repository["name"]))
            is_python_language("https", "github.com", user, repository["name"])
    except requests.exceptions.HTTPError:
        sys.exit(
            "ERROR: Unable to retrieve repositories. Check if the user has any public repositories."
        )


def analyse_directory(path, dir_name, total_length, current_file):
    """
    Recursively search the directory for Python files and process them.

    Args:
        path: The absolute path to the directory.
        dir_name: The name of the current directory being processed.
        system.
        total_length: Number of files inside the directory.
        current_file: Number of files already checked from the root path.
    """
    try:
        # List all items in the directory
        items = os.listdir(path)
        # Process each item
        for item in items:
            item_path = os.path.join(path, item)
            # Check if the item is a python file"
            if os.path.isfile(item_path) and item.endswith(".py"):
                print_progress(current_file[0] + 1, total_length)
                analyse_file(item_path, dir_name)
                current_file[0] += 1
            # Check if the item is a directory
            elif os.path.isdir(item_path):
                analyse_directory(item_path, item, total_length, current_file)
    except FileNotFoundError:
        print(f"Directory {path} not found")
    except PermissionError:
        print(f"Permission denied to access {path}")


def analyse_file(path, dir_name):
    """
    Read a Python file and parse it into an abstract syntax tree (AST).

    Args:
        path: The path to the Python file.
        dir_name: The name of the current directory being processed.
    """
    with open(path) as fp:
        my_code = fp.read()
        try:
            tree = ast.parse(my_code)
            # Iterate through and process every attribute
            for attribute_list in ATTRIBUTES:
                for attribute in attribute_list:
                    file = path.split("/")[-1]
                    IterTree(tree, attribute, file, dir_name)
        except SyntaxError:
            print("There is a syntax error in the code")
            pass


def print_progress(current, total):
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
    print(f"\r[{progress}] {percent}%", end="")


def get_repo_data(owner, repo):
    print("Processed commits\t[ ]", end="")
    sys.stdout.flush() 
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    # COMMITS INFO
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, params={'per_page': 100, 'page': 1}, headers=headers)

    if response.status_code != 200:
        print(f"Warning: there was an error retrieving commits information [{response.status_code}]")
        return

    response_json = response.json()

    total_commits = int(response.headers.get('X_Total_Count', 0))
    
    files_set = set()
    total_loc = 0
    commit_dates = []

    for commit in response_json:
        commit_response = requests.get(commit['url'], headers=headers).json()

        # Number of files modified
        files = commit_response.get('files', [])
        for file in files:
            files_set.add(file['filename'])

        # LOC
        stats = commit_response.get('stats', {})
        total_loc += stats.get('additions', 0) + stats.get('deletions', 0)

        # Commit dates
        commit_date = commit_response['commit']['committer']['date']
        commit_timestamp = datetime.fromisoformat(commit_date.replace('Z', '+00:00')).timestamp()
        commit_dates.append(commit_timestamp)

    total_files_modified = len(files_set)
    total_hours = calculate_hours_spent(commit_dates)
    print("\rProcessed commits\t[✓]")

    # CONTRIBUTORS INFO
    print("Fetched contributors\t[]", end="")
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Warning: there was an error retrieving contributors information [{response.status_code}]")
        return

    response_json = response.json()

    contributors = []
    for contributor in response_json:
        author = {
            'name': contributor['login'],
            'commits': contributor['contributions']   
        }
        contributors.append(author)
    print("\rFetched contributors\t[✓]")
    return {
        'total_commits': total_commits,
        'total_loc': total_loc,
        'total_files_modified': total_files_modified,
        'total_hours': total_hours,
        'contributors': contributors
    }


def calculate_hours_spent(commit_dates, max_commit_diff_seconds=120*60, first_commit_addition_seconds=120*60):
    """
    Convert a list of commit timestamps (in seconds since epoch) to an estimate of hours spent.

    Args:
        commit_dates: List of commit timestamps in seconds since epoch (e.g., [1609459200.0, ...])
        max_commit_diff_seconds: Maximum allowed time difference between commits to be considered continuous work (in seconds)
        first_commit_addition_seconds: Time added for the first commit (in seconds)

    Returns: 
        Estimated hours spent
    """
    if len(commit_dates) < 2:
        return first_commit_addition_seconds / 3600

    # Sort times and compute differences
    commit_dates.sort()
    time_diffs = [commit_dates[i] - commit_dates[i-1] for i in range(1, len(commit_dates))]

    # Filter out differences longer than max_commit_diff_seconds
    continuous_time_diffs = [diff for diff in time_diffs if diff <= max_commit_diff_seconds]

    # Sum up the continuous time differences and add the first commit addition
    total_seconds = sum(continuous_time_diffs) + first_commit_addition_seconds

    return round(total_seconds / 3600)  # Convert seconds to hours



def save_data(repo_data):
    try:
        with open("backend/tmp/data.json", "r") as file:
            data = json.load(file)    
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find data file")

    data.update({"repoInfo": repo_data})

    os.makedirs("backend/data", exist_ok=True)

    output_file = f"backend/data/{REPO_NAME}.json"

    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)


def get_api_token():
    try:
        with open("backend/config/personal.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find personal.json")

    return data.get("API-KEY", "")

def main():
    """
    Main function to handle command-line arguments and invoke appropriate actions.
    """
    parser = argparse.ArgumentParser(description="Process options.")
    parser.add_argument("-d", "--directory", type=str, help="Path to the directory")
    parser.add_argument("-r", "--repo", type=str, help="Repository URL")
    parser.add_argument("-u", "--user", type=str, help="User identifier")

    args = parser.parse_args()

    if args.directory:
        analyse_directory(args.directory, args.directory.split("/")[-1])
    elif args.repo:
        request_url(args.repo)
    elif args.user:
        run_user(args.user)
    else:
        parser.print_help()
        sys.exit("Usage: python3 pycerfl.py [-d directory | -r repo | -u user]")


if __name__ == "__main__":
    main()
