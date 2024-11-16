<a id="readme-top"></a>

<br />
<div align="center">
  <a href="https://github.com/Jemeni11/CrossRename"><img src="logo.png" alt="Logo" width="128" height="128"></a>

<h3 align="center">CrossRename</h3>

  <p align="center">
    Harmonize file names for Linux and Windows.
    <br />
    <a href="https://github.com/Jemeni11/CrossRename"><strong>Explore the repo »</strong></a>
    <br />
  </p>
</div>

Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Examples](#examples)
- [Why did I build this?](#why-did-i-build-this)
- [Contributing](#contributing)
- [Wait a minute, who are you?](#wait-a-minute-who-are-you)
- [License](#license)
- [Changelog](#changelog)

## Introduction

CrossRename is a command-line tool designed to harmonize file names across Linux and Windows systems.
It ensures that your file names are compatible with both operating systems, eliminating naming conflicts
when transferring files between different environments.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- Sanitizes file names to be Windows-compatible (and thus Linux-compatible)
- Handles both individual files and entire directories
- Supports recursive renaming of files in subdirectories
- Preserves file extensions, including compound extensions like .tar.gz
- Provides informative logging
- Provides a dry-run mode to preview renaming changes without executing them
- Skips recursive symlinks to avoid infinite loops

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation

### From PyPI (Using PIP)

```
pip install CrossRename
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

```
usage: crossrename [-h] [-p PATH] [-v] [-u] [-r] [-d]

CrossRename: Harmonize file names for Linux and Windows.

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  The path to the file or directory to rename.
  -v, --version         Prints out the current version and quits.
  -u, --update          Check if a new version is available.
  -r, --recursive       Rename all files in the directory path given and its subdirectories.
  -d, --dry-run         Perform a dry run, logging changes without renaming.


```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Examples

Rename a single file:

```
crossrename -p /path/to/file.txt
```

Rename all files in a directory (and its subdirectories ):

```
crossrename -p /path/to/directory -r
```

Perform a dry run to preview renaming changes without executing them:

```
crossrename -p /path/to/directory -r -d
```

Check for an update:

```
crossrename -u
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Why did I build this?

> [!WARNING]
>
> I'm no longer dual booting. I'm only using Windows 10 now. I do have WSL2 and that's what I use for testing.
> I don't know if there'll be any difference in the way the tool works on a native Linux system.

I'm a dual-booter running Windows 10 and Lubuntu 22.04. One day (literally yesterday lol), while transferring a
folder between the two systems, I hit a naming roadblock. Five stubborn files refused to budge,
thanks to the quirky differences in file naming rules between Linux and Windows.

This experience got me thinking. You see, I had previously built [FicImage](https://github.com/Jemeni11/ficimage),
a nifty application that elevates the reading experience of [FicHub](https://fichub.net/) epubs by adding missing
images. It required handling file creation and renaming, and that knowledge proved invaluable.

And so, CrossRename was born – a tool to simplify your life when managing files between Linux and
Windows. No more naming hassles, just smooth, worry-free file management.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are welcome! If you'd like to improve CrossRename or add support for
other operating systems (like macOS), please feel free to submit a pull request.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Wait a minute, who are you?

Hello there! I'm Emmanuel Jemeni, and while I primarily work as a Frontend Developer,
Python holds a special place as my first programming language.
You can find me on various platforms:

- [LinkedIn](https://www.linkedin.com/in/emmanuel-jemeni)
- [GitHub](https://github.com/Jemeni11)
- [Twitter/X](https://twitter.com/Jemeni11_)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

[MIT License](LICENSE)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Changelog
[Changelog](/CHANGELOG.md)