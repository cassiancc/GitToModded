# Git to Modded

This Python script generates Modded Minecraft Wiki docs from a GitHub Wiki. This allows for developers to easily transfer their existing work from GitHub to the Modded Minecraft Wiki without having to manually rename files and add basic, scriptable information.

Experimental support is also available for users of other git-based forges like GitLab, and users who [sync their Gitbook docs to GitHub/GitLab](https://docs.gitbook.com/getting-started/git-sync).

Note that links, images, and some metadata may not yet transfer 1:1. This script is still in early active development.

## Requirements
- Python 3 (tested on 3.13)
    - gitpython
- Node.js (if you want to preview the Wiki through this script)

## Installation

- [Install Python](https://www.python.org/downloads/)
- Install gitpython
```bash
pip install gitpython
```
- [Install Node.js](https://nodejs.org/en/download)

## Usage
- Run `python script.py`
- Enter in a Git repository to download and convert.
    - This process can be sped up by passing in a URL as a CLI arg e.g. `python script.py https://github.com/cassiancc/Pyrite`
- The docs will be generated into a `/docs/modname` folder. You can repeat this step for as many mods as you wish to convert.
    - The option to repeat can be skipped by passing the auto variable after the URL e.g. `python script.py https://github.com/cassiancc/Pyrite auto`
- When you're finished, you're given the option to preview the docs. Note that live preview is still an unfinished feature.
- When you're done with the script, you can copy your docs from `docs/modname` to your mod's GitHub repository. From there, finish setting up your Modded MC Wiki support as directed on the [Modded MC Wiki](https://moddedmc.wiki/en/about/devs).

## Feature Roadmap

These are the features I'm actively working on. If you want to improve the script, feel free to PR at them, and if you have any other nice-to-haves, PRs and issues are welcome.

- Conversion of relative links from GitHub wikis.
- Migration of images.
    - Migration of images from GitLab wikis.
    - Migration of images from Gitbook wikis.
- Generating `_meta_json` files for wikis with subdirectories.
- Generating Modrinth and CurseForge slugs from other common sources of metadata (currently only README.md is supported)
    - `fabric.mod.json` and `mods.toml`
    - GitHub footers.
    - README (no extension?)
- Converting GitHub custom sidebars to a folder structure.
    - Losing GitHub metadata is frustrating, but mapping it to a directory structure is an imperfect solution. Very much open to feature PRs there - if its ever added it'd definitely have to be optional.
- Appending GitHub custom footers to the bottom of (all?) pages.
    - Again, if this is added it'd be optional.