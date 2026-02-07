<a id="readme-top"></a>

<br />
<div align="center">
  <a href="https://github.com/Jemeni11/CrossRename"><img src="logo.png" alt="Logo" width="128" height="128"></a>

<h3 align="center">CrossRename</h3>

  <p align="center">
    Harmonize file and directory names for Linux, Windows, and macOS.
    <br />
    <a href="https://github.com/Jemeni11/CrossRename"><strong>Explore the repo »</strong></a>
    <br />
  </p>
</div>

Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [From PyPI (Using PIP)](#from-pypi-using-pip)
- [Usage](#usage)
  - [Examples](#examples)
  - [Unicode Alternatives Mode](#unicode-alternatives-mode)
  - [Safety First](#safety-first)
- [Platform Compatibility](#platform-compatibility)
- [Why did I build this?](#why-did-i-build-this)
- [Contributing](#contributing)
- [Wait a minute, who are you?](#wait-a-minute-who-are-you)
- [License](#license)
- [Changelog](#changelog)

## Introduction

CrossRename is a command-line tool designed to harmonize file and directory names across Linux, Windows, and macOS systems.
It ensures that your file names are compatible with all three operating systems, eliminating naming conflicts
when transferring files between different environments.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- Sanitizes file names to be Windows-compatible (and thus Linux-compatible and macOS-compatible)
- Option to replace forbidden characters with Unicode lookalikes instead of removing them
- Optionally renames directories to be cross-platform compatible
- Handles both individual files and entire directories
- Supports recursive renaming of files in subdirectories
- Preserves file extensions, including compound extensions like .tar.gz
- Provides informative logging
- Provides a dry-run mode to preview renaming changes without executing them
- Interactive safety warnings with option to skip for automation
- Skips recursive symlinks to avoid infinite loops

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation

### From PyPI (Using PIP)

```bash
pip install CrossRename
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Other package managers coming soon.

## Usage

```bash
usage: crossrename [-h] [-p PATH] [-v] [-u] [-r] [-d] [-D] [-a] [--force] [--credits]

CrossRename: Harmonize file and directory names for Linux, Windows and macOS.

options:
  -h, --help                  show this help message and exit
  -p, --path PATH             The path to the file or directory to rename.
  -v, --version               Prints out the current version and quits.
  -u, --update                Check if a new version is available.
  -r, --recursive             Rename all files in the directory path given and its subdirectories. When used with -D, also renames subdirectories.
  -d, --dry-run               Perform a dry run, logging changes without renaming.
  -D, --rename-directories    Also rename directories to be cross-platform compatible. Use with caution!
  -a, --use-alternatives      Replace forbidden characters with Unicode lookalikes instead of removing them. May cause display issues on some systems.
  --force                     Skip safety prompts (useful for automated scripts)
  --credits                   Show credits and support information
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Examples

Rename a single file:

```bash
crossrename -p /path/to/file.txt
```

Rename all files in a directory (and its subdirectories):

```bash
crossrename -p /path/to/directory -r
```

Rename all files AND directories recursively:

```bash
crossrename -p /path/to/directory -r -D
```

Rename a single directory:

```bash
crossrename -p /path/to/problematic_directory -D
```

Perform a dry run to preview renaming changes without executing them:

```bash
crossrename -p /path/to/directory -r -D -d
```

Skip safety prompts for automated scripts:

```bash
crossrename -p /path/to/directory -r -D --force
```

Use [Unicode alternatives](#unicode-alternatives-mode) instead of removing characters:

```bash
crossrename -p /path/to/file.txt -a
```

Check for an update:

```bash
crossrename -u
```

Show credits and project information:

```bash
crossrename --credits
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Unicode Alternatives Mode

Use `--use-alternatives` to replace forbidden characters with similar Unicode characters instead of removing them:

```bash
crossrename -p "file<name>.txt" --use-alternatives
# Result: "fileᐸnameᐳ.txt" instead of "filename.txt"
```

Character mappings:

- `<` → `ᐸ` (Canadian Syllabics Pa)
- `>` → `ᐳ` (Canadian Syllabics Po)
- `:` → `∶` (Ratio)
- `"` → `ʺ` (Modified Letter Double Prime)
- `/` → `∕` (Division Slash)
- `\` → `⧵` (Reverse Solidus Operator)
- `|` → `∣` (Divides)
- `?` → `﹖` (Small Question Mark)
- `*` → `🞱` (Bold Five Spoked Asterisk)

> [!WARNING]
>
> These Unicode characters may not display correctly on all systems, fonts, or applications.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Safety First

> [!WARNING]  
> Always run with `--dry-run` first!

CrossRename will show interactive safety warnings before making any changes to help prevent accidental data loss.
However, it's strongly recommended to:

1. **Run a dry run first** to preview what will be changed:

   ```bash
   crossrename -p /your/path -r -D -d
   ```

2. **Backup your data** before running the tool on important files

3. **Use `--force` flag** for automation in CI/CD pipelines:

   ```bash
   crossrename -p /your/path -r -D --force
   ```

Directory renaming is particularly powerful and potentially disruptive since it changes folder paths that other
applications might reference.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Platform Compatibility

CrossRename works on:

- **Windows**
- **Linux**
- **macOS**

The tool sanitizes filenames to be compatible with the *most restrictive* filesystem (Windows),
ensuring files work everywhere. This means:

- Removing Windows-forbidden characters: `< > : " / \ | ? *`
- Handling Windows reserved names: CON, PRN, AUX, NUL, COM1-9, LPT1-9
- Removing trailing spaces and periods
- Limiting filenames to 255 characters
- Removing control characters

Since Windows has the strictest rules, files renamed by CrossRename will work on Linux and macOS without issues.

> [!IMPORTANT]
>
> If files were created on Linux or macOS with Windows-forbidden characters (like `<`, `>`, `:`, etc.), Windows cannot see those characters—the filenames appear mangled or stripped. To fix these files, you must run CrossRename from the originating OS (or WSL for Linux files), not from Windows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Why did I build this?

So I was dual-booting Windows 10 and Lubuntu 22.04, and one day I'm trying to move some files between the two systems.
Five files just wouldn't copy over because of what I later found out were the differences in Windows and Linux's file
naming rules.

That got me thinking because I'd already built a Python package that had to deal with some file creation and renaming (
It's called [FicImage](https://github.com/Jemeni11/ficimage), please check it out 🫶) before, so I had an idea or two
about how to go about this.

Long story short, I got annoyed enough to build CrossRename. Now I don't have to deal with file naming headaches when
switching between systems.

> [!NOTE]
>
> I'm no longer dual booting. I'm using Windows 11 now. I do have WSL2 and that's what I use for testing. I don't know if there'll be any difference in the way the tool works on a native Linux system.
>
> macOS support is theoretical but should work since the tool uses the most restrictive ruleset (Windows).
>
> If you test on macOS, please report any issues!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are welcome! If you'd like to improve CrossRename please feel free to submit a pull request.

**Especially welcome:**

- macOS/APFS testing and feedback (currently untested on real macOS hardware)
- Linux testing and feedback (on native linux)
- Edge case handling for Unicode normalization differences
- Performance improvements for large directory trees
- Other Operating Systems
- Any other thing I forgot to list here

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Wait a minute, who are you?

Hello there! I'm Emmanuel Jemeni, and while I primarily work as a Frontend Developer,
Python holds a special place as my first programming language.
You can find me on various platforms:

- [LinkedIn](https://www.linkedin.com/in/emmanuel-jemeni)
- [GitHub](https://github.com/Jemeni11)
- [BlueSky](https://bsky.app/profile/jemeni11.bsky.social)
- [Twitter/X](https://twitter.com/Jemeni11_)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

[MIT License](LICENSE)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Changelog

[Changelog](/CHANGELOG.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
