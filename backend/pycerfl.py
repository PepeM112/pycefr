import ast
import os
import sys
import shlex
import subprocess
import requests
import argparse
from backend.scripts.ClassIterTree import IterTree
from scripts.getjson import read_Json
from scripts.getcsv import read_FileCsv
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

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
    # Parse the repository URL
    parsed_url = urlparse(url)

    if parsed_url.scheme != 'https':
        sys.exit("ERROR: URL must use the 'https' protocol.")
    if parsed_url.netloc != 'github.com':
        sys.exit("ERROR: URL must  be from 'github.com'.")

    path_segments = parsed_url.path.strip('/').split('/')
    user = path_segments[0]
    repo = path_segments[1].replace(".git", "")
    
    if not path_segments:
        sys.exit(
            "ERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO.git"
        )

    if not is_python_language(parsed_url.scheme, parsed_url.netloc, user, repo):
        sys.exit("ERROR: The repository does not contain at least 50% of Python.")

    cloned_repo = clone_repo(url)

    analyse_directory(cloned_repo, cloned_repo.split("/")[-1])



def is_python_language(protocol, type_git, user, repo):
    """
    Check if the repository's primary language is Python and if it constitutes at least 50% of the code.

    Args:
        protocol: The protocol part of the URL.
        type_git: The domain part of the URL.
        user: The GitHub username.
        repo: The repository name.

    Returns:
        bool: True is repo contains enough Python, False otherwise

    Raises:
        SystemExit: If the repository does not meet the language criteria.
    """
    repo_url = f"{protocol}://api.{type_git}/repos/{user}/{repo}/languages"
    print("Analyzing repository languages...\n")

    # Decode JSON response into a Python dict:
    response = requests.get(repo_url).json()

    # Calculate total elements and check Python presence
    total_elem = sum(response.values())
    python_quantity = response.get("Python", 0)

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
    repo_name = url.split("/")[-1].replace(".git", "")

    # Delete folder if already exists
    if os.path.exists(clone_dir):
        subprocess.call(["rm", "-rf", clone_dir])

    os.makedirs(clone_dir)

    command_line = shlex.split(f"git clone {url} {os.path.join(clone_dir, repo_name)}")
    subprocess.call(command_line)

    return os.path.join(clone_dir, repo_name)


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
    try:
        # Extract headers
        headers = requests.get(user_url)
        headers.raise_for_status()
        # Decode JSON response into a Python dict:
        response = headers.json()
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
        names = requests.get(repo_url)
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


def analyse_directory(path, dir_name):
    """
    Recursively search the directory for Python files and process them.

    Args:
        path: The absolute path to the directory.
        dir_name: The name of the current directory being processed.
        system.
    """
    try:
        # List all items in the directory
        items = os.listdir(path)
        # Process each item
        for item in items:
            item_path = os.path.join(path, item)
            # Check if the item is a python file"
            if os.path.isfile(item_path) and item.endswith(".py"):
                analyse_file(item_path, dir_name)

            # Check if the item is a directory
            elif os.path.isdir(item_path):
                analyse_directory(item_path, item)

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
    print(">> analyze_file: ", path, "|", dir_name)
    with open(path) as fp:
        my_code = fp.read()
        try:
            tree = ast.parse(my_code)
            iterate_list(tree, path, dir_name)
        except SyntaxError:
            print("There is a syntax error in the code")
            pass


def iterate_list(tree, path, dir_name):
    """
    Iterate through the list of attributes and process each one.

    Args:
        tree: The AST of the Python code.
        path: The path to the Python file.
        dir_name: The name of the current directory being processed.
    """
    print(">>>> iterate_list: ", tree, "|", path, "|", dir_name)
    for attribute_list in ATTRIBUTES:
        for attribute in attribute_list:
            file = path.split("/")[-1]
            IterTree(tree, attribute, file, dir_name)


def summary_Levels():
    """
    Provide a summary of the directory levels by reading JSON and CSV files.
    """
    result = read_Json()
    read_FileCsv()
    print(result)


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
