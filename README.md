# Git to Modded

This Python script generates Modded Minecraft Wiki docs from a GitHub/GitLab Wiki. This allows for developers to easily transfer their existing work from GitHub/GitLab to the Modded Minecraft Wiki without having to manually rename files and add basic, scriptable information.

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
- Run `script.py`
- Enter in a Git repository to download and convert.
- The docs will be generated into a `/docs/modname` folder. You can repeat this step for as many mods as you wish to convert.
- When you're finished, you're given the option to preview the docs. Note that live preview is still an unfinished feature.
- When you're done with the script, you can copy your docs from `docs/modname` to your mod's GitHub repository. From there, finish setting up your Modded MC Wiki support as directed on the [Modded MC Wiki](https://moddedmc.wiki/en/about/devs).

## Feature Roadmap

- Conversion of relative links
- Conversion of images
    - Conversion of images from GitLab
    - Conversion of images from Gitbook
- Generating `_meta_json` files for subdirectories.
- Generating Modrinth and CurseForge slugs from `fabric.mod.json` and `mods.toml`