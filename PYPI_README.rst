.. _readme-top:

CrossRename
===========

.. raw:: html

   <div align="center">
     <img src="https://github.com/Jemeni11/CrossRename/blob/master/logo.png?raw=true" alt="Logo" width="128" height="128">
     <br/>
     <br/>
   </div>

.. raw:: html

   <p align="center">
     Harmonize file and directory names for Linux and Windows.
     <br />
     <a href="https://github.com/Jemeni11/CrossRename"><strong>Explore the repo »</strong></a>
     <br />
   </p>

Table of Contents
-----------------

- `Introduction`_
- `Features`_
- `Installation`_
- `Usage`_

  - `Examples`_
  - `Safety First`_

- `Why did I build this?`_
- `Contributing`_
- `Wait a minute, who are you?`_
- `License`_
- `Changelog`_

Introduction
------------

CrossRename is a command-line tool designed to harmonize file and directory names across Linux and Windows systems.
It ensures that your file names are compatible with both operating systems, eliminating naming conflicts
when transferring files between different environments.

`back to top <readme-top_>`__

Features
--------

- Sanitizes file names to be Windows-compatible (and thus Linux-compatible)
- **NEW:** Optionally renames directories to be cross-platform compatible
- Handles both individual files and entire directories
- Supports recursive renaming of files in subdirectories
- Preserves file extensions, including compound extensions like .tar.gz
- Provides informative logging
- Provides a dry-run mode to preview renaming changes without executing them
- Interactive safety warnings with option to skip for automation
- Skips recursive symlinks to avoid infinite loops

`back to top <readme-top_>`__

Installation
------------

From PyPI (Using PIP)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install CrossRename

`back to top <readme-top_>`__

Usage
-----

.. code-block:: text

   usage: crossrename [-h] [-p PATH] [-v] [-u] [-r] [-d] [-D] [--force] [--credits]

   CrossRename: Harmonize file and directory names for Linux and Windows.

   options:
     -h, --help                  show this help message and exit
     -p, --path PATH             The path to the file or directory to rename.
     -v, --version               Prints out the current version and quits.
     -u, --update                Check if a new version is available.
     -r, --recursive             Rename all files in the directory path given and its subdirectories. When used with -D, also renames subdirectories.
     -d, --dry-run               Perform a dry run, logging changes without renaming.
     -D, --rename-directories    Also rename directories to be cross-platform compatible. Use with caution!
     --force                     Skip safety prompts (useful for automated scripts)
     --credits                   Show credits and support information

`back to top <readme-top_>`__

Examples
~~~~~~~~

Rename a single file:

.. code-block:: bash

   crossrename -p /path/to/file.txt

Rename all files in a directory (and its subdirectories):

.. code-block:: bash

   crossrename -p /path/to/directory -r

Rename all files AND directories recursively:

.. code-block:: bash

   crossrename -p /path/to/directory -r -D

Rename a single directory:

.. code-block:: bash

   crossrename -p /path/to/problematic_directory -D

Perform a dry run to preview renaming changes without executing them:

.. code-block:: bash

   crossrename -p /path/to/directory -r -D -d

Skip safety prompts for automated scripts:

.. code-block:: bash

   crossrename -p /path/to/directory -r -D --force

Check for an update:

.. code-block:: bash

   crossrename -u

Show credits and project information:

.. code-block:: bash

   crossrename --credits

`back to top <readme-top_>`__

Safety First
~~~~~~~~~~~~

.. warning::
   Always run with ``--dry-run`` first!

CrossRename will show interactive safety warnings before making any changes to help prevent accidental data loss.
However, it's strongly recommended to:

1. **Run a dry run first** to preview what will be changed:

   .. code-block:: bash

      crossrename -p /your/path -r -D -d

2. **Backup your data** before running the tool on important files

3. **Use** ``--force`` **flag** for automation in CI/CD pipelines:

   .. code-block:: bash

      crossrename -p /build/output -r -D --force

Directory renaming is particularly powerful and potentially disruptive since it changes folder paths that other
applications might reference.

`back to top <readme-top_>`__

Why did I build this?
---------------------

.. warning::
   I'm no longer dual booting. I'm using Windows 11 now. I do have WSL2 and that's what I use for testing.
   I don't know if there'll be any difference in the way the tool works on a native Linux system.

So I was dual-booting Windows 10 and Lubuntu 22.04, and one day I'm trying to move some files between the two systems.
Five files just wouldn't copy over because of what I later found out were the differences in Windows and Linux's file
naming rules.

That got me thinking because I'd already built a Python package that had to deal with some file creation and renaming (
It's called `FicImage <https://github.com/Jemeni11/ficimage>`__ please check it out 🫶) before, so I had an idea or two
about how to go about this.

Long story short, I got annoyed enough to build CrossRename. Now I don't have to deal with file naming headaches when
switching between systems.

`back to top <readme-top_>`__

Contributing
------------

Contributions are welcome! If you'd like to improve CrossRename or add support for
other operating systems (like macOS), please feel free to submit a pull request.

`back to top <readme-top_>`__

Wait a minute, who are you?
---------------------------

Hello there! I'm Emmanuel Jemeni, and while I primarily work as a Frontend Developer,
Python holds a special place as my first programming language.
You can find me on various platforms:

- `LinkedIn <https://www.linkedin.com/in/emmanuel-jemeni>`__
- `GitHub <https://github.com/Jemeni11>`__
- `BlueSky <https://bsky.app/profile/jemeni11.bsky.social>`__
- `Twitter/X <https://twitter.com/Jemeni11_>`__

`back to top <readme-top_>`__

License
-------

`MIT License <https://github.com/Jemeni11/CrossRename/blob/main/LICENSE>`__

`back to top <readme-top_>`__

Changelog
---------

`Changelog <https://github.com/Jemeni11/CrossRename/blob/main/CHANGELOG.md>`__

`back to top <readme-top_>`__