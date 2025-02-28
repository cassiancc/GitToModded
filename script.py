from git import Repo  # pip install gitpython
import git # pip install gitpython
from urllib.parse import urlparse
import os
import shutil
from pathlib import Path
import json
import tomllib

# Functions used in the script.

def getPath(url: str):
    return urlparse(url).path.split("/")[-1]

def safeMkDir(path: str):
    if (not os.path.isdir(path)):
        os.mkdir(path)

def clone(url: str, isWiki: bool):
    print(url)
    path = getPath(url)
    # .wiki is assumed, but if it's added to the url make sure that its handled.
    if (isWiki and not (url.endswith(".wiki"))):
        path+=".wiki"
        url+=".wiki"
    if not os.path.isdir(path):
        print("Cloning " + path)
        Repo.clone_from(url, path)
    else:
        print(path+ " exists on disk, no need to clone.")

def toTitle(file: str):
    return file.replace("-", " ").replace("_", " ").strip()


# Start script.

def convert(url):
    git_url = url
    while git_url == "":
        git_url = input("What repository would you like to clone? (e.g. https://github.com/cassiancc/Pyrite)\n")
        if (git_url.find("https://") == -1):
            git_url = ""
        if (git_url != ""):
            # ignore .git urls, they'll only confuse later code elements.
            git_url = git_url.removesuffix(".git")
            # if a user provides the link to the wiki, replace that with the correct link
            if (git_url.endswith("/wiki")):
                git_url = git_url.replace("/wiki", ".wiki")
            # clone the wiki if possible
            try:
                clone(git_url, True) # Clone the wiki
            except git.exc.GitError:
                print("This repository does not exist (or is not public)!")
                git_url = ""

    # get the name of the wiki - used for folder naming
    git_path = getPath(git_url)

    # Copy wiki over to a working directory, ignoring git files.
    if (os.path.isdir(".working")):
        shutil.rmtree(".working")
    
    wiki_path = git_path
    if (not wiki_path.endswith(".wiki")):
        wiki_path += ".wiki"
    else:
        git_path = git_path.replace(".wiki", "")

    # get the id of the wiki, used for _meta.json
    id = git_path.lower()
    
    shutil.copytree(wiki_path, '.working', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))

    # Create output folder
    safeMkDir("docs")

    # Create output folder
    safeMkDir("docs/"+id)

    meta = {}

    # Read markdown files and convert to MDX
    for file in Path('.working').glob('*'):
        with open(file, 'r', encoding="utf8") as original:
            old = original.read()
            with open(f"docs/{id}/{file.name.replace(".md", ".mdx")}", 'w', encoding="utf8") as modified:
                modified.write(f"---\ntitle: {toTitle(file.stem)}\n---\n\n{old}") # write the new line before
                meta[file.name] = toTitle(file.stem)

    # Write wiki.json file
    with open(f"docs/{id}/sinytra-wiki.json", 'w', encoding="utf8") as wiki:
        wiki.write(json.dumps({
        "id": id.replace("_", "-"),
        "platforms": {
            "modrinth": id,
            "curseforge": id
        }
    }, indent=2))

    # Write _meta.json file
    with open(f"docs/{id}/_meta.json", 'w', encoding="utf8") as wiki:
        wiki.write(json.dumps(meta, indent=2))

    print()
    shouldRunAgain = input(f"Converted the GitHub Wiki of {toTitle(git_path)} to a Modded Minecraft Wiki. Would you like to convert another wiki? (y/n, or paste URL)\n")
    if (len(shouldRunAgain) > 0):
        if ((shouldRunAgain[0].lower() == "y") or (shouldRunAgain.find("https") != -1)):
            convert(shouldRunAgain)

convert("")

# Run a live preview by cloning the Modded MC Wiki, installing its dependencies, and running it in local preview mode.
shouldRunPreview = input("Would you like to preview the Wiki? (y/n)\n")
if (shouldRunPreview[0].lower() == "y"):
    os.environ['ENABLE_LOCAL_PREVIEW'] = "true" # Set the Wiki to local preview.
    clone("https://github.com/Sinytra/Wiki", False) # Clone the wiki
    shutil.copytree("docs", 'Wiki/preview', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
    os.chdir("Wiki") # Open the Wiki
    roots = ""
    for doc in os.listdir("./preview"):
        roots += f"./preview/{doc};"
    print(roots)
    os.environ['LOCAL_DOCS_ROOTS'] = roots
    os.system("npm install") # Install Wiki Dependencies
    os.system("npm run dev") # Run the Wiki