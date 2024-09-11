import os
import sys
import argparse
from backend.scripts.analyzer import request_url, analyse_project, run_user


def main():
    """
    Main function to handle command-line arguments and invoke appropriate actions.
    """
    parser = argparse.ArgumentParser(description="Process options.")
    parser.add_argument("-d", "--directory", type=str, help="Path to the directory")
    parser.add_argument("-r", "--repo", type=str, help="Repository URL")
    parser.add_argument("-u", "--user", type=str, help="User identifier")

    args = parser.parse_args()

    if sum([bool(args.directory), bool(args.repo), bool(args.user)]) != 1:
        parser.print_help()
        sys.exit("Usage: python3 pycerfl.py [-d directory | -r repo | -u user]")

    if args.directory:
        analyse_project(args.directory)
    elif args.repo:
        request_url(args.repo)
    elif args.user:
        run_user(args.user)
    else:
        parser.print_help()
        sys.exit("Usage: python3 pycerfl.py [-d directory | -r repo | -u user]")


if __name__ == "__main__":
    main()
