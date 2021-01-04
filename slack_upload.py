import glob
import logging
import math
import time

import requests
from requests_toolbelt import MultipartEncoder

import secret as s

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y/%m/%d %H:%M:%S",
    handlers=[
        logging.StreamHandler()
    ]
)

headers = {
    "Cookie": s.COOKIES,
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Sec-GPC": "1"
}

def upload_emoji(emoji_fp: str, csrf_token: str):
    filename = emoji_fp.split("/")[1]
    split = filename.split(".")
    emoji_name = split[0]
    extension = ".".join(split[1:])

    if extension == "x-icon" or extension == "vnd.microsoft.icon" or extension == "x-ms-bmp" or extension == "bmp":
        logging.warning(f"skipping emoji due to unsupported file type (.{extension}): {emoji_name}")
        return

    mime = f"image/{extension}"

    m = MultipartEncoder(
        fields = {
            "mode": "data",
            "name": emoji_name,
            "image": (filename, open(emoji_fp, "rb"), mime),
            "token": csrf_token,
            "_x_reason": "customize-emoji-add",
            "_x_mode": "online"
        }
    )

    h = headers.copy()
    h["Content-Type"] = m.content_type

    r = requests.post(s.SLACK_URL + f"/api/emoji.add", headers=h, data=m)
    resp = r.json()

    if resp["ok"]:
        logging.debug(f"successfully uploaded {emoji_name}")
    elif resp["error"].startswith("error_name_taken"):
        logging.warning(f"failed to upload {emoji_name}: name already taken")
    elif resp["error"] == "ratelimited":
        logging.warning(f"got rate limited, sleeping for 30 sec")
        time.sleep(30)
        upload_emoji(emoji_fp, csrf_token)
    else:
        logging.error(f"failed to upload {emoji_name}: " + r.content.decode())

def get_csrf_token() -> str:
    r = requests.get(s.SLACK_URL + "/customize/emoji", headers=headers)
    
    body = r.content.decode()
    token = body.split(',"api_token":"')[1].split('","vvv_paths":')[0]

    return token

token = get_csrf_token()
logging.info(f"got csrf token: " + token)

emoji_fp_list = glob.glob("emojis/*")
num_emojis = len(emoji_fp_list)
logging.info(f"there are {num_emojis} emojis to upload")

counter = 0
percent = 0

logging.info("STARTING SLACK UPLOAD")

for i in range(counter, len(emoji_fp_list)):
    new_percent = math.floor((counter / num_emojis) * 100)
    if new_percent > percent:
        percent = new_percent
        logging.info(f"emoji uploads: {percent}% completed ({counter} emojis)")

    upload_emoji(emoji_fp_list[i], token)

    counter += 1

logging.info("FINISHED SLACK UPLOAD")
