from pathlib import Path

from backend.models.schemas.analysis import AnalysisResult, FullAnalysisResult
from backend.services.analyzer.analyzer_class import Analyzer
from backend.services.analyzer.github_manager import GitHubManager


def request_url(url: str) -> None:
    gh = GitHubManager(repo_url=url)
    gh.validate_repo_url()
    cloned_repo = gh.clone_repo()

    an = Analyzer(cloned_repo)
    an.analyse_project()

    repo_info = gh.get_repo_info()
    analysis_result = an.get_results()

    full_analysis = FullAnalysisResult(elements=analysis_result.elements, repo_info=repo_info)

    repo_name = repo_info.data.name
    file_path = Path(f"results/{repo_name}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(full_analysis.model_dump_json(indent=4))


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
                break  # Exit the loop to continue with analysis
            else:
                print("Invalid input. Please enter Y or n.")
    an = Analyzer(directory)
    an.analyse_project()
    analysis_results = an.get_results()

    full_analysis = AnalysisResult(elements=analysis_results.elements)

    repo_name = Path(directory).resolve().name
    file_path = Path(f"results/{repo_name}.json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(full_analysis.model_dump_json(indent=4))


def run_user(user: str) -> None:
    gh = GitHubManager(user=user)
    gh.fetch_user()
    repos = gh.fetch_user_repos()
    repo = GitHubManager.choose_repo(repos)
    request_url(repo)
