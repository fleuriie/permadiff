from diff_match_patch import diff_match_patch
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep, time
from typing import NewType, List
from sys import getsizeof
from pathlib import Path
import statistics
import threading
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

    print(response.status_code)
    if response.status_code != 200 and response.content is None:
        # fail to get page, perhaps throw error?
        return None

    # parse html using bs4 library, mainly for cleanup
    # maybe we can use for more complex things later?

    soup = BeautifulSoup(response.content, "html.parser")
    html = str(soup)
    dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return scrape_result((url, dt, html))


def save(scrape: scrape_result, diff: bool = True):
    this_url, this_time, this_html = scrape
    safe_url = sanitized_url(this_url)
    html = None

    # make a subdirectory to store this url

    subdir = cwd / "snapshots" / safe_url

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # just store it raw if diff is false

    if not diff:
        with gzip.open(subdir / f"{this_time}.html", "wt") as f:
            f.write(this_html)
        return

    # try to get html from cache if possible

    if safe_url in cache:
        print(f"Using cached html for {this_url}")
        html = cache[safe_url]
    else:
        # ensure that source.html exists

        if not os.path.exists(subdir / "source.html"):
            with gzip.open(subdir / "source.html", "wt") as f:
                f.write(this_html)

        # load source.html

        with gzip.open(subdir / "source.html", "rt") as f:
            start = time()
            html = f.read()
            print(f"Raw read time: {time() - start:.5f}")

        # apply all diffs in the form of <date>.diff in order

        patch_times = []
        diff_files = [f for f in os.listdir(subdir) if f.endswith(".diff")]
        diff_files.sort()
        for diff_file in diff_files:
            with gzip.open(subdir / diff_file, "rt") as f:
                start = time()
                delta = f.read()
                diffs = dmp.diff_fromDelta(html, delta)
                html = dmp.patch_apply(dmp.patch_make(diffs), html)[0]
                patch_times.append(time() - start)

        if len(patch_times) > 1:
            print(f"Patch times: {patch_times}")
            print(
                f"Average patch time: {sum(patch_times)/len(patch_times):.5f}")
            print(f"STDDEV patch time: {statistics.stdev(patch_times):.5f}")
    cache[safe_url] = this_html

    # diff the current html with the new html, stores as a delta

    diffs = dmp.diff_main(html, this_html)
    delta = dmp.diff_toDelta(diffs)

    # save the diff

    with gzip.open(subdir / f"{this_time}.diff", "wt") as f:
        f.write(delta)


def period_snapshot(
    urls: List[str],
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    diff: bool = True,
    iterations: int = -1
):
    if not any([days, hours, minutes, seconds]):
        raise ValueError("At least one time unit must be non-zero.")

    interval = seconds + minutes*60 + hours*3600 + days*86400

    # run scrape_url every <seconds> seconds
    # and diff_save the result

    latency = []

    iteration = 0
    while iterations == -1 or iteration < iterations:
        iteration += 1
        for url in urls:
            print(
                f"Attempting scrape of {url} at:",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            result = scrape_url(url)

            if not result is None:
                print("Scraped successfully.")
                start = time()
                if diff:
                    save(result, diff=True)
                    print("Diff saved.")
                else:
                    save(result, diff=False)
                    print("Raw saved.")
                latency.append(time() - start)
                print(f"Latency: {latency[-1]:.3f} seconds.")
                print(f"Average: {sum(latency)/len(latency):.5f} seconds")
                if len(latency) > 1:
                    print(f"STDDEV: {statistics.stdev(latency):.5f}")
            else:
                print("Failed to scrape.")

            print()
        sleep(interval)


########
# MAIN #
########

if __name__ == "__main__":
    urls = [
        "https://www.google.com/",
        "https://www.reddit.com/",
        "https://www.whatsapp.com/"
        "https://www.wikipedia.org/",
        "https://www.yahoo.com/",
        "https://www.yahoo.co.jp/",
        "https://www.baidu.com/",
        "https://www.netflix.com/",
        "https://www.linkedin.com/",
        "https://office.com/",
        "https://www.naver.com/",
        "https://news.yahoo.co.jp/",
        "https://www.twitch.tv/",
        "https://samsung.com/",
        "https://www.globo.com/",
        "https://www.fandom.com/",
        "https://weather.com/",
        "https://telegram.org/",
    ]

    period_snapshot(
        urls,
        minutes=30,
        diff=True,
        iterations=20
    )
    # period_snapshot(
    #     urls,
    #     minutes=30,
    #     diff=False,
    #     iterations=20
    # )
