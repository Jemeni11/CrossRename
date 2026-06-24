import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crossrename.rename import (
    get_extension,
    rename_directory,
    rename_file,
    sanitize_filename,
)


class TestGetExtension(unittest.TestCase):
    def test_simple_extension(self):
        self.assertEqual(get_extension("file.txt"), ".txt")

    def test_compound_extension(self):
        self.assertEqual(get_extension("archive.tar.gz"), ".tar.gz")

    def test_no_extension(self):
        self.assertEqual(get_extension("README"), "")

    def test_dotfile(self):
        # Path('.gitignore').suffixes returns [] — Python treats it as a stem, not an extension
        self.assertEqual(get_extension(".gitignore"), "")


class TestSanitizeFilenameByteLimit(unittest.TestCase):
    """Tests for byte-aware filename truncation (issue #8)."""

    def test_ascii_at_255_bytes_unchanged(self):
        """255 ASCII chars = 255 bytes, should not be truncated."""
        name = "a" * 251 + ".txt"  # 251 + 4 = 255 bytes
        result = sanitize_filename(name)
        self.assertEqual(result, name)
        self.assertEqual(len(result.encode("utf-8")), 255)

    def test_ascii_exceeding_255_bytes_truncated(self):
        """256+ ASCII chars should be truncated to fit 255 bytes."""
        name = "a" * 260 + ".txt"
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)
        self.assertTrue(result.endswith(".txt"))

    def test_cjk_exceeding_255_bytes(self):
        """CJK chars are 3 bytes each in UTF-8. 100 CJK chars = 300 bytes."""
        name = "中" * 100  # 300 bytes
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)

    def test_cjk_with_extension(self):
        """CJK filename with extension: extension must be preserved."""
        name = "中" * 100 + ".txt"  # 300 + 4 = 304 bytes
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)
        self.assertTrue(result.endswith(".txt"))

    def test_emoji_exceeding_255_bytes(self):
        """Emoji are 4 bytes each in UTF-8. 70 emoji = 280 bytes."""
        name = "😀" * 70
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)

    def test_cyrillic_exceeding_255_bytes(self):
        """Cyrillic chars are 2 bytes each. 200 Cyrillic chars = 400 bytes."""
        name = "щ" * 200
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)

    def test_mixed_ascii_and_multibyte(self):
        """Mixed ASCII + CJK should be byte-counted correctly."""
        # 100 ASCII (100 bytes) + 60 CJK (180 bytes) = 280 bytes
        name = "a" * 100 + "中" * 60
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)

    def test_exactly_255_bytes_unchanged(self):
        """A filename at exactly 255 bytes should not be modified."""
        name = "中" * 85  # 85 * 3 = 255 bytes
        result = sanitize_filename(name)
        self.assertEqual(result, name)
        self.assertEqual(len(result.encode("utf-8")), 255)

    def test_compound_extension_preserved(self):
        """Compound extensions like .tar.gz should be preserved during truncation."""
        name = "中" * 100 + ".tar.gz"  # 300 + 7 = 307 bytes
        result = sanitize_filename(name)
        self.assertLessEqual(len(result.encode("utf-8")), 255)
        self.assertTrue(result.endswith(".tar.gz"))

    def test_custom_max_bytes_lower(self):
        """Custom max_bytes should truncate accordingly."""
        name = "a" * 200
        result = sanitize_filename(name, max_bytes=100)
        self.assertLessEqual(len(result.encode("utf-8")), 100)

    def test_custom_max_bytes_with_extension(self):
        """Custom max_bytes with extension preserved."""
        name = "a" * 200 + ".py"
        result = sanitize_filename(name, max_bytes=50)
        self.assertLessEqual(len(result.encode("utf-8")), 50)
        self.assertTrue(result.endswith(".py"))

    def test_short_filename_unchanged(self):
        """Short filenames should never be truncated."""
        name = "hello.txt"
        result = sanitize_filename(name)
        self.assertEqual(result, name)

    def test_extension_longer_than_max_bytes(self):
        """Extension longer than max_bytes: stem is dropped, extension preserved.

        The CLI enforces max_bytes >= 16, so this path is unreachable via the
        command line.  We test it via direct function call to verify the
        best-effort contract: when the extension alone exceeds the limit, the
        stem is dropped and the extension returned as-is.
        """
        # .tar.gz is 7 bytes; max_bytes=6 means the ext alone exceeds the limit.
        name = "a.tar.gz"
        result = sanitize_filename(name, max_bytes=6)
        self.assertEqual(result, ".tar.gz")


class TestSanitizeFilenameCharacters(unittest.TestCase):
    """Tests for character sanitization (existing behavior)."""

    def test_removes_windows_forbidden_chars(self):
        result = sanitize_filename('file<name>with:bad"chars.txt')
        self.assertEqual(result, "filenamewithbadchars.txt")

    def test_unicode_alternatives_mode(self):
        result = sanitize_filename("file<name>.txt", use_alternatives=True)
        self.assertIn("ᐸ", result)
        self.assertIn("ᐳ", result)

    def test_reserved_names_prefixed(self):
        result = sanitize_filename("CON.txt")
        self.assertEqual(result, "_CON.txt")

    def test_trailing_spaces_and_periods_removed(self):
        result = sanitize_filename("file.txt...")
        self.assertEqual(result, "file.txt")

    def test_empty_after_sanitization(self):
        result = sanitize_filename('<<<>>>"')
        self.assertEqual(result, "unnamed_file")

    def test_control_characters_removed(self):
        result = sanitize_filename("file\x01\x02name.txt")
        self.assertEqual(result, "filename.txt")


class TestQuietMode(unittest.TestCase):
    """Tests for the -q/--quiet flag behavior.

    On Windows, we cannot create files with forbidden characters (<, >, :, etc.)
    directly on disk, so tests that need a simulated rename use
    unittest.mock.patch on sanitize_filename.
    """

    LOGGER_NAME = "crossrename.rename"

    # ── rename_file: suppression ──────────────────────────────────────

    def test_rename_file_quiet_suppresses_no_change_message(self):
        """With quiet=True, a clean file emits NO info-level log output at all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "clean_file.txt"
            file_path.write_text("test content")

            # When quiet=True and the file needs no rename, zero INFO logs
            # are emitted, so assertLogs should raise AssertionError.
            with (
                self.assertRaises(
                    AssertionError, msg="Expected no INFO logs in quiet mode for a clean file"
                ),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO"),
            ):
                rename_file(file_path, quiet=True)

    def test_rename_file_default_logs_no_change_message(self):
        """With quiet=False (default), 'No change needed' is logged for a clean file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "clean_file.txt"
            file_path.write_text("test content")

            with self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm:
                rename_file(file_path)

            log_text = "\n".join(cm.output)
            self.assertIn("No change needed", log_text)
            self.assertIn("clean_file.txt", log_text)

    # ── rename_file: actual renames still logged ──────────────────────

    def test_rename_file_quiet_still_logs_actual_rename(self):
        """With quiet=True, actual rename messages are still emitted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "keep_me.txt"
            file_path.write_text("test content")

            # Mock sanitize_filename to simulate a rename. The real
            # filename is clean (cross-platform safe); the mock makes
            # rename_file think a rename is needed.
            with (
                patch("crossrename.rename.sanitize_filename", return_value="renamed_file.txt"),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm,
            ):
                rename_file(file_path, quiet=True)

            log_text = "\n".join(cm.output)
            self.assertIn("Renamed:", log_text)
            self.assertNotIn("No change needed", log_text)

    def test_rename_file_quiet_dry_run_still_logs_preview(self):
        """Dry-run + quiet still shows rename previews for changed files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "keep_me.txt"
            file_path.write_text("test content")

            with (
                patch("crossrename.rename.sanitize_filename", return_value="renamed_file.txt"),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm,
            ):
                rename_file(file_path, dry_run=True, quiet=True)

            log_text = "\n".join(cm.output)
            self.assertIn("[Dry-run] Would rename:", log_text)
            self.assertNotIn("No change needed", log_text)

    # ── rename_directory: suppression ─────────────────────────────────

    def test_rename_directory_quiet_suppresses_no_change_message(self):
        """With quiet=True, a clean directory emits NO info-level log output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "clean_dir"
            dir_path.mkdir()

            with (
                self.assertRaises(
                    AssertionError, msg="Expected no INFO logs in quiet mode for a clean dir"
                ),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO"),
            ):
                rename_directory(dir_path, quiet=True)

    def test_rename_directory_default_logs_no_change_message(self):
        """With quiet=False (default), 'No change needed for directory' IS logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "clean_dir"
            dir_path.mkdir()

            with self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm:
                rename_directory(dir_path)

            log_text = "\n".join(cm.output)
            self.assertIn("No change needed for directory", log_text)
            self.assertIn("clean_dir", log_text)

    # ── rename_directory: actual renames still logged ─────────────────

    def test_rename_directory_quiet_still_logs_actual_rename(self):
        """With quiet=True, actual directory rename messages are still emitted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "keep_me"
            dir_path.mkdir()

            with (
                patch("crossrename.rename.sanitize_filename", return_value="renamed_dir"),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm,
            ):
                rename_directory(dir_path, quiet=True)

            log_text = "\n".join(cm.output)
            self.assertIn("Renamed directory:", log_text)
            self.assertNotIn("No change needed for directory", log_text)

    # ── integration: mixed quiet + dry-run ────────────────────────────

    def test_dry_run_mixed_quiet_only_shows_changes(self):
        """Dry-run + quiet: rename previews appear, 'No change needed' does not."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Both files actually exist on disk so the test doesn't rely on
            # dry-run coincidentally skipping existence checks.
            dirty_file = Path(tmpdir) / "needs_rename.txt"
            dirty_file.write_text("test")
            clean_file = Path(tmpdir) / "clean.txt"
            clean_file.write_text("test")

            # Mock: the "needs_rename" file gets a different sanitized name;
            # the clean file gets its own name back (no change).
            with (
                patch(
                    "crossrename.rename.sanitize_filename",
                    side_effect=lambda name, *a, **kw: (
                        "renamed.txt" if name == "needs_rename.txt" else name
                    ),
                ),
                self.assertLogs(logger=self.LOGGER_NAME, level="INFO") as cm,
            ):
                rename_file(dirty_file, dry_run=True, quiet=True)
                rename_file(clean_file, dry_run=True, quiet=True)

            log_text = "\n".join(cm.output)
            self.assertIn("[Dry-run] Would rename:", log_text)
            self.assertNotIn("No change needed", log_text)


if __name__ == "__main__":
    unittest.main()
