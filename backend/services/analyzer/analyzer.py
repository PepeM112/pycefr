import sys
from pathlib import Path
from typing import Any, Dict, List

from backend.services.analyzer.analyzer_class import Analyzer
from backend.services.analyzer.github_manager import GitHubManager


def request_url(url: str) -> None:
    try:
        gh = GitHubManager(repo_url=url, is_cli=True)
        gh.validate_repo_url()
        cloned_repo = gh.clone_repo()

        an = Analyzer(cloned_repo, is_cli=True)
        an.analyse_project()

        repo_info = gh.get_repo_info()
        analysis_result = an.get_results()
        analysis_result.repo = repo_info

        repo_name = repo_info.name
        file_path = Path(f"results/{repo_name}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(analysis_result.model_dump_json(indent=4))

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


def run_directory(directory: str) -> None:
    git_url = GitHubManager.get_git_repo_url(directory)

    if git_url:
        while True:
            repo_input = (
                input(
                    "A valid Git configuration has been detected. Would you like to analyse the origin repository? "
                    "(Y/n) "
                )
                .strip()
                .lower()
            )
            if repo_input == "y":
                request_url(git_url)
                return
            elif repo_input == "n":
                break
            else:
                print("Invalid input. Please enter Y or n.")

    try:
        an = Analyzer(directory, is_cli=True)
        an.analyse_project()
        analysis_results = an.get_results()

        repo_name = Path(directory).resolve().name
        file_path = Path(f"results/{repo_name}.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(analysis_results.model_dump_json(indent=4))
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    finally:
        Analyzer.delete_tmp_files()


def run_user(user: str) -> None:
    try:
        gh = GitHubManager(user=user, is_cli=True)
        gh.fetch_user()
        repos = gh.fetch_user_repos()
        repo_url = _choose_repo_cli(repos)
        if repo_url:
            request_url(repo_url)

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


def _choose_repo_cli(repos: List[Dict[str, Any]]) -> str:
    """Función auxiliar exclusiva para la interfaz CLI"""
    print("Repositories found:")
    for idx, repo in enumerate(repos, start=1):
        print(f"\t[{idx}] {repo.get('name')}")

    while True:
        repo_input = input("\nSelect which one you want to analyze (Enter [0] to exit): ")
        if repo_input == "0":
            sys.exit(0)
        elif repo_input.isdigit():
            repo_pos = int(repo_input) - 1
            if 0 <= repo_pos < len(repos):
                selected_repo = repos[repo_pos]
            else:
                print("Invalid number. Please try again.")
                continue
        else:
            matching_repos = [repo for repo in repos if repo.get("name") == repo_input]
            if not matching_repos:
                print("Repository name not found. Please try again (Enter [0] to exit).")
                continue
            selected_repo = matching_repos[0]

        confirm_input = input(f"Analyze [{selected_repo.get('name')}]? (Y/n) ")
        if confirm_input.lower() == "y":
            return str(selected_repo.get("html_url"))
        elif confirm_input.lower() != "n":
            print("Not valid. Please enter 'y' or 'n'.")
