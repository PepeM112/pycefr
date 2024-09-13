from genericpath import isdir
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ast
import json
import shlex
import shutil
import subprocess
import requests
from backend.scripts.ClassIterTree import IterTree
from datetime import datetime
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
USER_NAME = ""
API_KEY = ""
SETTINGS = {}


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
    validate_repo_url(url)

    cloned_repo = clone_repo(REPO_URL)

    analyse_project(cloned_repo)
    remove_dir(cloned_repo)

    repo_info = get_repo_data()
    save_data(repo_info)

    print("\nDone.")


def remove_dir(path):
    if not os.path.isdir(path):
        print(f"ERROR: Not a directory")
        return
    if not os.path.isabs(path) or not os.path.exists(path):
        print(f"ERROR: The directory does not exist: {path}")
        return

    try:
        shutil.rmtree(path)
    except Exception as e:
        print(f"ERROR: Couldn't remove directory {path}: {e}")



def validate_repo_url(url):
    global REPO_URL, REPO_NAME, USER_NAME, API_KEY
    API_KEY = get_api_token()
    
    print("[ ] Validating URL", end="")
    parsed_url = urlparse(url)

    if parsed_url.scheme != 'https':
        sys.exit("\nERROR: URL must use the 'https' protocol.")
    if parsed_url.netloc != 'github.com':
        sys.exit("\nERROR: URL must  be from 'github.com'.")

    path_segments = parsed_url.path.strip('/').split('/')
    USER_NAME = path_segments[0]
    REPO_NAME = path_segments[1].replace(".git", "")
    
    REPO_URL = url

    if not path_segments:
        sys.exit(
            "\nERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO.git"
        )

    if not is_python_language(parsed_url.scheme, parsed_url.netloc):
        sys.exit("\nERROR: The repository does not contain at least 50% of Python.")
    
    print("\r[✓] Validating URL")


def is_python_language(protocol, type_git):
    """
    Check if the repository's primary language is Python and if it constitutes at least 50% of the code.

    Args:
        protocol: The protocol part of the URL.
        type_git: The domain part of the URL.

    Returns:
        bool: True is repo contains enough Python, False otherwise

    Raises:
        SystemExit: If the repository does not meet the language criteria.
    """
    repo_url = f"{protocol}://api.{type_git}/repos/{USER_NAME}/{REPO_NAME}/languages"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    # Decode JSON response into a Python dict:
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 403:
        print("You've reached the limit of API calls. You can further continue by adding a personal access token or by loging in GitHub")
    elif response.status_code == 404:
        sys.exit(f"ERROR: Repository doesn't exist [{response.status_code}]")
    elif response.status_code != 200:
        sys.exit(f"ERROR: Couldn't validate Python language [{response.status_code}]")
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
    print("[ ] Cloning repository", end="")
    clone_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'tmp') # ...backend/tmp
    clone_path = os.path.join(clone_dir, REPO_NAME)

    # Delete folder if already exists
    if os.path.exists(clone_dir):
        subprocess.call(["rm", "-rf", clone_dir])

    os.makedirs(clone_dir)

    command_line = shlex.split(f"git clone {url} {clone_path}")

    # Redirigir la salida estándar y la salida de errores a subprocess.PIPE
    subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    print("\r[✓] Cloning repository")
    return clone_path



def run_user(user):
    """
    Analyze the repositories of a specified GitHub user.

    Args:
        user: The GitHub username.

    Raises:
        SystemExit: If the user is not found or if the repositories cannot be analyzed.
    """
    global API_KEY
    API_KEY = get_api_token()
    user_data = fetch_user(user)

    if not bool(user_data.get('public_repos')):
        print(f"The user { user } has no repositories to analyze")
        return

    user_repos = fetch_user_repos(user)

    print(f"{user} has {len(user_repos)} public repositories:")
    
    for index, repo in enumerate(user_repos, start=1):
        print(f"  [{index}] {repo.get('name')}")

    repo_url = choose_repo(user_repos)

    request_url(repo_url)    


def fetch_user(user):
    """
    Fetch data for a given GitHub user.

    This function sends a request to the GitHub API to retrieve data for the specified user.

    Args:
        user (str): The GitHub username to fetch data for.

    Returns:
        dict: A dictionary containing the user's information if the request is successful.

    Raises:
        SystemExit: If the user is not found, or if there is an issue with authentication or the request.
    """
    print("[ ] Fetching user", end="")
    user_url = "https://api.github.com/users/" + user
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    
    response = requests.get(user_url, headers=headers)

    if response.status_code == 404:
        sys.exit(f"ERROR: { user } is not a GitHub user")
    elif response.status_code == 401:
        sys.exit(f"ERROR: Forbidden")
    elif response.status_code != 200:
        sys.exit(f"ERROR: Couldn't fetch user data")

    print("\r[✓] Fetching user")
    return response.json()


def fetch_user_repos(user):
    """
    Fetch the public repositories for a given GitHub user.

    This function sends a request to the GitHub API to retrieve the list of public repositories for the specified user.

    Args:
        user (str): The GitHub username to fetch repositories for.

    Returns:
        list: A list of dictionaries, each containing data for one of the user's repositories.

    Raises:
        SystemExit: If the user or repositories are not found, or if the request fails.
    """
    print("[ ] Fetching repositories", end="")
    repos_url = f"https://api.github.com/users/{user}/repos"
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(repos_url, headers=headers)

    if response.status_code == 404:
        sys.exit(f"ERROR: Couldn't find repository")
    elif response.status_code != 200:
        sys.exit(f"ERROR: Couldn't fetch repository data")

    print("\r[✓] Fetching repositories")
    return response.json()


def choose_repo(repos):
    """
    Allow the user to select a repository from the list by number or by exact name.

    Args:
        repos: A list of repositories, each represented as a dictionary with at least 'name' and 'html_url' keys.

    Returns:
        str: The URL of the selected repository.
    """
    while True:
        repo_input = input("\nSelect which one you want to analyze: ")

        if repo_input.isdigit():
            repo_pos = int(repo_input) - 1
            if 0 <= repo_pos < len(repos):
                selected_repo = repos[repo_pos]
            else:
                print("Invalid number. Please try again.")
                continue
        else:
            selected_repo = next((repo for repo in repos if repo.get('name') == repo_input), None)
            if selected_repo is None:
                print("Repository name not found. Please try again.")
                continue
        
        # Confirmar la selección
        confirm_input = input(f"Analyze [{selected_repo.get('name')}]? (y/n) ")
        if confirm_input.lower() == 'y':
            return selected_repo.get('html_url')
        elif confirm_input.lower() != 'n':
            print("Not valid. Please enter 'y' or 'n'.")


def analyse_project(rootPath):
    """
    Initiates the analysis of a Python project by recursively traversing the specified directory.

    Args:
        rootPath: The root directory of the project to be analyzed.

    Returns:
        None
    
    Raises:
        SystemExit: If the provided path does not exist or is not a directory.
    """
    print("Starting code analysis")

    load_settings()
    rootPath = os.path.abspath(rootPath)

    if not os.path.exists(rootPath):
        sys.exit(f"ERROR: Path {rootPath} does not exist")
    if not os.path.isdir(rootPath):
        sys.exit(f"ERROR: Path {rootPath} is not a directory")
    
    ignored_folders = SETTINGS.get("ignoreFolders", [])

    file_count = 0
    for root, dirs, files in os.walk(rootPath):
        dirs[:] = [d for d in dirs if not any(os.path.join(root, d).endswith(ignored_folder)
                for ignored_folder in ignored_folders
            )]
        for file in files:
            if file.endswith(".py"):
                file_count += 1
    
    current_file = [0]
    analyse_directory(rootPath, file_count, current_file)
    print()


def analyse_directory(path, total_length=None, current_file=None):
    """
    Recursively search the directory for Python files and process them.

    Args:
        path: The absolute path to the directory.
        total_length: Number of files inside the directory.
        current_file: Number of files already checked from the root path.
    """
    try:
        # List all items in the directory
        items = os.listdir(path)
        # Process each item
        for item in items:
            item_path = os.path.join(path, item)
            # Check if the item is a Python file
            if os.path.isfile(item_path) and item.endswith(".py"):
                print_progress(current_file[0] + 1, total_length)
                analyse_file(item_path)
                current_file[0] += 1
            # Check if the item is a directory
            elif os.path.isdir(item_path):
                # Skip the directory if it matches any ignored folder
                if any(
                    os.path.join(item_path).endswith(ignored_folder)
                    for ignored_folder in SETTINGS.get("ignoreFolders", [])
                ):
                    continue
                
                # Recursively analyse the directory if not ignored
                analyse_directory(item_path, total_length, current_file)

    except FileNotFoundError:
        print(f"ERROR: Directory {path} not found")
    except PermissionError:
        print(f"ERROR: Permission denied to access {path}")
    except Exception:
        print(f"ERROR: Couldn't read {path}")



def analyse_file(path):
    """
    Read a Python file and parse it into an abstract syntax tree (AST).

    Args:
        path: The path to the Python file.
    """
    with open(path) as fp:
        my_code = fp.read()
        try:
            tree = ast.parse(my_code)
            # Iterate through and process every attribute
            for attribute_list in ATTRIBUTES:
                for attribute in attribute_list:
                    file = os.path.basename(path)
                    dir_name = os.path.basename(os.path.dirname(path))
                    IterTree(tree, attribute, file, dir_name)
        except SyntaxError:
            print("There is a syntax error in the code")
            pass


def load_settings():
    """
    Load settings from the JSON file into the global SETTINGS variable.
    If the file does not exist, create it with default content.
    """
    global SETTINGS
    default_settings = {
        "ignoreFolders": [],
        "API-KEY": "",
        "addLocalSuffix": True
    }
    
    if not os.path.isfile('settings.json'):
        with open('settings.json', 'w') as file:
            json.dump(default_settings, file, indent=4)
    
    with open('settings.json', 'r') as file:
        SETTINGS = json.load(file)

    SETTINGS["ignoreFolders"] = [folder.rstrip('/') for folder in SETTINGS.get("ignoreFolders", [])]    # Remove / if included


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


def get_repo_data():
    """
    Fetch data about the repository, including commits, lines of code (LOC), modified files, and contributors.

    This function interacts with the GitHub API to retrieve:
    - Information about commits, including the total number of commits, modified files, lines of code added or deleted, and timestamps of commits.
    - Information about contributors, including their names and the number of commits they've made.

    Returns:
        dict: A dictionary containing:
            - 'total_commits': Total number of commits.
            - 'total_loc': Total lines of code (additions and deletions).
            - 'total_files_modified': Total number of unique files modified across all commits.
            - 'total_hours': Estimated hours spent on the project, calculated from commit timestamps.
            - 'contributors': A list of contributors with their GitHub usernames and number of commits.
    """

    repo_data = get_repo()
    repo_commits = get_repo_commits()
    repo_contributors = get_repo_contributors()

    return {
        'data': repo_data,
        'commits': repo_commits,
        'contributors': repo_contributors
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


def get_repo():
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    print("[ ] Fetching data", end="")
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Warning: there was an error retrieving repository information [{response.status_code}]")
        return
    
    response_json = response.json()
    print("\r[✓] Fetching data")
    return {
        'name' : response_json['name'],
        'url': response_json['html_url'],
        'description': response_json['description'],
        'createdDate': response_json['created_at'],
        'lastUpdateDate': response_json['updated_at'],
        'owner': {
            'name' : response_json.get('owner')['login'],
            'avatar' : response_json.get('owner')['avatar_url'],
            'profile_url' : response_json.get('owner')['html_url']
        }
    }


def get_repo_commits():
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    print("[ ] Fetching commits", end="", flush=True)
    page_counter = 1
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}/commits"
    all_commits = []

    while True:
        response = requests.get(url, params={'per_page': 100, 'page': page_counter}, headers=headers)

        if response.status_code != 200:
            print(f"\nWarning: there was an error retrieving commits information [{response.status_code}]")
            return
        
        page_commits = response.json()
        all_commits.extend(page_commits)

        if len(page_commits) < 100:
            break
        
        page_counter += 1

    total_commits = len(all_commits)
    total_loc = 0
    files_set = set()
    commit_dates = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_commit_details, commit['url'], headers) for commit in all_commits]

        for future in as_completed(futures):
            commit_response = future.result()

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
    print("\r[✓] Fetching commits", flush=True)

    return {
        'total_commits': total_commits,
        'total_loc': total_loc,
        'total_files_modified': total_files_modified,
        'total_hours': total_hours
    }



def fetch_commit_details(commit_url, headers):
    response = requests.get(commit_url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_repo_contributors():
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}/contributors"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Warning: there was an error retrieving contributors information [{response.status_code}]")
        return

    response_json = response.json()

    contributors = []
    for contributor in response_json:
        author = {
            'name': contributor['login'],
            'avatar': contributor['avatar_url'],
            'profile_url': contributor['html_url'],
            'commits': contributor['contributions']   
        }
        contributors.append(author)

    print("\r[✓] Fetching contributors")

    return contributors

def save_data(data):
    """
    Save the repository data into a JSON file.

    This function loads existing data from `data_new.json`, updates it with the new repository information, and saves it to a new file in the `results/` directory. The new file will be named after the repository.

    Args:
        data (dict): The repository data to be saved, typically returned from `get_repo_data()`.

    Raises:
        SystemExit: If the `data_new.json` file cannot be found.
    """
    print("[ ] Saving data", end="")
    try:
        with open("backend/tmp/data.json", "r") as file:
            file_data = json.load(file)    
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find data file")

    if all(key in data for key in ['data', 'commit', 'contributors']):
        file_data.update({"repoInfo": data})
    else:
        REPO_NAME = data
        file_data.update({"dirInfo": {'name': data}})

    os.makedirs("results", exist_ok=True)

    suffix = "_local" if SETTINGS.get("addLocalSuffix", False) else ""

    output_file = f"results/{REPO_NAME}{suffix}.json"

    with open(output_file, "w") as file:
        json.dump(file_data, file, indent=4)
    
    print("\r[✓] Saving data")


def get_api_token():
    """
    Retrieve the API token from the personal configuration file.

    This function reads the `backend/config/personal.json` file and extracts the GitHub API key used for authentication.

    Returns:
        str: The API token if found in the configuration file, otherwise an empty string.

    Raises:
        SystemExit: If the `personal.json` file cannot be found.
    """
    try:
        with open("backend/config/personal.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find personal.json")

    return data.get("API-KEY", "")