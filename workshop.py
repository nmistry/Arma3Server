import os
import re
import subprocess
import urllib.request

import keys

WORKSHOP_SKIP_DOWNLOAD = os.getenv('WORKSHOP_SKIP_DOWNLOAD', False)
    
WORKSHOP = "steamapps/workshop/content/107410/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa: E501

def rename_to_lowercase(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            src = os.path.join(dirpath, filename)
            dst = os.path.join(dirpath, filename.lower())
            if src != dst and not os.path.exists(dst):
                os.rename(src, dst)

        # Rename directories
        for dirname in dirnames:
            src = os.path.join(dirpath, dirname)
            dst = os.path.join(dirpath, dirname.lower())
            if src != dst and not os.path.exists(dst):
                os.rename(src, dst)

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def download(mods):
    for batch in chunk(mods,5):
        print("Downloading workshopmods batch: ", batch)
        steamcmd = ["/steamcmd/steamcmd.sh"]
        steamcmd.extend(["+force_install_dir", "/arma3"])
        steamcmd.extend(["+login", os.environ["STEAM_USER"], os.environ["STEAM_PASSWORD"]])
        for id in batch:
            steamcmd.extend(["+workshop_download_item", "107410", id])
        steamcmd.extend(["+quit"])
        subprocess.call(steamcmd)


def preset(mod_file):
    if mod_file.startswith("http"):
        req = urllib.request.Request(
            mod_file,
            headers={"User-Agent": USER_AGENT},
        )
        remote = urllib.request.urlopen(req)
        with open("preset.html", "wb") as f:
            f.write(remote.read())
        mod_file = "preset.html"
    mods = []
    moddirs = []
    with open(mod_file) as f:
        html = f.read()
        regex = r"filedetails\/\?id=(\d+)\""
        matches = re.finditer(regex, html, re.MULTILINE)
        for _, match in enumerate(matches, start=1):
            mods.append(match.group(1))
            moddir = WORKSHOP + match.group(1)
            moddirs.append(moddir)
        if not WORKSHOP_SKIP_DOWNLOAD:
            download(mods)
            for moddir in moddirs:
                keys.copy(moddir)
            rename_to_lowercase(WORKSHOP)
    return moddirs
