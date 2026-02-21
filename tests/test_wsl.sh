#!/usr/bin/env bash
# =============================================================================
# CrossRename WSL Integration Test
# =============================================================================
# Tests byte-aware truncation (Issue #8) and standard filename sanitization.
#
# Usage (from WSL or Linux):
#   bash tests/test_wsl.sh [--keep]
#
# Options:
#   --keep    Don't clean up test_files/ after running (for manual inspection)
#
# Requirements:
#   - CrossRename installed (pip install crossrename  OR  pip install -e .)
#   - Python 3
#   - Linux/WSL (ext4 or btrfs filesystem)
# =============================================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

# --- Config ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$PROJECT_DIR/test_files"
KEEP=false
PASS=0; FAIL=0

# --- Parse args ---
for arg in "$@"; do case "$arg" in --keep) KEEP=true;; *) echo -e "${RED}Unknown argument: $arg${NC}"; exit 1;; esac; done

# --- Helpers ---
header() {
    echo ""
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════${NC}"
}
section() { echo ""; echo -e "${YELLOW}--- $1 ---${NC}"; }

check_file_exists() {
    local d="$1" f="$2" desc="$3"
    [ -f "$d/$f" ] && { echo -e "  ${GREEN}✓ PASS${NC}: $desc"; ((PASS++)); } \
                   || { echo -e "  ${RED}✗ FAIL${NC}: $desc ('$f' missing)"; ((FAIL++)); }
}

check_file_absent() {
    local d="$1" f="$2" desc="$3"
    [ ! -f "$d/$f" ] && { echo -e "  ${GREEN}✓ PASS${NC}: $desc"; ((PASS++)); } \
                      || { echo -e "  ${RED}✗ FAIL${NC}: $desc ('$f' remains)"; ((FAIL++)); }
}

check_truncated() {
    local target_dir="$1" prefix="$2" max_bytes="$3" desc="$4"
    for f in "$target_dir/$prefix"*; do
        if [ -f "$f" ]; then
            local name; name="$(basename "$f")"
            local byte_len; byte_len="$(echo -n "$name" | wc -c)"
            if [ "$byte_len" -le "$max_bytes" ]; then
                echo -e "  ${GREEN}✓ PASS${NC}: $desc (${byte_len}/${max_bytes} bytes)"
                ((PASS++)); return
            fi
        fi
    done
    echo -e "  ${RED}✗ FAIL${NC}: $desc (no valid '$prefix*' file found under limit)"
    ((FAIL++))
}

cleanup() {
    if [ "$KEEP" = false ] && [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        echo -e "${YELLOW}Cleaned up $TEST_DIR${NC}"
    fi
}
trap cleanup EXIT

# =============================================================================
# PHASE 1: Setup
# =============================================================================
header "Phase 1: Setup"

[ -d "$TEST_DIR" ] && { echo "Removing previous test_files/..."; rm -rf "$TEST_DIR"; }
mkdir -p "$TEST_DIR"
echo -e "Created test dir: ${BOLD}$TEST_DIR${NC}"

# --- Detect CrossRename ---
section "Detecting CrossRename"
CROSSRENAME=""
USE_WINPATH=false

if command -v crossrename &>/dev/null; then
    CROSSRENAME="crossrename"
elif command -v crossrename.exe &>/dev/null; then
    CROSSRENAME="crossrename.exe"
    USE_WINPATH=true
elif python3 -c "from CrossRename.main import main" &>/dev/null 2>&1; then
    CROSSRENAME="python3 -m CrossRename"
elif python -c "from CrossRename.main import main" &>/dev/null 2>&1; then
    CROSSRENAME="python -m CrossRename"
else
    echo -e "${RED}ERROR: CrossRename not found.${NC}"
    echo "  Install with: pip install crossrename"
    echo "  Or for dev:   pip install -e ."
    exit 1
fi

resolve_path() { [[ "$USE_WINPATH" == true ]] && wslpath -w "$1" || echo "$1"; }

echo -e "Using: ${BOLD}$CROSSRENAME${NC}"
$CROSSRENAME -v

# --- Detect Python ---
section "Detecting Python"
PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED}ERROR: Python not found.${NC}"; exit 1
fi
echo -e "Using: ${BOLD}$PYTHON${NC}"

# =============================================================================
# PHASE 2: Create test files
# =============================================================================
header "Phase 2: Creating test files"

section "Forbidden Windows characters"
touch "$TEST_DIR/file<with>brackets.txt" \
      "$TEST_DIR/file:with:colons.txt" \
      "$TEST_DIR/file?with?questions.txt" \
      "$TEST_DIR/file*with*asterisks.txt" \
      "$TEST_DIR/file|with|pipes.txt" \
      "$TEST_DIR/file\"with\"quotes.txt"
echo "  Created 6 files with forbidden characters ✓"

section "Reserved Windows names"
touch "$TEST_DIR/CON.txt" "$TEST_DIR/NUL.txt" "$TEST_DIR/COM1.txt" \
      "$TEST_DIR/LPT1.txt" "$TEST_DIR/PRN.txt" "$TEST_DIR/AUX.txt"
echo "  Created 6 reserved name files ✓"

section "Control characters"
touch "$TEST_DIR/file$(printf '\x01')ctrl.txt" \
      "$TEST_DIR/file$(printf '\x1f')ctrl2.txt"
echo "  Created 2 control character files ✓"

section "Emoji and CJK filenames (should be unchanged)"
touch "$TEST_DIR/🎉party🎊time.txt" \
      "$TEST_DIR/📁folder📂icon.txt" \
      "$TEST_DIR/日本語ファイル.txt"
echo "  Created 3 emoji/CJK files ✓"

section "Byte truncation (Option 1: custom --max-filename-bytes)"
# All safely under 255 bytes so they create cleanly on ext4/btrfs
LONG_ASCII=$(printf 'a%.0s' {1..250}); touch "$TEST_DIR/${LONG_ASCII}.txt"   # 254 bytes
LONG_CJK=$(printf '中%.0s' {1..83});   touch "$TEST_DIR/${LONG_CJK}.txt"     # 253 bytes
LONG_EMOJI=$(printf '😀%.0s' {1..61}); touch "$TEST_DIR/${LONG_EMOJI}.txt"   # 248 bytes
echo "  Created 3 long files (all <255 bytes, truncated by --max-filename-bytes 100) ✓"

section "Clean files (should be unchanged)"
touch "$TEST_DIR/normal_file.txt" \
      "$TEST_DIR/another-file.md" \
      "$TEST_DIR/.hidden_file"
echo "  Created 3 clean files ✓"

echo ""
echo -e "${BOLD}Total files created: $(ls -1A "$TEST_DIR" | wc -l)${NC}"

# =============================================================================
# PHASE 3: Issue #8 — Extreme byte length verification (mocked)
# =============================================================================
header "Phase 3: Issue #8 Byte Math Verification"
section "Testing extreme CJK/Emoji lengths via sanitize_filename()"

# Note: We verify this by calling the Python function directly because
# files exceeding 255 bytes cannot be created on any standard Linux filesystem
# (ext4/btrfs) or via WSL's Windows drive interop (drvfs), regardless of NTFS.
PHASE3_PASS=true
$PYTHON -c "
import sys
from CrossRename.main import sanitize_filename

tests = [
    ('中' * 120 + '.txt',  255, '120 CJK chars (360 bytes) → ≤255 bytes'),
    ('😀' * 80  + '.txt',  255, '80 Emoji (324 bytes) → ≤255 bytes'),
    ('щ'  * 200 + '.txt',  255, '200 Cyrillic chars (404 bytes) → ≤255 bytes'),
    ('中' * 120 + '.txt',  100, '120 CJK chars with custom limit → ≤100 bytes'),
]

failed = 0
for original, limit, desc in tests:
    result = sanitize_filename(original, max_bytes=limit)
    result_bytes = len(result.encode('utf-8'))
    if result_bytes <= limit:
        print(f'  \u2713 PASS: {desc} (got {result_bytes} bytes)')
    else:
        print(f'  \u2717 FAIL: {desc} (got {result_bytes} bytes, limit {limit})')
        failed += 1

sys.exit(failed)
" || PHASE3_PASS=false

if [ "$PHASE3_PASS" = true ]; then
    ((PASS+=4))
else
    ((FAIL+=1))
fi

# =============================================================================
# PHASE 4: Dry run
# =============================================================================
header "Phase 4: Dry Run"
echo -e "${YELLOW}Running: $CROSSRENAME -p $(resolve_path "$TEST_DIR") -r -d${NC}"
echo ""
$CROSSRENAME -p "$(resolve_path "$TEST_DIR")" -r -d
echo ""

# Verify nothing was renamed during dry run
if [ -f "$TEST_DIR/file<with>brackets.txt" ]; then
    echo -e "  ${GREEN}✓ PASS${NC}: Dry run made no changes"
    ((PASS++))
else
    echo -e "  ${RED}✗ FAIL${NC}: Dry run unexpectedly modified files"
    ((FAIL++))
fi

# =============================================================================
# PHASE 5: Actual rename (standard 255-byte limit)
# =============================================================================
header "Phase 5: Rename — Standard (255 bytes)"
echo -e "${YELLOW}Running: $CROSSRENAME -p $(resolve_path "$TEST_DIR") -r --force${NC}"
echo ""
$CROSSRENAME -p "$(resolve_path "$TEST_DIR")" -r --force

# =============================================================================
# PHASE 6: Rename again (custom 100-byte limit)
# =============================================================================
header "Phase 6: Rename — Custom (--max-filename-bytes 100)"
echo -e "${YELLOW}Running: $CROSSRENAME -p $(resolve_path "$TEST_DIR") --max-filename-bytes 100 --force${NC}"
echo ""
$CROSSRENAME -p "$(resolve_path "$TEST_DIR")" --max-filename-bytes 100 --force

# =============================================================================
# PHASE 7: Verification
# =============================================================================
header "Phase 7: Verification"

section "Forbidden characters removed"
check_file_exists "$TEST_DIR" "filewithbrackets.txt"    "Angle brackets removed"
check_file_absent "$TEST_DIR" "file<with>brackets.txt"  "Original bracket file gone"
check_file_exists "$TEST_DIR" "filewithcolons.txt"      "Colons removed"
check_file_exists "$TEST_DIR" "filewithquestions.txt"   "Question marks removed"
check_file_exists "$TEST_DIR" "filewithasterisks.txt"   "Asterisks removed"
check_file_exists "$TEST_DIR" "filewithpipes.txt"       "Pipes removed"
check_file_exists "$TEST_DIR" "filewithquotes.txt"      "Quotes removed"

section "Reserved names prefixed"
check_file_exists "$TEST_DIR" "_CON.txt"   "CON  → _CON"
check_file_exists "$TEST_DIR" "_NUL.txt"   "NUL  → _NUL"
check_file_exists "$TEST_DIR" "_COM1.txt"  "COM1 → _COM1"
check_file_exists "$TEST_DIR" "_LPT1.txt"  "LPT1 → _LPT1"
check_file_exists "$TEST_DIR" "_PRN.txt"   "PRN  → _PRN"
check_file_exists "$TEST_DIR" "_AUX.txt"   "AUX  → _AUX"

section "Control characters removed"
check_file_exists "$TEST_DIR" "filectrl.txt"   "Control char (0x01) removed"
check_file_exists "$TEST_DIR" "filectrl2.txt"  "Control char (0x1f) removed"

section "Emoji/CJK filenames preserved"
check_file_exists "$TEST_DIR" "🎉party🎊time.txt"   "Emoji filename preserved"
check_file_exists "$TEST_DIR" "📁folder📂icon.txt"   "Emoji filename preserved"
check_file_exists "$TEST_DIR" "日本語ファイル.txt"       "CJK filename preserved"

section "Byte truncation (--max-filename-bytes 100)"
check_truncated "$TEST_DIR" "中" 100 "CJK (253 bytes) truncated to ≤100 bytes"
check_truncated "$TEST_DIR" "😀" 100 "Emoji (248 bytes) truncated to ≤100 bytes"
check_truncated "$TEST_DIR" "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" 100 "ASCII (254 bytes) truncated to ≤100 bytes"

section "Clean files unchanged"
check_file_exists "$TEST_DIR" "normal_file.txt"  "normal_file.txt unchanged"
check_file_exists "$TEST_DIR" "another-file.md"  "another-file.md unchanged"
check_file_exists "$TEST_DIR" ".hidden_file"     ".hidden_file unchanged"

# =============================================================================
# Summary
# =============================================================================
header "Results"
echo -e "  ${GREEN}Passed: $PASS${NC}  ${RED}Failed: $FAIL${NC}"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ All tests passed!${NC} 🎉"
    exit 0
else
    echo -e "${RED}${BOLD}❌ $FAIL test(s) failed.${NC}"
    exit 1
fi
