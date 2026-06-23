import argparse
import logging
import sys
from pathlib import Path

from .rename import collect_directories, file_search, rename_directory, rename_file
from .utils import check_for_update

__version__ = "1.6.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s » %(message)s")


def show_warning(renaming_directories: bool, use_alternatives: bool = False) -> None:
    if renaming_directories:
        print("⚠️ WARNING: File AND directory renaming is enabled!")
        print("   This may rename the target directory itself and/or subdirectories.")
        print("   Directory renaming will change folder paths and may break external references.")
    else:
        print("⚠️ WARNING: File renaming is enabled!")

    if use_alternatives:
        print("⚠️ WARNING: Unicode alternatives enabled!")
        print("   Special characters will be replaced with similar-looking Unicode characters.")
        print("   These may not display correctly on all systems or in all applications.")
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
    I was dual-booting Windows 10 and Lubuntu 22.04, and one day I'm trying to move some files
    between the two systems. Five files just wouldn't copy over because of what I later found out
    were the differences in Windows and Linux's file naming rules.

    That got me thinking because I'd already built a Python package that had to deal with some file
    creation and renaming (It's called [FicImage](https://github.com/Jemeni11/ficimage), please
    check it out) before, so I had an idea or two about how to go about this.

    Long story short, I got annoyed enough to build CrossRename. Now I don't have to deal with file
    naming headaches when switching between systems.

    WARNING

    I'm no longer dual booting. I'm using Windows 11 now. I do have WSL2 and that's what I use for
    testing. I don't know if there'll be any difference in the way the tool works on a native
    Linux system. macOS support is theoretical but should work since the tool uses the most
    restrictive ruleset (Windows). If you test on macOS, please report any issues!

    Thank you
    """)
    print("Find me at:")
    print("  ✦  GitHub: https://github.com/Jemeni11")
    print("  ✦  GitLab: https://gitlab.com/Jemeni11")
    print("  ✦  LinkedIn: https://linkedin.com/in/emmanuel-jemeni")
    print("  ✦  BlueSky: https://bsky.app/profile/jemeni11.bsky.social")
    print("  ✦  Twitter/X: https://twitter.com/Jemeni11_")
    print("\nSupport CrossRename:")
    print("  ✦  Send Feedback: https://tally.so/r/7Rjpgz?project=CrossRename")
    print("  ✦  Star the repo: https://github.com/Jemeni11/CrossRename")
    print("  ✦  Contribute: PRs and Issues welcome!")
    print("  ✦  Buy me a coffee: https://buymeacoffee.com/jemeni11")
    print("  ✦  GitHub Sponsors: https://github.com/sponsors/Jemeni11")


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="Harmonize file and directory names for Linux, Windows and \
             macOS.",
            epilog="Made with <3 by Emmanuel Jemeni | \
                Send Feedback: https://tally.so/r/7Rjpgz?project=CrossRename",
        )
        parser.add_argument("-p", "--path", help="The path to the file or directory to rename.")
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
            help="Rename all files in the directory path given and its subdirectories. When used\
             with -D, also renames subdirectories.",
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
            help="Replace forbidden characters with Unicode lookalikes instead of removing them.\
                 May cause display issues on some systems.",
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
                sys.exit("Error: Renaming requires --force flag in non-interactive mode")

        if path is None:
            sys.exit(
                "Error: Please provide a path to a file or directory using the --path argument."
            )

        if Path(path).is_file():
            rename_file(Path(path), dry_run, use_alternatives, max_bytes)
        elif Path(path).is_dir():
            if recursive:
                # First rename directories (deepest first)
                if rename_dirs:
                    directories: list[Path] = collect_directories(path)
                    for dir_path in directories:
                        rename_directory(dir_path, dry_run, use_alternatives, max_bytes)

                # Then rename files (using updated paths)
                file_list: list[Path] = file_search(path)
                for file_path in file_list:
                    rename_file(file_path, dry_run, use_alternatives, max_bytes)
            else:
                if rename_dirs:
                    path = rename_directory(Path(path), dry_run, use_alternatives, max_bytes)

                # Handle files in the directory
                for item in Path(path).iterdir():
                    if item.is_file():
                        rename_file(item, dry_run, use_alternatives, max_bytes)
        else:
            sys.exit(f"Error: {path} is not a valid file or directory")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
