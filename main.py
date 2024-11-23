from diff_match_patch import diff_match_patch
from datetime import datetime
from bs4 import BeautifulSoup
from typing import NewType
from sys import getsizeof
from pathlib import Path
from time import sleep
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

# cache for website htmls

cache = {}


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

    if response.status_code != 200 and response.content is None:
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

    # try to get html from cache if possible

    if safe_url in cache:
        print(f"Using cached html for {this_url}")
        html = cache[safe_url]
    else:
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
            with gzip.open(subdir / diff_file, "rt") as f:
                delta = f.read()
                diffs = dmp.diff_fromDelta(html, delta)
                html = dmp.patch_apply(dmp.patch_make(diffs), html)[0]

    cache[safe_url] = this_html

    # diff the current html with the new html, stores as a delta

    diffs = dmp.diff_main(html, this_html)
    delta = dmp.diff_toDelta(diffs)

    # save the diff

    with gzip.open(subdir / f"{this_time}.diff", "wt") as f:
        f.write(delta)


def period_snapshot(
    url: str,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0
):
    if not any([days, hours, minutes, seconds]):
        raise ValueError("At least one time unit must be non-zero.")

    interval = seconds + minutes*60 + hours*3600 + days*86400

    # run scrape_url every <seconds> seconds
    # and diff_save the result

    while True:
        print(
            f"Attempting scrape of {url} at:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        result = scrape_url(url)

        if not result is None:
            print("Scraped successfully.")
            diff_save(result)
            print("Diff saved.")
        else:
            print("Failed to scrape.")

        print()
        sleep(interval)

########
# MAIN #
########

if __name__ == "__main__":
    period_snapshot("https://www.news.google.com", seconds=2)
