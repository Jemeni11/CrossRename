import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


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
    if re.match(reserved_names, sanitized, re.IGNORECASE):
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
    file_path: Path, dry_run: bool = False, use_alternatives: bool = False, max_bytes: int = 255
) -> None:
    directory, filename = file_path.parent, file_path.name
    new_filename = sanitize_filename(filename, use_alternatives, max_bytes)

    if new_filename != filename:
        new_file_path = directory / new_filename

        # Check if target already exists (collision prevention)
        if new_file_path.exists() and Path(file_path).resolve() != new_file_path.resolve():
            # Target exists and is a different file - add suffix
            base_name, ext = Path(new_filename).stem, Path(new_filename).suffix
            counter = 1
            while new_file_path.exists():
                new_filename = f"{base_name}_{counter}{ext}"
                new_file_path = directory / new_filename
                counter += 1
            logger.warning(f"Target exists, using: {new_filename}")

        if dry_run:
            logger.info(f"[Dry-run] Would rename: {filename} -> {new_filename}")
        else:
            try:
                # Check if file still exists before rename (TOCTOU mitigation)
                if not file_path.exists():
                    logger.warning(f"File no longer exists, skipping: {filename}")
                    return

                file_path.rename(new_file_path)
                logger.info(f"Renamed: {filename} -> {new_filename}")
            except FileNotFoundError:
                logger.warning(f"File was deleted by another process: {filename}")
            except PermissionError:
                logger.error(f"Permission denied for {filename}")
            except FileExistsError:
                logger.error(f"Target file already exists (race condition): {new_filename}")
            except Exception as e:
                logger.error(f"Error renaming {filename}: {str(e)}")
    else:
        logger.info(f"No change needed: {filename}")


def file_search(directory: str) -> list[Path]:
    file_list: list[Path] = []
    visited_paths: set[Path] = set()

    for root, _, files in Path(directory).walk(follow_symlinks=False):
        real_root = root.resolve()

        if real_root in visited_paths:
            logger.warning(f"Skipping recursive symlink in {root}")
            continue

        visited_paths.add(real_root)

        for file in files:
            file_path = root / file
            if file_path.is_symlink():
                logger.info(f"Skipping symlink: {file_path}")
                continue
            file_list.append(file_path)

    return file_list


def collect_directories(directory: str) -> list[Path]:
    """Collect all directories, sorted by depth (deepest first)"""
    directories: list[Path] = []
    for root, dirs, _ in Path(directory).walk(follow_symlinks=False):
        for dir_name in dirs:
            dir_path = root / dir_name
            if not dir_path.is_symlink():  # Skip symlinked directories
                directories.append(dir_path)

    # Sort by depth (deepest first) to avoid path breakage
    return sorted(directories, key=lambda x: len(x.parts), reverse=True)


def rename_directory(
    dir_path: Path, dry_run: bool = False, use_alternatives: bool = False, max_bytes: int = 255
) -> Path:
    """Rename directory and return the new path"""
    parent_dir, dir_name = dir_path.parent, dir_path.name
    new_dir_name = sanitize_filename(dir_name, use_alternatives, max_bytes)

    if new_dir_name != dir_name:
        new_dir_path = parent_dir / new_dir_name
        if dry_run:
            logger.info(f"[Dry-run] Would rename directory: {dir_name} -> {new_dir_name}")
            return new_dir_path  # Return what the path would be
        try:
            dir_path.rename(new_dir_path)
            logger.info(f"Renamed directory: {dir_name} -> {new_dir_name}")
            return new_dir_path
        except Exception as e:
            logger.error(f"Error renaming directory {dir_name}: {str(e)}")
            return dir_path  # Return original path if rename failed
    else:
        logger.info(f"No change needed for directory: {dir_name}")
        return dir_path
