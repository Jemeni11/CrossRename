CrossRename
===========

Harmonize file names for Linux and Windows.

Table of Contents
=================

-  `Introduction <#introduction>`__
-  `Features <#features>`__
-  `Installation <#installation>`__
-  `Usage <#usage>`__
-  `Examples <#examples>`__
-  `Why did I build this? <#why-did-i-build-this>`__
-  `Contributing <#contributing>`__
-  `Wait a minute, who are you? <#wait-a-minute-who-are-you>`__
-  `License <#license>`__
-  `Changelog <#changelog>`__

Introduction
============

CrossRename is a command-line tool designed to harmonize file names
across Linux and Windows systems. It ensures that your file names are
compatible with both operating systems, eliminating naming conflicts
when transferring files between different environments.

Features
========

-  Sanitizes file names to be Windows-compatible (and thus
   Linux-compatible)
-  Handles both individual files and entire directories
-  Supports recursive renaming of files in subdirectories
-  Preserves file extensions, including compound extensions like .tar.gz
-  Provides informative logging with optional debug mode

Installation
============

From PyPI (Using PIP)
---------------------

::

   pip install CrossRename

Usage
=====

::

   usage: crossrename [-h] -p PATH [-d] [-v] [-r]

   CrossRename: Harmonize file names for Linux and Windows.

   options:
     -h, --help            show this help message and exit
     -p PATH, --path PATH  The path to the file or directory to rename.
     -d, --debug           Enable debug mode.
     -v, --version         Prints out the current version and quits.
     -r, --recursive       Rename all files in the directory path given and its subdirectories.

Examples
--------

Rename a single file:

::

   crossrename -p /path/to/file.txt

Rename all files in a directory (and its subdirectories):

::

   crossrename -p /path/to/directory -r

Why did I build this?
=====================

.. warning::

   I’m no longer dual booting. I’m only using Windows 10 now. I do have
   WSL2 and that’s what I use for testing. I don’t know if there’ll be
   any difference in the way the tool works on a native Linux system.

I’m a dual-booter running Windows 10 and Lubuntu 22.04. One day
(literally yesterday lol), while transferring a folder between the two
systems, I hit a naming roadblock. Five stubborn files refused to budge,
thanks to the quirky differences in file naming rules between Linux and
Windows.

This experience got me thinking. You see, I had previously built
`FicImage <https://github.com/Jemeni11/ficimage>`__, a nifty application
that elevates the reading experience of `FicHub <https://fichub.net/>`__
epubs by adding missing images. It required handling file creation and
renaming, and that knowledge proved invaluable.

And so, CrossRename was born – a tool to simplify your life when
managing files between Linux and Windows. No more naming hassles, just
smooth, worry-free file management.

Contributing
============

Contributions are welcome! If you’d like to improve CrossRename or add
support for other operating systems (like macOS), please feel free to
submit a pull request.

Wait a minute, who are you?
===========================

Hello there! I’m Emmanuel Jemeni, and while I primarily work as a
Frontend Developer, Python holds a special place as my first programming
language. You can find me on various platforms:

-  `LinkedIn <https://www.linkedin.com/in/emmanuel-jemeni>`__
-  `GitHub <https://github.com/Jemeni11>`__
-  `Twitter/X <https://twitter.com/Jemeni11_>`__

License
=======

`MIT License <LICENSE>`__

Changelog
=========

`Changelog <CHANGELOG.md>`__
