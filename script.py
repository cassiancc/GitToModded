import git # pip install gitpython
from urllib.parse import urlparse
import os, shutil, json,  re
from pathlib import Path


# Functions used in the script.

def getPath(url: str):
    return urlparse(url).path.split("/")[-1]

# Convert Markdown to MDX, and rename the homepage accordingly.
def getNewFileName(file: Path):
    if (file.name == "Home.md"):
        return "_homepage.mdx"
    return file.name.replace(".md", ".mdx")

# Create a folder if it does not already exist.
def safeMkDir(path: str):
    if (not os.path.isdir(path)):
        os.mkdir(path)

# Clone a GitHub Repository.
def clone(url: str, isWiki: bool):
    print(url)
    path = getPath(url)
    # .wiki is assumed, but if it's added to the url make sure that its handled.
    if (isWiki and not (url.endswith(".wiki"))):
        path+=".wiki"
        url+=".wiki"
    if not os.path.isdir(path):
        print("Cloning " + path)
        git.Repo.clone_from(url, path)
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
                clone(git_url, True) # Clone the wiki for data.
                clone(git_url, False) # Clone the main repository for metadata.
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
    meta = {}
    cf = id
    mr = id
    
    # Create output folders
    shutil.copytree(wiki_path, '.working', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
    safeMkDir("docs")
    safeMkDir("docs/"+id)

    # Find the CurseForge URL from the README.md, if present.
    try:
        with open(f"{git_path}/README.md", 'r', encoding="utf8") as original:
            README = original.read()
            cfmatch = re.search("https://[a-z]*\\.*curseforge.com/minecraft/[a-z-]*/[a-z-]*", README)
            if (cfmatch):  
                cf = getPath(cfmatch.group())
                mr = cf
    except:
        print("Unable to locate README!")

    # Read markdown files and convert to MDX
    for file in Path('.working').glob('*'):
        with open(file, 'r', encoding="utf8") as original:
            README = original.read()
            with open(f"docs/{id}/{getNewFileName(file)}", 'w', encoding="utf8") as modified:
                modified.write(f"---\ntitle: {toTitle(file.stem)}\n---\n\n{README}") # write the new line before
                meta[file.name] = toTitle(file.stem)

    # Write wiki.json file
    with open(f"docs/{id}/sinytra-wiki.json", 'w', encoding="utf8") as wiki:
        wiki.write(json.dumps({
        "id": id.replace("_", "-"),
        "platforms": {
            "modrinth": mr,
            "curseforge": cf
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