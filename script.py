import git # pip install gitpython
from urllib.parse import urlparse
import os, shutil, json,  re, sys
from pathlib import Path


# Functions used in the script.

# Find the last segment of the URL - used to guess at folder names.
def getPath(url: str):
    return urlparse(url).path.split("/")[-1]

def autoinput(s: str):
    if (not auto):
        return input(s)
    return False

# Convert Markdown to MDX, and rename the homepage accordingly.
def getNewFileName(file: Path):
    if (file.name.lower() == "home.md"):
        return "_homepage.mdx"
    new = str(file).replace(".md", ".mdx").removeprefix(".working\\").removeprefix(".working/")
    return new

# Create a folder if it does not already exist.
def safeMkDir(path: str):
    if (not os.path.isdir(path)):
        os.mkdir(path)

# Clone a GitHub Repository.
def clone(url: str, isWiki: bool):
    path = getPath(url)
    # .wiki is assumed, but if it's added to the url make sure that its handled.
    if (isWiki and not (url.endswith(".wiki"))):
        path+=".wiki"
        url+=".wiki"
    # If the wiki isn't cached, clone it.
    if not os.path.isdir(path):
        print(f"Cloning {path} ({url})")
        git.Repo.clone_from(url, path, depth=1)
    else:
        print(path+ " exists on disk, no need to clone.")

def toTitle(file: str):
    return file.replace("-", " ").replace("_", " ").strip().title()

def userPrompt(prompt: str):
    if (not auto):
        userInput = input(f"{prompt}\n")
        if (len(userInput) > 0):
            if (userInput[0].lower() == "y"):
                return True
    return False

def replaceCover(original: str, id: str):
    index = original.find("cover: ")
    cover = original[index:]
    index = cover.find("\n")
    cover = cover[:index]
    img = re.sub("cover: [./]*.gitbook\\/assets/", "", cover)
    component = f"\n<Asset location=\"{id}:{img}\" />"
    original = original.replace(cover, "")
    index = original.rfind("---")+3
    original = original[:index] + component + original[index:]
    return original

# Start script.

def convert(url, auto):
    # Clear cache
    safeMkDir(".cache")
    git_url = url
    # Use main repo - defaults to disabled, allows for using the main repo instead of its associated wiki. Useful for Gitbook users.
    useMainRepo = False
    # Request a Git URL from the user and clone it and its associated wiki.
    while git_url == "":
        git_url = input("What repository would you like to clone? (e.g. https://github.com/cassiancc/Pyrite)\n")
        if (git_url.find("https://") == -1 and not os.path.isdir(f".cache/{url}")):
            git_url = ""
        if (git_url != ""):
            # ignore .git urls, they'll only confuse later code elements.
            git_url = git_url.removesuffix(".git")
            # if a user provides the link to the wiki, replace that with the correct link
            if (git_url.endswith("/wiki")): #github
                git_url = git_url.replace("/wiki", ".wiki")
            elif (git_url.endswith("/-/wikis/home")): #gitlab
                git_url = git_url.replace("/-/wikis/home", ".wiki")
            elif (git_url.endswith("/-/wikis")): #gitlab
                git_url = git_url.replace("/-/wikis", ".wiki")
            # clone the wiki into cache if possible
            os.chdir(".cache")
            try:
                clone(git_url.replace(".wiki", ""), False) # Clone the main repository for metadata - or if it has no wiki.
                try:
                    clone(git_url, True) # Clone the wiki for data.
                except git.exc.GitError:
                    print("\nThis repository has no associated wiki!")
                    useMainRepo = userPrompt("Would you like to treat the main repo as the wiki? (e.g. Gitbook) (y/n)")
                    if (not useMainRepo):
                        git_url = ""
            except git.exc.GitError:
                print("This repository does not exist (or is not public)!")
                git_url = ""
            os.chdir("..")

    # get the name of the wiki - used for folder naming
    git_path = getPath(git_url)
    wiki_path = git_path
    if (not wiki_path.endswith(".wiki") and not useMainRepo):
        wiki_path += ".wiki"
    else:
        git_path = git_path.replace(".wiki", "")

    # get the id of the wiki, used for _meta.json
    meta = {}
    id = git_path.lower()
    cf = id
    mr = id
    
    # Copy wiki over to a working directory, ignoring git files.
    if (os.path.isdir(".working")):
        shutil.rmtree(".working")
    shutil.copytree(f".cache/{wiki_path}", '.working', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', ".gitlab", ".gitignore", "_sidebar.md"))
    # Create output folders
    safeMkDir("docs")
    safeMkDir(f"docs/{id}")
    safeMkDir(f"docs/{id}/.assets")
    safeMkDir(f"docs/{id}/.assets/{id}")

    # Find the CurseForge slug from the main project's README.md, if present.
    try:
        with open(f".cache/{git_path}/README.md", 'r', encoding="utf8") as original:
            README = original.read()
            # Find CurseForge from README
            cfmatch = re.search("https://[a-z]*\\.*curseforge.com/minecraft/[a-z-]*/[a-z-]*", README)
            if (cfmatch):  
                cf = getPath(cfmatch.group())
                mr = cf
            # Find Modrinth from README
            mrmatch = re.search("https://modrinth.com/[a-z-]*/[a-z-+]*", README)
            if (mrmatch):  
                mr = getPath(mrmatch.group())
                print(mr)
            # If CurseForge is found, but not Modrinth, assume Modrinth and CurseForge links are the same.
            elif (cfmatch):
                mr = cf
            # If Modrinth is found, but not CurseForge, assume Modrinth and CurseForge links are the same.
            if (mrmatch and not cfmatch):
                cf = mr
    except:
        print("Unable to locate README!")

    # Read markdown files and convert to MDX
    for file in Path('.working').rglob('*'):
        if (file.name.endswith(".png")):
            shutil.copyfile(file, f"docs/{id}/.assets/{id}/{file.name}")
        else:
            try:
                with open(file, 'r', encoding="utf8") as original:
                    FILENAME = f"docs/{id}/{getNewFileName(file)}"
                    os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
                    DOC = original.read()
                    if (file.name.endswith(".md")):
                        if (DOC.find("cover: ") != -1):
                            DOC = replaceCover(DOC, id)
                        with open(FILENAME, 'w', encoding="utf8") as modified:
                            title = f"\ntitle: {toTitle(file.stem)}\n"
                            test = DOC[:3] == "---"
                            if (test == True):
                                DOC = DOC[:3] + title + DOC[3:]
                                modified.write(DOC)
                            else:
                                modified.write(f"---{title}---\n\n{DOC}") # write the new line before
                            meta[file.name] = toTitle(file.stem)
            except:
                pass

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

    # Check source of wiki for output.
    if (urlparse(git_url).netloc == "github.com"):
        src = "GitHub"
    elif (urlparse(git_url).netloc == "gitlab.com"):
        src = "GitLab"
    else:
        src = "Git"
    if (useMainRepo):
        src += " Repository"
    else:
        src += " Wiki of"
    
    result = f"\nConverted the {src} {toTitle(git_path)} to a Modded Minecraft Wiki."
    if (not auto):
        shouldRunAgain = input(f"{result} Would you like to convert another wiki? (y/n, or paste URL)\n")
        if (len(shouldRunAgain) > 0):
            if ((shouldRunAgain[0].lower() == "y") or (shouldRunAgain.find("https") != -1)):
                convert(shouldRunAgain)
    else: print(result)


val = ""
auto = False
NARGS = len(sys.argv)
if (NARGS > 1):
    val = sys.argv[1]
    if (NARGS > 2):
        if (sys.argv[2] == "auto"):
            auto = True
convert(val, auto)

# Run a live preview by cloning the Modded MC Wiki, installing its dependencies, and running it in local preview mode.
if (userPrompt("Would you like to preview the Wiki? (y/n)")):
    os.environ['ENABLE_LOCAL_PREVIEW'] = "true" # Set the Wiki to local preview.
    clone("https://github.com/Sinytra/Wiki", False) # Clone the wiki
    shutil.copytree("docs", 'Wiki/preview', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
    os.chdir("Wiki") # Open the Wiki
    roots = ""
    for doc in os.listdir("./preview"):
        roots += f"./preview/{doc};"
    os.environ['LOCAL_DOCS_ROOTS'] = roots
    os.system("npm install") # Install Wiki Dependencies
    os.system("npm run dev") # Run the Wiki