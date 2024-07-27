import ast
import os
import sys
import shlex
import subprocess
import requests
import argparse
from ClassIterTree import IterTree
from getjson import read_Json
from getcsv import read_fileCsv


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


def choose_option(option, path):
    """
    Choose the appropriate action based on the provided option.

    Args:
        option: The type of action to perform ('d' for directory, 'r' for repository URL, 'u' for user).
        path: The path or URL to be processed.

    Raises:
        SystemExit: If the option is incorrect.
    """
    if option == "d":
        repo = path.split("/")[-1]
        read_directory(path, repo)
    elif option == "r":
        request_url(path)
    elif option == "u":
        run_user(path)
    else:
        sys.exit("Incorrect Option")


def request_url(url):
    """
    Handle a repository URL by splitting it, checking its validity, and analyzing its language content.

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
    values = url.split("/")
    try:
        protocol = values[0].split(":")[0]
        type_git = values[2]
        user = values[3]
        repo = values[4][:-4]  # Remove the ".git" extension if present
    except IndexError:
        sys.exit("ERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO.git")

    # Validate the URL's protocol and domain
    if protocol != "https":
        sys.exit("ERROR: URL must use the 'https' protocol.")
    if type_git != "github.com":
        sys.exit("ERROR: URL must be from 'github.com'.")

    check_language(url, protocol, type_git, user, repo)


def check_language(url, protocol, type_git, user, repo):
    """
    Check if the repository's primary language is Python and if it constitutes at least 50% of the code.

    Args:
        url: The URL of the repository.
        protocol: The protocol part of the URL.
        type_git: The domain part of the URL.
        user: The GitHub username.
        repo: The repository name.

    Raises:
        SystemExit: If the repository does not meet the language criteria.
    """
    total_elem = 0
    python_lang = False
    python_quantity = 0
    # Create the URL of the API
    repo_url = (
        protocol + "://api." + type_git + "/repos/" + user + "/" + repo + "/languages"
    )
    print("Analyzing repository languages...\n")
    # Get content
    r = requests.get(repo_url)
    # Decode JSON response into a Python dict:
    content = r.json()
    # Get used languages and their quantity
    for key in content.keys():
        print(key + ": " + str(content[key]))
        if key == "Python":
            python_lang = True
            python_quantity = content[key]
        total_elem += content[key]
    # Check if Python is 50%
    if python_lang:
        amount = total_elem / 2
        if python_quantity >= amount:
            print("\nPython >50% OK\n")
            # Clone the repository
            run_url(url)
        else:
            print("\nThe repository does not contain 50% of Python.\n")


def run_url(url):
    """
    Clone the repository from the provided URL and handle the directory.

    Args:
        url: The URL of the repository to be cloned.
    """
    command_line = shlex.split("git clone " + url)
    print("Running URL...")
    # Run in the shell the command_line
    subprocess.call(command_line)
    get_directory(url)


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
        content = headers.json()
        # Get repository URL
        repo_url = content["repos_url"]
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
        content = names.json()
        # Show repository names
        for repository in content:
            print("\nRepository: " + str(repository["name"]))
            url = "https://github.com/" + user + "/" + repository["name"]
            check_language(url, "https", "github.com", user, repository["name"])
    except requests.exceptions.HTTPError:
        sys.exit("ERROR: Unable to retrieve repositories. Check if the user has any public repositories.")



def get_directory(url):
    """
    Determine the name of the directory where the repository has been cloned.

    Args:
        url: The URL of the cloned repository.
    """
    # Get values from the URL
    values = url.split("/")
    # Last element in the list
    name_directory = values[-1]
    # Remove extension .git
    if ".git" in str(name_directory):
        name_directory = name_directory[0:-4]
    print("The directory is: " + name_directory)
    get_path(name_directory)


def get_path(name_directory):
    """
    Get the absolute path to the directory and initiate further processing.

    Args:
        name_directory: The name of the directory to be processed.
    """
    abs_file_path = os.path.abspath(name_directory)
    # Check if the last element is a file.py
    fichero = abs_file_path.split("/")[-1]
    if fichero.endswith(".py"):
        abs_file_path = abs_file_path.replace("/" + fichero, "")
    print("This script's absolute path is ", abs_file_path)
    read_directory(abs_file_path, name_directory)


def read_directory(path, dir_name):
    """
    Recursively search the directory for Python files and process them.

    Args:
        path: The absolute path to the directory.
        dir_name: The name of the current directory being processed.
        system.
    """
    print("Directory: ")

    try:
        # List all items in the directory
        items = os.listdir(path)
        print(items)

        # Process each item
        for item in items:
            item_path = os.path.join(path, item)

            # Check if the item is a python file"
            if os.path.isfile(item_path) and item.endswith(".py"):
                print("Python File: " + str(item))
                read_file(item_path, dir_name)

            # Check if the item is a directory
            elif os.path.isdir(item_path):
                print("\nOpening another directory...\n")
                read_directory(item_path, item)

    except FileNotFoundError:
        print(f"Directory {path} not found")
    except PermissionError:
        print(f"Permission denied to access {path}")


def read_file(path, dir_name):
    """
    Read the content of a Python file and parse it into an abstract syntax tree (AST).

    Args:
        pos: The path to the Python file.
        dir_name: The name of the current directory being processed.
    """
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
    for attribute_list in ATTRIBUTES:
        for attribute in attribute_list:
            file = path.split("/")[-1]
            IterTree(tree, attribute, file, dir_name)


def summary_Levels():
    """
    Provide a summary of the directory levels by reading JSON and CSV files.
    """
    result = read_Json()
    read_fileCsv()
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
        choose_option("d", args.directory)
    elif args.repo:
        choose_option("r", args.repo)
    elif args.user:
        choose_option("u", args.user)
    else:
        parser.print_help()
        sys.exit("Usage: python3 pycerfl.py [-d directory | -r repo | -u user]")


if __name__ == "__main__":
    main()
