from diff_match_patch import diff_match_patch
from datetime import datetime
from bs4 import BeautifulSoup
from typing import NewType
from sys import getsizeof
from pathlib import Path
import requests
import hashlib
import gzip
import json
import os
import re


###########
# GLOBALS #
###########


dmp = diff_match_patch()

scrape_result = NewType("scrape_result", tuple[str, str, str])

# current working directory and file

cwf = Path(__file__)
cwd = cwf.parent


#############
# FUNCTIONS #
#############


def sanitized_url(url: str) -> str:
    # replace unsafe chars with underscores

    sanitized = re.sub(r'[<>:"/\\|?*.]', '_', url)

    # trim to a max length
    # and add hash suffix in case two urls look the same after regex

    max_length = 100
    hash_suffix = hashlib.md5(url.encode()).hexdigest()[:8]
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "_" + hash_suffix
    else:
        sanitized += "_" + hash_suffix

    return sanitized


def scrape_url(url: str) -> scrape_result | None:
    response = requests.get(url)

    return scrape_result((url, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), str(response.content)))
    if response.status_code != 200:
        # fail to get page, perhaps throw error?
        return None

    # parse html using bs4 library, mainly for cleanup
    # maybe we can use for more complex things later?

    soup = BeautifulSoup(response.content, "html.parser")
    html = str(soup)
    dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return scrape_result((url, dt, html))


def diff_save(scrape: scrape_result):
    this_url, this_time, this_html = scrape
    safe_url = sanitized_url(this_url)
    html = None

    # make a subdirectory to store this url

    subdir = cwd / "snapshots" / safe_url

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # ensure that source.html exists

    if not os.path.exists(subdir / "source.html"):
        with open(subdir / "source.html", "w") as f:
            f.write(this_html)

    # load source.html

    with open(subdir / "source.html", "r") as f:
        html = f.read()

    # apply all diffs in the form of <date>.diff in order

    diff_files = [f for f in os.listdir(subdir) if f.endswith(".diff")]
    diff_files.sort()
    for diff_file in diff_files:
        # with open(subdir / diff_file, "r") as f:
        #     delta = f.read()
        #     diffs = dmp.diff_fromDelta(html, delta)
        #     # diff = json.loads(f.read())
        #     html = dmp.patch_apply(dmp.patch_make(diffs), html)[0]
        with gzip.open(subdir / diff_file, "rt") as f:
            delta = f.read()
            diffs = dmp.diff_fromDelta(html, delta)
            html = dmp.patch_apply(dmp.patch_make(diffs), html)[0]
            print(html)

    # diff the current html with the new html

    diffs = dmp.diff_main(html, this_html)
    delta = dmp.diff_toDelta(diffs)

    # save the diff

    with gzip.open(subdir / f"{this_time}.diff", "wt") as f:
        f.write(delta)

    # diff_file = subdir / f"{this_time}.diff"
    # with open(diff_file, "w") as f:
    #     f.write(delta)


result = scrape_url("https://amazon.com/")
if not result is None:
    diff_save(result)
