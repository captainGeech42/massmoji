import logging
import math
from typing import List

import requests
from bs4 import BeautifulSoup

SLACKMOJI_URL = "https://slackmojis.com"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y/%m/%d %H:%M:%S",
    handlers=[
        logging.StreamHandler()
    ]
)

class Emoji:
    name: str
    url: str

    def __init__(self, name: str, url: str):
        self.name = name.replace(":", "")
        self.url = url

    def __eq__(self, other):
        if isinstance(other, Emoji):
            return self.name == other.name
        return False

    def __str__(self):
        return self.name

def get_emojis(html: str) -> List[Emoji]:
    soup = BeautifulSoup(html, "html.parser")

    emoji_a_tags = soup.find_all("a", "downloader")

    emojis = []

    for a_tag in emoji_a_tags:
        name =  a_tag.find("div", "name").string.strip()
        url = a_tag.find("img").get("src")

        emojis.append(Emoji(name, url))

    return emojis

def get_see_mores(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")

    seemore_divs = soup.find_all("div", "seemore")

    return [x.find("a").get("href") for x in seemore_divs]

def save_all_emojis_to_disk(emojis: List[Emoji]):
    counter = 0
    percent = 0

    for i in range(len(emojis)):
        if math.floor((counter / len(emojis)) * 100) > percent:
            percent += 1
            logging.info(f"emoji downloads: {percent}% completed")

        e = emojis[i]

        r = requests.get(e.url)

        ct = r.headers["content-type"]
        extension = ct.split("/")[1]

        with open(f"emojis/{e.name}.{extension}", "wb") as f:
            f.write(r.content)

        counter += 1

logging.info("STARTING SLACKMOJI DOWNLOAD")

# get the emojis
logging.info("downloading html for /")
r = requests.get(SLACKMOJI_URL + "/")
emojis = []

# get everything from the homepage
logging.info("parsing emojis from /")
emojis.extend(get_emojis(r.content.decode()))

# get all of the see more URLs
logging.info("parsing see more urls from /")
more_urls = get_see_mores(r.content.decode())

for u in more_urls:
    logging.info(f"downloading html for {u}")

    r = requests.get(SLACKMOJI_URL + u)

    logging.info(f"parsing emojis for {u}")
    emojis.extend(get_emojis(r.content.decode()))

# download the emojis (this takes forever)
logging.info("starting the big download")
save_all_emojis_to_disk(emojis)

logging.info("FINISHED SLACKMOJI DOWNLOAD")
