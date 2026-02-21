import os
import sys
import re
from pathlib import Path
import argparse
import logging
from .utils import check_for_update

__version__ = "1.5.0"

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s » %(message)s"
)


def get_extension(filename: str) -> str:
    """Extracts the extension from a
    filename. Returns an empty string if
    no extension is found.
    """
    # Handle special cases like .tar.gz, .tar.bz2, etc.
    path = Path(filename)
    suffixes = path.suffixes

    if not suffixes:
        return ""

    return "".join(suffixes[-2:]) if len(suffixes) > 1 else suffixes[-1]


def sanitize_filename(filename: str, use_alternatives: bool = False, max_bytes: int = 255) -> str:
    """
    Sanitizes filename to be Windows-compatible (and thus Linux-compatible and macOS-compatible)

    :param filename: The original filename to sanitize
    :param use_alternatives: If True, replace forbidden characters with Unicode lookalikes
                 instead of removing them. May cause display/compatibility issues.
    :param max_bytes: Maximum filename length in bytes (default: 255 for ext4/btrfs compatibility).
                 Multi-byte UTF-8 characters (CJK, emoji, etc.) consume more of this budget.
    :return: The sanitized filename
    """
    # A file name can't contain any of the following characters on Windows: \ / : * ? " < > |
    if use_alternatives:
        # Replace reserved characters
        sanitized = re.sub(r"\x00", "", filename)
        sanitized = sanitized.translate(
            str.maketrans(
                {
                    "\\": "⧵",  # Reverse Solidus Operator U+29F5
                    "/": "∕",  # Division Slash U+2215
                    ":": "∶",  # Ratio U+2236
                    "*": "🞱",  # Bold Five Spoked Asterisk U+1F7B1
                    "?": "﹖",  # Small Question Mark U+FE56
                    '"': "ʺ",  # Modified Letter Double Prime U+2BA
                    "<": "ᐸ",  # Canadian Syllabics Pa U+1438
                    ">": "ᐳ",  # Canadian Syllabics Po U+1433
                    "|": "∣",  # Divides U+2223
                }
            )
        )
    else:
        # Remove reserved characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00]', "", filename)

    # Remove control characters
    sanitized = "".join(char for char in sanitized if ord(char) > 31)

    # Handle reserved names (including those with superscript digits)
    reserved_names = r"^(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])($|\..*$)"
    if re.match(reserved_names, sanitized, re.I):
        sanitized = f"_{sanitized}"

    # Remove trailing spaces and periods
    sanitized = sanitized.rstrip(" .")

    # Ensure the filename isn't empty after sanitization
    if not sanitized:
        sanitized = "unnamed_file"

    # Handle leading period (allowed, but keep it only if it was there originally)
    if filename.startswith(".") and not sanitized.startswith("."):
        sanitized = "." + sanitized

    # Truncate filename if it exceeds the byte limit (default 255 for ext4/btrfs).
    # We measure bytes because ext4/btrfs limit filenames to 255 bytes, not characters.
    # Multi-byte UTF-8 chars (CJK, emoji, etc.) consume more of this budget.
    if len(sanitized.encode("utf-8")) > max_bytes:
        ext = get_extension(sanitized)
        ext_bytes = len(ext.encode("utf-8"))
        name = sanitized[: -len(ext)] if ext else sanitized
        # Remove characters from the end until the total fits within the byte limit
        while len(name.encode("utf-8")) + ext_bytes > max_bytes and name:
            name = name[:-1]
        sanitized = name + ext

    return sanitized


def rename_file(
    file_path: str, dry_run: bool = False, use_alternatives: bool = False, max_bytes: int = 255
) -> None:
    directory, filename = os.path.split(file_path)
    new_filename = sanitize_filename(filename, use_alternatives, max_bytes)

    if new_filename != filename:
        new_file_path = os.path.join(directory, new_filename)

        # Check if target already exists (collision prevention)
        if os.path.exists(new_file_path) and os.path.realpath(
            file_path
        ) != os.path.realpath(new_file_path):
            # Target exists and is a different file - add suffix
            base_name, ext = os.path.splitext(new_filename)
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                new_file_path = os.path.join(directory, new_filename)
                counter += 1
            logger.warning(f"Target exists, using: {new_filename}")

        if dry_run:
            logger.info(f"[Dry-run] Would rename: {filename} -> {new_filename}")
        else:
            try:
                # Check if file still exists before rename (TOCTOU mitigation)
                if not os.path.exists(file_path):
                    logger.warning(f"File no longer exists, skipping: {filename}")
                    return

                os.rename(file_path, new_file_path)
                logger.info(f"Renamed: {filename} -> {new_filename}")
            except FileNotFoundError:
                logger.warning(f"File was deleted by another process: {filename}")
            except PermissionError:
                logger.error(f"Permission denied for {filename}")
            except FileExistsError:
                logger.error(
                    f"Target file already exists (race condition): {new_filename}"
                )
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


def rename_directory(
    dir_path: str, dry_run: bool = False, use_alternatives: bool = False, max_bytes: int = 255
) -> str:
    """Rename directory and return the new path"""
    parent_dir, dir_name = os.path.split(dir_path)
    new_dir_name = sanitize_filename(dir_name, use_alternatives, max_bytes)

    if new_dir_name != dir_name:
        new_dir_path = os.path.join(parent_dir, new_dir_name)
        if dry_run:
            logger.info(
                f"[Dry-run] Would rename directory: {dir_name} -> {new_dir_name}"
            )
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


def show_warning(renaming_directories: bool, use_alternatives: bool = False) -> None:
    if renaming_directories:
        print("⚠️ WARNING: File AND directory renaming is enabled!")
        print("   This may rename the target directory itself and/or subdirectories.")
        print(
            "   Directory renaming will change folder paths and may break external references."
        )
    else:
        print("⚠️ WARNING: File renaming is enabled!")

    if use_alternatives:
        print("⚠️ WARNING: Unicode alternatives enabled!")
        print(
            "   Special characters will be replaced with similar-looking Unicode characters."
        )
        print(
            "   These may not display correctly on all systems or in all applications."
        )
        print("   Some file managers or legacy systems may have compatibility issues.")

    print("  This may break scripts, shortcuts, or other references to these files.")
    print("  It is HIGHLY recommended to run with --dry-run first.")
    print("  Continue? (y/N): ", end="")

    response = input().lower().strip()
    if response != "y":
        print("Operation cancelled.")
        sys.exit(0)


def show_credits() -> None:
    print("🎉 CrossRename - Made by @Jemeni11")
    print("\n📖 Why I built this:")
    print("""
    So I was dual-booting Windows 10 and Lubuntu 22.04, and one day I'm trying to move some files between the two systems.
    Five files just wouldn't copy over because of what I later found out were the differences in Windows and Linux's file
    naming rules.

    That got me thinking because I'd already built a Python package that had to deal with some file creation and renaming (
    It's called [FicImage](https://github.com/Jemeni11/ficimage), please check it out) before, so I had an idea or two
    about how to go about this.

    Long story short, I got annoyed enough to build CrossRename. Now I don't have to deal with file naming headaches when
    switching between systems.

    > WARNING
    >
    > I'm no longer dual booting. I'm using Windows 11 now. I do have WSL2 and that's what I use for testing.
    > I don't know if there'll be any difference in the way the tool works on a native Linux system.
    >
    > macOS support is theoretical but should work since the tool uses the most restrictive ruleset (Windows).
    >
    > If you test on macOS, please report any issues!

    Thank you
    ( ͡• ͜ʖ ͡• )
    """)
    print("\nFind me at:")
    print("  ✦  GitHub: https://github.com/Jemeni11")
    print("  ✦  LinkedIn: https://linkedin.com/in/emmanuel-jemeni")
    print("  ✦  BlueSky: https://bsky.app/profile/jemeni11.bsky.social")
    print("  ✦  Twitter/X: https://twitter.com/Jemeni11_")
    print("\nSupport CrossRename:")
    print("  ✦  Star the repo: https://github.com/Jemeni11/CrossRename")
    print("  ✦  Contribute: PRs and Issues welcome!")
    print("  ✦  Buy me a coffee: https://buymeacoffee.com/jemeni11")
    print("  ✦  GitHub Sponsors: https://github.com/sponsors/Jemeni11")


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="CrossRename: Harmonize file and directory names for Linux, Windows and macOS.",
            epilog="Made with ❤️ by Emmanuel Jemeni | Run --credits to learn more & show support",
        )
        parser.add_argument(
            "-p", "--path", help="The path to the file or directory to rename."
        )
        parser.add_argument(
            "-v",
            "--version",
            help="Prints out the current version and quits.",
            action="version",
            version=f"CrossRename Version {__version__}",
        )
        parser.add_argument(
            "-u",
            "--update",
            help="Check if a new version is available.",
            action="store_true",
        )
        parser.add_argument(
            "-r",
            "--recursive",
            help="Rename all files in the directory path given and its subdirectories. When used with -D, also renames subdirectories.",
            action="store_true",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            help="Perform a dry run, logging changes without renaming.",
            action="store_true",
        )
        parser.add_argument(
            "-D",
            "--rename-directories",
            help="Also rename directories to be cross-platform compatible. Use with caution!",
            action="store_true",
        )
        parser.add_argument(
            "-a",
            "--use-alternatives",
            help="Replace forbidden characters with Unicode lookalikes instead of removing them. May cause display issues on some systems.",
            action="store_true",
        )
        parser.add_argument(
            "--force",
            help="Skip safety prompts (useful for automated scripts)",
            action="store_true",
        )
        parser.add_argument(
            "--credits",
            help="Show credits and support information",
            action="store_true",
        )
        parser.add_argument(
            "--max-filename-bytes",
            type=int,
            default=255,
            metavar="N",
            help="Maximum filename length in bytes (default: 255, valid range: 4-255). "
                 "Filenames exceeding this limit will be truncated. The default of 255 bytes "
                 "ensures compatibility with Linux filesystems (ext4, btrfs). "
                 "Multi-byte characters (CJK, Cyrillic, emoji) consume more bytes per character.",
        )

        args = parser.parse_args()
        path = args.path
        recursive = args.recursive
        dry_run = args.dry_run
        rename_dirs = args.rename_directories
        use_alternatives = args.use_alternatives
        max_bytes = args.max_filename_bytes

        if not (4 <= max_bytes <= 255):
            sys.exit("Error: --max-filename-bytes must be between 4 and 255.")

        if args.update:
            check_for_update(__version__)
            sys.exit()
        if args.credits:
            show_credits()
            sys.exit()

        # Show warning for ANY renaming operation (unless dry-run or force)
        if not dry_run and not args.force:
            if sys.stdout.isatty():
                show_warning(rename_dirs, use_alternatives)
            else:
                sys.exit(
                    "Error: Renaming requires --force flag in non-interactive mode"
                )

        if path is None:
            sys.exit(
                "Error: Please provide a path to a file or directory using the --path argument."
            )

        if os.path.isfile(path):
            rename_file(path, dry_run, use_alternatives, max_bytes)
        elif os.path.isdir(path):
            if recursive:
                # First rename directories (deepest first)
                if rename_dirs:
                    directories = collect_directories(path)
                    for dir_path in directories:
                        rename_directory(dir_path, dry_run, use_alternatives, max_bytes)

                # Then rename files (using updated paths)
                file_list = file_search(path)
                for file_path in file_list:
                    rename_file(file_path, dry_run, use_alternatives, max_bytes)
            else:
                if rename_dirs:
                    path = rename_directory(path, dry_run, use_alternatives, max_bytes)

                # Handle files in the directory
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        rename_file(item_path, dry_run, use_alternatives, max_bytes)
        else:
            sys.exit(f"Error: {path} is not a valid file or directory")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
