import os
import argparse
from backend.scripts.analyzer import request_url, run_directory, run_user
from backend.scripts import console


def list_results():
    """
    List files in the ./results/ directory.
    """
    results_dir = './results/'
    try:
        files = os.listdir(results_dir)
        if not files:
            print("No result files found.")
        else:
            print("Available results:")
            for file in files:
                print(f"- {file}")
    except FileNotFoundError:
        print(f"The directory {results_dir} does not exist.")


def main():
    """
    Main function to handle command-line arguments and invoke appropriate actions.
    """
    parser = argparse.ArgumentParser(description="An utility for analyzing Python level in local and Github repositories.")
    parser.add_argument("-d", "--directory", type=str, help="Run in directory mode")
    parser.add_argument("-r", "--repo", type=str, help="Run with the specified repository URL")
    parser.add_argument("-u", "--user", type=str, help="Run with the specified user identifier")
    parser.add_argument("-c", "--console", type=str, help="See results in console")
    parser.add_argument("-l", "--list", action='store_true', help="List available result files")

    args = parser.parse_args()

    if sum([bool(args.directory), bool(args.repo), bool(args.user), bool(args.console), bool(args.list)]) != 1:
        parser.print_help()
    elif args.console:
        console.main(f"results/{args.console}")
    elif args.directory:
        run_directory(args.directory)
    elif args.list:
        list_results()
    elif args.repo:
        request_url(args.repo)
    elif args.user:
        run_user(args.user)

if __name__ == "__main__":
    main()
