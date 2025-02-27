from git import Repo  # pip install gitpython
import git # pip install gitpython
from urllib.parse import urlparse
import os
import shutil
from pathlib import Path
import json
import tomllib

def getPath(url):
    return urlparse(git_url).path.split("/")[-1]

def clone(url, isWiki):
    path = getPath(url)
    if (isWiki):
        path+=".wiki"
        url+=".wiki"
    if not os.path.isdir(path):
        print("Cloning " + path)
        Repo.clone_from(url, path)
    else:
        print(path+ " exists on disk, no need to clone.")

def toTitle(file: str):
    return file.replace("-", " ").replace("_", " ").strip()

git_url = ""



while git_url == "":
    git_url = input("What repository would you like to clone?\n")
    if (git_url.find("https://") == -1):
        git_url = ""
    if (git_url != ""):
        try:
            clone(git_url, True) # Clone the wiki
        except git.exc.GitError:
            print("This repository does not exist (or is not public)!")
            git_url = ""

    

git_path = getPath(git_url)
id = git_path.lower()



# Start script
# clone(git_url, False) # Clone the main branch
# clone("https://github.com/Sinytra/Wiki", False) # Clone the wiki


# Copy wiki over to a working directory, ignoring git files.
if (os.path.isdir("working")):
    shutil.rmtree("working")
shutil.copytree(git_path + ".wiki", 'working', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))

# Create output folder
if (not os.path.isdir("docs")):
    os.mkdir("docs")

# Create output folder
if (not os.path.isdir("docs/"+id)):
    os.mkdir("docs/"+id)

meta = {}

# Read markdown files and convert to MDX
for file in Path('working').glob('*'):
    with open(file, 'r', encoding="utf8") as original:
        old = original.read()
        with open(f"docs/{id}/{file.name.replace(".md", ".mdx")}", 'w', encoding="utf8") as modified:
            modified.write(f"---\ntitle: {toTitle(file.stem)}\n---\n\n{old}") # write the new line before
            meta[file.name] = toTitle(file.stem)

# Write wiki.json file
with open(f"docs/{id}/sinytra-wiki.json", 'w', encoding="utf8") as wiki:
    wiki.write(json.dumps({
    "id": id,
     "platforms": {
        "modrinth": id,
        "curseforge": id
     }
}, indent=2))

# Write _meta.json file
with open(f"docs/{id}/_meta.json", 'w', encoding="utf8") as wiki:
    wiki.write(json.dumps(meta, indent=2))

print()
print(f"Converted the GitHub Wiki of {git_path.replace("_", " ").replace("-", " ")} to a Modded Minecraft Wiki. Copy the newly generated docs folder into its GitHub repository.")