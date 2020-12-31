from typing import List

import requests
from bs4 import BeautifulSoup

SLACKMOJI_URL = "https://slackmojis.com/"

class Emoji:
    name: str
    url: str

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __eq__(self, other):
        if isinstance(other, Emoji):
            return self.name == other.name
        return False

    def __str__(self):
        return self.name

def get_emojis(html: str) -> List[Emoji]:
    # an emoji is in a <img> with loading=lazy, and an equivalent alt and title
    # its all wrapped in an <a> with class=downloader
    soup = BeautifulSoup(html, "html.parser")

    emoji_a_tags = soup.find_all("a", "downloader")

    emojis = []

    for a_tag in emoji_a_tags:
        name =  a_tag.find("div", "name").string.strip()
        url = a_tag.find("img").get("src")

        emojis.append(Emoji(name, url))

    return emojis

# get the emojis
r = requests.get(SLACKMOJI_URL)
emojis = []

# get everything from the homepage
emojis.extend(get_emojis(r.content.decode()))

print([str(x) for x in emojis[:5]])


