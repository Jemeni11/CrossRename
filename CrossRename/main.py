import os
import sys
import re
from pathlib import Path
import argparse
import logging
from .utils import check_for_update

__version__ = "1.2.0"

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


def collect_directories(directory: str) -> list[str]:
    """Collect all directories, sorted by depth (deepest first)"""
    directories = []
    for root, dirs, _ in os.walk(directory, followlinks=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.path.islink(dir_path):  # Skip symlinked directories
                directories.append(dir_path)

    # Sort by depth (deepest first) to avoid path breakage
    return sorted(directories, key=lambda x: x.count(os.sep), reverse=True)


def rename_directory(dir_path: str, dry_run: bool = False) -> str:
    """Rename directory and return the new path"""
    parent_dir, dir_name = os.path.split(dir_path)
    new_dir_name = sanitize_filename(dir_name)

    if new_dir_name != dir_name:
        new_dir_path = os.path.join(parent_dir, new_dir_name)
        if dry_run:
            logger.info(f"[Dry-run] Would rename directory: {dir_name} -> {new_dir_name}")
            return new_dir_path  # Return what the path would be
        else:
            try:
                os.rename(dir_path, new_dir_path)
                logger.info(f"Renamed directory: {dir_name} -> {new_dir_name}")
                return new_dir_path
            except Exception as e:
                logger.error(f"Error renaming directory {dir_name}: {str(e)}")
                return dir_path  # Return original path if rename failed
    else:
        logger.info(f"No change needed for directory: {dir_name}")
        return dir_path


def show_warning(renaming_directories: bool):
    if renaming_directories:
        print("⚠️  WARNING: File AND directory renaming is enabled!")
        print("   This may rename the target directory itself and/or subdirectories.")
        print("   Directory renaming will change folder paths and may break external references.")
    else:
        print("⚠️  WARNING: File renaming is enabled!")

    print("   This may break scripts, shortcuts, or other references to these files.")
    print("   It is HIGHLY recommended to run with --dry-run first.")
    print("   Continue? (y/N): ", end="")

    response = input().lower().strip()
    if response != 'y':
        print("Operation cancelled.")
        sys.exit(0)


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="CrossRename: Harmonize file and directory names for Linux and Windows.")
        parser.add_argument("-p", "--path", help="The path to the file or directory to rename.")
        parser.add_argument(
            "-v",
            "--version",
            help="Prints out the current version and quits.",
            action='version',
            version=f"CrossRename Version {__version__}"
        )
        parser.add_argument(
            "-u", "--update",
            help="Check if a new version is available.",
            action="store_true"
        )
        parser.add_argument(
            "-r",
            "--recursive",
            help="Rename all files in the directory path given and its subdirectories. When used with -D, also renames subdirectories.",
            action="store_true"
        )
        parser.add_argument("-d", "--dry-run", help="Perform a dry run, logging changes without renaming.",
                            action="store_true")
        parser.add_argument(
            "-D", "--rename-directories",
            help="Also rename directories to be cross-platform compatible. Use with caution!",
            action="store_true"
        )
        parser.add_argument(
            "--force",
            help="Skip safety prompts (useful for automated scripts)",
            action="store_true"
        )

        args = parser.parse_args()
        path = args.path
        recursive = args.recursive
        dry_run = args.dry_run
        rename_dirs = args.rename_directories

        if args.update:
            check_for_update(__version__)
            sys.exit()

        # Show warning for ANY renaming operation (unless dry-run or force)
        if not dry_run and not args.force:
            if sys.stdout.isatty():
                show_warning(rename_dirs)
            else:
                sys.exit("Error: Renaming requires --force flag in non-interactive mode")


        if path is None:
            sys.exit("Error: Please provide a path to a file or directory using the --path argument.")

        if os.path.isfile(path):
            rename_file(path, dry_run)
        elif os.path.isdir(path):
            if recursive:
                # First rename directories (deepest first)
                if rename_dirs:
                    directories = collect_directories(path)
                    for dir_path in directories:
                        rename_directory(dir_path, dry_run)

                # Then rename files (using updated paths)
                file_list = file_search(path)
                for file_path in file_list:
                    rename_file(file_path, dry_run)
            else:
                if rename_dirs:
                    rename_directory(path, dry_run)

                # Handle files in the directory
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
