from crossrename.rename import get_extension, sanitize_filename


class TestGetExtension:
    def test_simple_extension(self):
        assert get_extension("file.txt") == ".txt"

    def test_compound_extension(self):
        assert get_extension("archive.tar.gz") == ".tar.gz"

    def test_no_extension(self):
        assert get_extension("README") == ""

    def test_dotfile(self):
        # Path('.gitignore').suffixes returns [] — Python treats it as a stem, not an extension
        assert get_extension(".gitignore") == ""


class TestSanitizeFilenameByteLimit:
    """Tests for byte-aware filename truncation (issue #8)."""

    def test_ascii_at_255_bytes_unchanged(self):
        """255 ASCII chars = 255 bytes, should not be truncated."""
        name = "a" * 251 + ".txt"  # 251 + 4 = 255 bytes
        result = sanitize_filename(name)
        assert result == name
        assert len(result.encode("utf-8")) == 255

    def test_ascii_exceeding_255_bytes_truncated(self):
        """256+ ASCII chars should be truncated to fit 255 bytes."""
        name = "a" * 260 + ".txt"
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        assert result.endswith(".txt")

    def test_cjk_exceeding_255_bytes(self):
        """CJK chars are 3 bytes each in UTF-8. 100 CJK chars = 300 bytes."""
        name = "中" * 100  # 300 bytes
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        # Should be ~85 characters (85 * 3 = 255)
        assert len(result) == 85

    def test_cjk_with_extension(self):
        """CJK filename with extension: extension must be preserved."""
        name = "中" * 100 + ".txt"  # 300 + 4 = 304 bytes
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        assert result.endswith(".txt")

    def test_emoji_exceeding_255_bytes(self):
        """Emoji are 4 bytes each in UTF-8. 70 emoji = 280 bytes."""
        name = "😀" * 70
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        # Should be ~63 characters (63 * 4 = 252)
        assert len(result) == 63

    def test_cyrillic_exceeding_255_bytes(self):
        """Cyrillic chars are 2 bytes each. 200 Cyrillic chars = 400 bytes."""
        name = "щ" * 200
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        # Should be ~127 characters (127 * 2 = 254)
        assert len(result) == 127

    def test_mixed_ascii_and_multibyte(self):
        """Mixed ASCII + CJK should be byte-counted correctly."""
        # 100 ASCII (100 bytes) + 60 CJK (180 bytes) = 280 bytes
        name = "a" * 100 + "中" * 60
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255

    def test_exactly_255_bytes_unchanged(self):
        """A filename at exactly 255 bytes should not be modified."""
        name = "中" * 85  # 85 * 3 = 255 bytes
        result = sanitize_filename(name)
        assert result == name
        assert len(result.encode("utf-8")) == 255

    def test_compound_extension_preserved(self):
        """Compound extensions like .tar.gz should be preserved during truncation."""
        name = "中" * 100 + ".tar.gz"  # 300 + 7 = 307 bytes
        result = sanitize_filename(name)
        assert len(result.encode("utf-8")) <= 255
        assert result.endswith(".tar.gz")

    def test_custom_max_bytes_lower(self):
        """Custom max_bytes should truncate accordingly."""
        name = "a" * 200
        result = sanitize_filename(name, max_bytes=100)
        assert len(result.encode("utf-8")) <= 100
        assert len(result) == 100

    def test_custom_max_bytes_with_extension(self):
        """Custom max_bytes with extension preserved."""
        name = "a" * 200 + ".py"
        result = sanitize_filename(name, max_bytes=50)
        assert len(result.encode("utf-8")) <= 50
        assert result.endswith(".py")

    def test_short_filename_unchanged(self):
        """Short filenames should never be truncated."""
        name = "hello.txt"
        result = sanitize_filename(name)
        assert result == name


class TestSanitizeFilenameCharacters:
    """Tests for character sanitization (existing behavior)."""

    def test_removes_windows_forbidden_chars(self):
        result = sanitize_filename('file<name>with:bad"chars.txt')
        assert result == "filenamewithbadchars.txt"

    def test_unicode_alternatives_mode(self):
        result = sanitize_filename("file<name>.txt", use_alternatives=True)
        assert "ᐸ" in result
        assert "ᐳ" in result

    def test_reserved_names_prefixed(self):
        result = sanitize_filename("CON.txt")
        assert result == "_CON.txt"

    def test_trailing_spaces_and_periods_removed(self):
        result = sanitize_filename("file.txt...")
        assert result == "file.txt"

    def test_empty_after_sanitization(self):
        result = sanitize_filename('<<<>>>"')
        assert result == "unnamed_file"

    def test_control_characters_removed(self):
        result = sanitize_filename("file\x01\x02name.txt")
        assert result == "filename.txt"
