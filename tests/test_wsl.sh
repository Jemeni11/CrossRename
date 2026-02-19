#!/usr/bin/env bash
# =============================================================================
# CrossRename WSL Integration Test
# =============================================================================
# Creates files with Windows-incompatible names on a Linux filesystem,
# runs CrossRename against them, and verifies the results.
#
# Usage (from WSL):
#   cd /mnt/c/Users/HP/Documents/Code/CrossRename
#   bash tests/test_wsl.sh [--keep]
#
# From PowerShell:
#   wsl bash -c "cd /mnt/c/Users/HP/Documents/Code/CrossRename && bash tests/test_wsl.sh"
#
# Options:
#   --keep    Don't clean up test_files/ after running (for manual inspection)
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Config ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$PROJECT_DIR/test_files"
KEEP=false
PASS=0
FAIL=0

# --- Parse args ---
for arg in "$@"; do
    case "$arg" in
        --keep) KEEP=true ;;
        *) echo -e "${RED}Unknown argument: $arg${NC}"; exit 1 ;;
    esac
done

# --- Helpers ---
header() {
    echo ""
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════${NC}"
}

section() {
    echo ""
    echo -e "${YELLOW}--- $1 ---${NC}"
}

check_file_exists() {
    local file="$1"
    local description="$2"
    if [ -f "$TEST_DIR/$file" ]; then
        echo -e "  ${GREEN}✓ PASS${NC}: $description → '$file' exists"
        ((PASS++))
    else
        echo -e "  ${RED}✗ FAIL${NC}: $description → '$file' not found"
        ((FAIL++))
    fi
}

check_file_absent() {
    local file="$1"
    local description="$2"
    if [ ! -f "$TEST_DIR/$file" ]; then
        echo -e "  ${GREEN}✓ PASS${NC}: $description → '$file' correctly removed/renamed"
        ((PASS++))
    else
        echo -e "  ${RED}✗ FAIL${NC}: $description → '$file' still exists (should have been renamed)"
        ((FAIL++))
    fi
}

# Verify that a file matching the prefix exists and its name is within the byte limit
check_truncated() {
    local prefix="$1"
    local max_bytes="$2"
    local description="$3"
    local found=false
    for f in "$TEST_DIR/$prefix"*; do
        if [ -f "$f" ]; then
            local basename
            basename=$(basename "$f")
            local byte_len
            byte_len=$(echo -n "$basename" | wc -c)
            if [ "$byte_len" -le "$max_bytes" ]; then
                echo -e "  ${GREEN}✓ PASS${NC}: $description → '${basename}' (${byte_len} bytes ≤ ${max_bytes})"
                ((PASS++))
            else
                echo -e "  ${RED}✗ FAIL${NC}: $description → '${basename}' is ${byte_len} bytes (limit: ${max_bytes})"
                ((FAIL++))
            fi
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        echo -e "  ${RED}✗ FAIL${NC}: $description → no file matching '${prefix}*' found"
        ((FAIL++))
    fi
}

cleanup() {
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        echo -e "${YELLOW}Cleaned up $TEST_DIR${NC}"
    fi
}

# --- Cleanup on exit (unless --keep) ---
if [ "$KEEP" = false ]; then
    trap cleanup EXIT
fi

# =============================================================================
# PHASE 1: Setup
# =============================================================================
header "Phase 1: Setup"

# Clean any previous test run
if [ -d "$TEST_DIR" ]; then
    echo "Removing previous test_files/..."
    rm -rf "$TEST_DIR"
fi

mkdir -p "$TEST_DIR"
echo -e "Created ${BOLD}$TEST_DIR${NC}"

# Detect CrossRename command
section "Detecting CrossRename"
cd "$PROJECT_DIR"
CROSSRENAME=""
USE_WINPATH=false
if command -v crossrename &>/dev/null; then
    CROSSRENAME="crossrename"
elif command -v crossrename.exe &>/dev/null; then
    CROSSRENAME="crossrename.exe"
    USE_WINPATH=true
elif python3 -c "from CrossRename.main import main" &>/dev/null 2>&1; then
    CROSSRENAME="python3 -m CrossRename.main"
elif python -c "from CrossRename.main import main" &>/dev/null 2>&1; then
    CROSSRENAME="python -m CrossRename.main"
else
    echo -e "${RED}ERROR: CrossRename not found.${NC}"
    echo "  Install it with: pip install -e .  (or pip install CrossRename)"
    exit 1
fi

# Convert paths for Windows executables running via WSL interop
resolve_path() {
    if [ "$USE_WINPATH" = true ]; then
        wslpath -w "$1"
    else
        echo "$1"
    fi
}

echo -e "Using: ${BOLD}$CROSSRENAME${NC}"
$CROSSRENAME -v

# =============================================================================
# PHASE 2: Create test files
# =============================================================================
header "Phase 2: Creating test files"

section "Forbidden Windows characters"
touch "$TEST_DIR/file<with>brackets.txt"
touch "$TEST_DIR/file:with:colons.txt"
touch "$TEST_DIR/file\"with\"quotes.txt"
touch "$TEST_DIR/file|with|pipes.txt"
touch "$TEST_DIR/file?with?questions.txt"
touch "$TEST_DIR/file*with*asterisks.txt"
echo "  Created 6 files with forbidden characters"

section "Trailing spaces and periods"
touch "$TEST_DIR/trailing_space .txt"
touch "$TEST_DIR/trailing_period..txt"
echo "  Created 2 files with trailing spaces/periods"

section "Reserved Windows names"
touch "$TEST_DIR/CON.txt"
touch "$TEST_DIR/NUL.txt"
touch "$TEST_DIR/COM1.txt"
touch "$TEST_DIR/LPT1.txt"
touch "$TEST_DIR/PRN.txt"
touch "$TEST_DIR/AUX.txt"
echo "  Created 6 files with reserved names"

section "Control characters"
touch "$TEST_DIR/file$(printf '\x01')ctrl.txt"
touch "$TEST_DIR/file$(printf '\x1f')ctrl2.txt"
echo "  Created 2 files with control characters"

section "Emoji filenames"
touch "$TEST_DIR/🎉party🎊time.txt"
touch "$TEST_DIR/📁folder📂icon.txt"
touch "$TEST_DIR/日本語ファイル.txt"
echo "  Created 3 files with emoji/CJK characters"

section "Filename truncation (byte limit)"
# 300 ASCII chars + .txt = 304 bytes (exceeds 255)
LONG_ASCII=$(printf 'a%.0s' $(seq 1 300))
touch "$TEST_DIR/${LONG_ASCII}.txt"
# 100 CJK chars = 300 bytes (each is 3 bytes in UTF-8)
LONG_CJK=$(printf '中%.0s' $(seq 1 100))
touch "$TEST_DIR/${LONG_CJK}.txt"
# 70 emoji = 280 bytes (each is 4 bytes in UTF-8)
LONG_EMOJI=$(printf '😀%.0s' $(seq 1 70))
touch "$TEST_DIR/${LONG_EMOJI}.txt"
# Long name with compound extension
LONG_TAR=$(printf 'b%.0s' $(seq 1 300))
touch "$TEST_DIR/${LONG_TAR}.tar.gz"
echo "  Created 4 files exceeding 255-byte limit"

section "Combination of issues"
touch "$TEST_DIR/bad<name>:file?.txt"
touch "$TEST_DIR/CON:bad|name .txt"
echo "  Created 2 files with multiple issues"

section "Files that should NOT change"
touch "$TEST_DIR/normal_file.txt"
touch "$TEST_DIR/another-file.md"
touch "$TEST_DIR/.hidden_file"
echo "  Created 3 clean files (should be unchanged)"

echo ""
echo -e "${BOLD}Total files created: $(ls -1A "$TEST_DIR" | wc -l)${NC}"

# =============================================================================
# PHASE 3: Dry run
# =============================================================================
header "Phase 3: Dry Run"

echo -e "${YELLOW}Running: $CROSSRENAME -p $(resolve_path "$TEST_DIR") -r -d${NC}"
echo ""
$CROSSRENAME -p "$(resolve_path "$TEST_DIR")" -r -d
echo ""
echo -e "${GREEN}Dry run complete. No files were renamed.${NC}"

# Verify nothing actually changed in dry run
section "Verifying dry run didn't rename anything"
if [ -f "$TEST_DIR/file<with>brackets.txt" ]; then
    echo -e "  ${GREEN}✓ PASS${NC}: Dry run did not modify files"
    ((PASS++))
else
    echo -e "  ${RED}✗ FAIL${NC}: Dry run modified files unexpectedly"
    ((FAIL++))
fi

# =============================================================================
# PHASE 4: Actual rename
# =============================================================================
header "Phase 4: Actual Rename"

echo -e "${YELLOW}Running: $CROSSRENAME -p $(resolve_path "$TEST_DIR") -r --force${NC}"
echo ""
$CROSSRENAME -p "$(resolve_path "$TEST_DIR")" -r --force
echo ""

# =============================================================================
# PHASE 5: Verify results
# =============================================================================
header "Phase 5: Verification"

section "Forbidden characters removed"
check_file_exists  "filewithbrackets.txt"       "Angle brackets removed"
check_file_absent  "file<with>brackets.txt"      "Original with brackets gone"
check_file_exists  "filewithcolons.txt"          "Colons removed"
check_file_absent  "file:with:colons.txt"        "Original with colons gone"
check_file_exists  "filewithquotes.txt"          "Quotes removed"
check_file_absent  'file"with"quotes.txt'        "Original with quotes gone"
check_file_exists  "filewithpipes.txt"           "Pipes removed"
check_file_absent  "file|with|pipes.txt"         "Original with pipes gone"
check_file_exists  "filewithquestions.txt"       "Question marks removed"
check_file_absent  "file?with?questions.txt"     "Original with questions gone"
check_file_exists  "filewithasterisks.txt"       "Asterisks removed"
check_file_absent  "file*with*asterisks.txt"     "Original with asterisks gone"

section "Trailing spaces and periods"
check_file_exists  "trailing_space.txt"          "Trailing space removed"
check_file_absent  "trailing_space .txt"         "Original with trailing space gone"
check_file_exists  "trailing_period.txt"         "Trailing periods removed"

section "Reserved names prefixed"
check_file_exists  "_CON.txt"                    "CON prefixed with underscore"
check_file_absent  "CON.txt"                     "Original CON.txt gone"
check_file_exists  "_NUL.txt"                    "NUL prefixed with underscore"
check_file_absent  "NUL.txt"                     "Original NUL.txt gone"
check_file_exists  "_COM1.txt"                   "COM1 prefixed with underscore"
check_file_absent  "COM1.txt"                    "Original COM1.txt gone"
check_file_exists  "_LPT1.txt"                   "LPT1 prefixed with underscore"
check_file_absent  "LPT1.txt"                    "Original LPT1.txt gone"
check_file_exists  "_PRN.txt"                    "PRN prefixed with underscore"
check_file_absent  "PRN.txt"                     "Original PRN.txt gone"
check_file_exists  "_AUX.txt"                    "AUX prefixed with underscore"
check_file_absent  "AUX.txt"                     "Original AUX.txt gone"

section "Control characters"
check_file_exists  "filectrl.txt"                "Control char removed"
check_file_exists  "filectrl2.txt"               "Control char removed"

section "Emoji/CJK filenames (should be unchanged)"
check_file_exists  "🎉party🎊time.txt"           "Emoji filename preserved"
check_file_exists  "📁folder📂icon.txt"           "Emoji filename preserved"
check_file_exists  "日本語ファイル.txt"              "CJK filename preserved"

section "Filename truncation"
check_truncated  "aaaa"  255  "Long ASCII filename truncated to ≤255 bytes"
check_truncated  "中"    255  "Long CJK filename truncated to ≤255 bytes"
check_truncated  "😀"   255  "Long emoji filename truncated to ≤255 bytes"
check_truncated  "bbbb"  255  "Long filename with .tar.gz truncated to ≤255 bytes"

section "Combination files"
check_file_exists  "badnamefile.txt"             "Multiple forbidden chars removed"
check_file_absent  "bad<name>:file?.txt"         "Original combo file gone"

section "Clean files unchanged"
check_file_exists  "normal_file.txt"             "Normal file unchanged"
check_file_exists  "another-file.md"             "Normal file unchanged"
check_file_exists  ".hidden_file"                "Hidden file unchanged"

# =============================================================================
# Summary
# =============================================================================
header "Results"

echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ -d "$TEST_DIR" ]; then
    echo -e "${BOLD}Remaining files in test_files/:${NC}"
    ls -1A "$TEST_DIR"
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}All tests passed!${NC} 🎉"
    exit 0
else
    echo -e "${RED}${BOLD}$FAIL test(s) failed.${NC}"
    exit 1
fi
