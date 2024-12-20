import os
import re
import sys
import ast
import json
import shlex
import shutil
import subprocess
import requests
import configparser
from datetime import datetime
from genericpath import isdir
from curses.ascii import isdigit
from urllib.parse import urlparse
from collections import defaultdict
from backend.scripts import console
from backend.scripts.iter_tree import IterTree
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
    global API_KEY
    API_KEY = get_api_token()

    validate_repo_url(url)

    cloned_repo = clone_repo(REPO_URL)

    analyse_project(cloned_repo)
    remove_dir(cloned_repo)

    repo_info = get_repo_data()
    output_file = save_data(repo_info)

    if SETTINGS.get("autoDisplayConsole", False):
        console.main(output_file)
    print(f"\nResults file can be found in file:/{os.path.abspath(output_file)}\n")


def remove_dir(path):
    """
    Removes a directory at the specified path and all its contents.

    Args:
        path (str): The path to the directory to be removed.

    Returns:
        None: Prints error messages if the directory does not exist or cannot be removed.
    """
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
    """
    Validates the GitHub repository URL and extracts the user name and repository name.

    Args:
        url (str): The GitHub repository URL to validate.

    Returns:
        None: Sets global variables for repository URL, user name, repository name, and API key.
              Exits the program if the URL is invalid or not from GitHub.
    """
    global REPO_URL, REPO_NAME, USER_NAME
    
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

    if response.status_code == 403 or response.status_code == 401:
        print()
        display_api_token_error()
    elif response.status_code == 404:
        sys.exit(f"\nERROR: Repository doesn't exist [{response.status_code}]")
    elif response.status_code != 200:
        sys.exit(f"\nERROR: Couldn't validate Python language [{response.status_code}]")
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

    if response.status_code == 403 or response.status_code == 401:
        print()
        display_api_token_error()
    elif response.status_code == 404:
        sys.exit(f"\nERROR: { user } is not a GitHub user")
    elif response.status_code != 200:
        sys.exit(f"\nERROR: Couldn't fetch user data")

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

    if response.status_code == 403 or response.status_code == 401:
        print()
        display_api_token_error()
    elif response.status_code == 404:
        sys.exit(f"\nERROR: Couldn't find repository")
    elif response.status_code != 200:
        sys.exit(f"\nERROR: Couldn't fetch repository data")

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
        repo_input = input("\nSelect which one you want to analyze (Enter [0] to exit): ")
        if repo_input == '0':
            sys.exit()
        elif repo_input.isdigit():
            repo_pos = int(repo_input) - 1
            if 0 <= repo_pos < len(repos):
                selected_repo = repos[repo_pos]
            else:
                print("Invalid number. Please try again.")
                continue
        else:
            selected_repo = next((repo for repo in repos if repo.get('name') == repo_input), None)
            if selected_repo is None:
                print("Repository name not found. Please try again (Enter [0] to exit).")
                continue
        
        # Confirmar la selección
        
        confirm_input = input(f"Analyze [{selected_repo.get('name')}]? (Y/n) ")
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
    print("[ ] Analysing code", end=" ")

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
    print("\r[✓] Analysing code" + " " * 50)


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
        print(f"\nERROR: Directory {path} not found")
    except PermissionError:
        print(f"\nERROR: Permission denied to access {path}")
    except Exception:
        print(f"\nERROR: Couldn't read {path}")



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
            # Calculate the relative path
            relative_path = os.path.relpath(path, start=os.getcwd())
            # Iterate through and process every attribute
            for attribute_list in ATTRIBUTES:
                for attribute in attribute_list:
                    IterTree(tree, attribute, re.sub(r"^backend/tmp/[^/]+/", "", relative_path))
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
        "ignoreFolders": [
            "node_modules/",
            ".git/",
            "__pycache__/"
        ],
        "API-KEY": "",
        "addLocalSuffix": True,
        "autoDisplayConsole": True
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
    print(f"\r[ ] Analysing code [{progress}] {percent}%", end="")


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


def run_directory(dir):
    """
    Check if the specified directory contains a Git repository.
    If a Git repository is found, prompt the user to add repository information to the analysis.
    If the user chooses 'n' or provides invalid input, proceed with analyzing the project.
    """
    git_url = get_git_repo_url(dir)
    if git_url != "":
        while True:
            repo_input = input('A valid Git configuration has been detected. Would you like to analyse the origin repository? (Y/n) ').strip().lower()
            if repo_input == 'y':
                request_url(git_url)
                return 
            elif repo_input == 'n':
                break  # Exit the loop to continue with analysis
            else:
                print('Invalid input. Please enter Y or n.')
    
    # Proceed with analyzing the project and saving data
    analyse_project(dir)
    output_file = save_data(os.path.basename(os.path.abspath(dir)))
    if SETTINGS.get("autoDisplayConsole", False):
        console.main(output_file)
    print(f"\nResults file can be found in {os.path.abspath(output_file)}\n")


def get_git_repo_url(dir):
    """
    Retrieves the Git repository URL from the .git/config file in the specified directory.

    Args:
        dir (str): The directory where the .git folder is expected to be located.

    Returns:
        str: The repository URL in HTTP format if available, or an empty string if no valid URL is found.
    """
    git_dir = os.path.join(dir, '.git')
    
    if not os.path.isdir(git_dir):
        return ""
    
    config_file = os.path.join(git_dir, 'config')
    
    if not os.path.isfile(config_file):
        return ""
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'remote "origin"' not in config:
        return ""
    
    url = config['remote "origin"'].get('url')
    
    if not bool(url):
        return ""
    
    if url.startswith('git@'):
        url_part = url[4:]  # Skip 'git@'
        http_url = url_part.replace(':', '/', 1).replace('.git', '')
        return f'https://{http_url}'
    
    return url
            

def get_repo():
    """
    Fetches the GitHub repository information for the specified user and repository.

    Returns:
        dict: A dictionary containing repository details such as name, URL, description,
              creation date, last update date, and owner information, or None if the
              repository cannot be retrieved due to an error.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    print("[ ] Fetching data", end="")
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}"
    response = requests.get(url, headers=headers)

    if response.status_code == 403 or response.status_code == 401:
        display_api_token_error()
    elif response.status_code != 200:
        print(f"Warning: Couldn't retrieve repository information [{response.status_code}]")
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
    """
    Retrieves the commits from the specified GitHub repository.

    Returns:
        list: A list of dictionaries containing information about each author, their
              number of commits, lines of code (LOC) added or removed, total hours spent,
              and the total number of files modified.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    print("[ ] Fetching commits", end="", flush=True)
    page_counter = 1
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}/commits"
    all_commits = []

    while True:
        response = requests.get(url, params={'per_page': 100, 'page': page_counter}, headers=headers)

        if response.status_code == 403 or response.status_code == 401:
            print()
            display_api_token_error()
        elif response.status_code != 200:
            sys.exit(f"\nERROR: there was an error retrieving commits information.")
        
        page_commits = response.json()
        all_commits.extend(page_commits)

        if len(page_commits) < 100:
            break
        
        page_counter += 1

    user_data = defaultdict(lambda: {
        'name': '',
        'github_user': '',
        'loc': 0,
        'commits': 0,
        'total_hours': 0,
        'commit_dates': [],
        'files_set': set()
    })

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_commit_details, commit['url'], headers) for commit in all_commits]

        for future in as_completed(futures):
            commit_response = future.result()

            author = commit_response['commit']['committer']['name']
            github_user = commit_response.get('author', {}).get('login', 'Unknown')  # GitHub username
            commit_date = commit_response['commit']['committer']['date']
            commit_timestamp = datetime.fromisoformat(commit_date.replace('Z', '+00:00')).timestamp()

            user_data[author]['name'] = author
            user_data[author]['github_user'] = github_user
            user_data[author]['commits'] += 1
            user_data[author]['commit_dates'].append(commit_timestamp)

            # LOC
            stats = commit_response.get('stats', {})
            loc = stats.get('additions', 0) + stats.get('deletions', 0)
            user_data[author]['loc'] += loc

            # Files modified
            files = commit_response.get('files', [])
            for file in files:
                user_data[author]['files_set'].add(file['filename'])

    for author, data in user_data.items():
        data['total_hours'] = calculate_hours_spent(data['commit_dates'])
        data['total_files_modified'] = len(data['files_set'])
        # No longer needed
        del data['commit_dates']
        del data['files_set']    

    print("\r[✓] Fetching commits", flush=True)

    return list(user_data.values())


def fetch_commit_details(commit_url, headers):
    response = requests.get(commit_url, headers=headers)
    if response.status_code == 403 or response.status_code == 401:
        display_api_token_error()
    elif response.status_code != 200:
        print("\nERROR: Couldn't fetch commit details")
    return response.json()


def get_repo_contributors():
    """
    Fetches detailed information about a specific commit using its URL.

    Args:
        commit_url (str): The URL of the commit to fetch details for.
        headers (dict): The headers to be included in the API request, typically
                        containing the authorization token.

    Returns:
        dict: A dictionary containing detailed information about the commit,
              or an empty dictionary if the commit details cannot be fetched.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    url = f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}/contributors"
    response = requests.get(url, headers=headers)

    if response.status_code == 403 or response.status_code == 401:
        print()
        display_api_token_error()
    elif response.status_code != 200:
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
    global REPO_NAME
    print("[ ] Saving data", end="")
    try:
        with open("backend/tmp/data.json", "r") as file:
            file_data = json.load(file)    
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find data file")

    if all(key in data for key in ['data', 'commits', 'contributors']):
        file_data.update({"repoInfo": data})
    else:
        suffix = "_local" if SETTINGS.get("addLocalSuffix", True) else ""
        REPO_NAME = data + suffix
        file_data.update({"repoInfo": {'data': { 'name' : data}}})  # Just to be aligned with Git analysis

    os.makedirs("results", exist_ok=True)


    output_file = f"results/{REPO_NAME}.json"

    with open(output_file, "w") as file:
        json.dump(file_data, file, indent=4)
    
    print("\r[✓] Saving data")

    return output_file


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
        with open("settings.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        sys.exit("ERROR: Couldn't find settings.json")

    return data.get("API-KEY", "")


def display_api_token_error():
    """
    Handle GitHub API token error by displaying a message and exiting the program.
    """
    print("ERROR: Looks like you've reached the limit of API requests.")
    print("To continue, you will need an API key. You can generate one at:\n\thttps://github.com/settings/tokens\nand add it to your settings.json file.")
    print("Also see: https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting")
    sys.exit(1)
