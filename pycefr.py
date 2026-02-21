"""CLI entry point for the PyCEFR analyzer.

This module provides a command-line interface to interact with the PyCEFR
analysis engine, allowing for local directory scanning, GitHub repository
analysis, and result management.
"""

import argparse
import os

from backend.services.analyzer import console
from backend.services.analyzer.analyzer import (
    request_url,
    run_directory,
    run_user,
)


def list_results() -> None:
    """List all generated JSON result files in the results directory.

    Checks for the existence of the './results/' directory and prints a
    bulleted list of all files contained within. If the directory is missing
    or empty, an appropriate message is displayed.
    """
    results_dir = "./results/"
    if not os.path.exists(results_dir):
        print(f"The directory {results_dir} does not exist.")
        return

    files = [f for f in os.listdir(results_dir) if os.path.isfile(os.path.join(results_dir, f))]
    if not files:
        print("No result files found.")
    else:
        print("Available results:")
        for file in files:
            print(f"- {file}")


def main() -> None:
    """Parse command-line arguments and execute the requested analysis action.

    This function sets up a mutually exclusive group for primary actions
    (directory, repo, user, console, list) to ensure valid command usage.
    It then routes the execution to the corresponding service function based
    on the provided flags.
    """
    parser = argparse.ArgumentParser(
        description="A utility for analyzing Python level in local and GitHub repositories."
    )

    # --- Mutually Exclusive Group ---
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument("-d", "--directory", type=str, help="Run in directory mode")
    action_group.add_argument("-r", "--repo", type=str, help="Run with the specified repository URL")
    action_group.add_argument("-u", "--user", type=str, help="Run with the specified user identifier")
    action_group.add_argument("-c", "--console", type=str, help="See results in console")
    action_group.add_argument("-l", "--list", action="store_true", help="List available result files")

    # --- Modifiers ---
    parser.add_argument(
        "--include-repo", action="store_true", help="Include repository metadata analysis (commits, contributors)"
    )
    parser.add_argument("-p", "--print", action="store_true", help="Print the results to the console after analysis")

    args = parser.parse_args()

    if args.console:
        target = args.console if args.console.endswith(".json") else f"{args.console}.json"
        console.main(f"results/{target}")

    elif args.directory:
        run_directory(args.directory, args.include_repo, args.print)

    elif args.list:
        list_results()

    elif args.repo:
        request_url(args.repo, args.include_repo, args.print)

    elif args.user:
        run_user(args.user, args.include_repo, args.print)


if __name__ == "__main__":
    main()
