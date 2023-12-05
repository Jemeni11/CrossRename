import argparse
import sys
import os

__version__ = "1.0.0"


def file_search(current_directory: str) -> list:
    files_path_list = []

    for dirpath, dirnames, files in os.walk(current_directory):
        for file in files:
            file_path = os.path.join(dirpath, file)
            files_path_list.append(file_path)

    if len(files_path_list) == 0:
        sys.exit("No files found!")

    print(f"Found {len(files_path_list)} files in total!")
    return files_path_list


def main() -> None:

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-p", "--path_to_file", help="The path to the file.")
    parser.add_argument("-c", "--config_file_path",
                        help="The path to the crossrename.json file.")
    parser.add_argument(
        "-d", "--debug", help="Enable debug mode.", action="store_true")
    parser.add_argument(
        "-v",
        "--version",
        help="Prints out the current version and quits.",
        action='version',
        version=f"CrossRename Version {__version__}"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="This will rename all files in the directory path given and its subdirectories.",
    )
    args = parser.parse_args()

    path_to_epub = args.path_to_epub
    config_file_path = args.config_file_path
    debug = args.debug
    recursive = args.recursive

    if path_to_epub is None and recursive is None:
        sys.exit("Either pass in a path to a file or use the --recursive flag to convert the current directory and "
                 "its sub-directories")
    elif path_to_epub:
        if recursive:
            print("Ignoring --recursive flag since path_to_epub was given")
        # update_epub(path_to_epub, config_file_path, debug)
    elif recursive:
        list_of_files = file_search(recursive)
        for i in list_of_files:
            try:
                print("")
                # update_epub(i, config_file_path, debug)
            except Exception as e:
                print(f"Error! Skipping {i}")
                if debug:
                    print(f"Exception: {e}")


if __name__ == '__main__':
    main()
