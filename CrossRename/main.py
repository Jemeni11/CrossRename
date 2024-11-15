import os
import sys
import re
from pathlib import Path
import argparse
import logging

__version__ = "1.1.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s » %(message)s')


def get_extension(filename: str) -> str:
    """Extracts the extension from a
    filename. Returns an empty string if
    no extension is found.
    """
    # Handle special cases like .tar.gz, .tar.bz2, etc.
    path = Path(filename)
    suffixes = path.suffixes

    if not suffixes:
        return ''

    return ''.join(suffixes[-2:]) if len(suffixes) > 1 else suffixes[-1]


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to be Windows-compatible (and thus Linux-compatible)"""
    # Remove reserved characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00]', '', filename)

    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) > 31)

    # Handle reserved names (including those with superscript digits)
    reserved_names = r'^(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])($|\..*$)'
    if re.match(reserved_names, sanitized, re.I):
        sanitized = f"_{sanitized}"

    # Remove trailing spaces and periods
    sanitized = sanitized.rstrip(' .')

    # Ensure the filename isn't empty after sanitization
    if not sanitized:
        sanitized = 'unnamed_file'

    # Handle leading period (allowed, but keep it only if it was there originally)
    if filename.startswith('.') and not sanitized.startswith('.'):
        sanitized = '.' + sanitized

    # Truncate filename if it's too long (255-character limit for name+extension)
    max_length = 255
    if len(sanitized) > max_length:
        ext = get_extension(sanitized)
        ext_length = len(ext)
        name = sanitized[:-ext_length] if ext else sanitized
        sanitized = name[:max_length - ext_length] + ext

    return sanitized


def rename_file(file_path: str, dry_run: bool = False) -> None:
    directory, filename = os.path.split(file_path)
    new_filename = sanitize_filename(filename)

    if new_filename != filename:
        new_file_path = os.path.join(directory, new_filename)
        if dry_run:
            logger.info(f"[Dry-run] Would rename: {filename} -> {new_filename}")
        else:
            try:
                os.rename(file_path, new_file_path)
                logger.info(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                logger.error(f"Error renaming {filename}: {str(e)}")
    else:
        logger.info(f"No change needed: {filename}")


def file_search(directory: str) -> list[str]:
    file_list = []
    visited_paths = set()

    for root, _, files in os.walk(directory, followlinks=False):
        real_root = os.path.realpath(root)

        if real_root in visited_paths:
            logger.warning(f"Skipping recursive symlink in {root}")
            continue

        visited_paths.add(real_root)

        for file in files:
            file_path = os.path.join(root, file)
            if os.path.islink(file_path):
                logger.info(f"Skipping symlink: {file_path}")
                continue
            file_list.append(file_path)

    return file_list


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="CrossRename: Harmonize file names for Linux and Windows.")
        parser.add_argument("-p", "--path", help="The path to the file or directory to rename.", required=True)
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
            help="Rename all files in the directory path given and its subdirectories.",
            action="store_true"
        )
        parser.add_argument("--dry-run", help="Perform a dry run, logging changes without renaming.",
                            action="store_true")
        args = parser.parse_args()

        path = args.path
        recursive = args.recursive
        dry_run = args.dry_run

        if path is None:
            sys.exit("Please provide a path to a file or directory using the --path argument.")

        if os.path.isfile(path):
            rename_file(path, dry_run)
        elif os.path.isdir(path):
            if recursive:
                file_list = file_search(path)
                for file_path in file_list:
                    rename_file(file_path, dry_run)
            else:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        rename_file(item_path, dry_run)
        else:
            sys.exit(f"Error: {path} is not a valid file or directory")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    main()
