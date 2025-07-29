from tqdm import tqdm
from pytubefix import Channel
import json
import subprocess
import os

process = subprocess.Popen(["youtube-po-token-generator"], stdout=subprocess.PIPE)

stdout, stderr = process.communicate()
token = json.loads(stdout)


def po_token_verifier():
    return (token["visitorData"], token["poToken"])


c = Channel(
    "https://www.youtube.com/@KElmerTinkersAcademy",
    use_po_token=True,
    po_token_verifier=po_token_verifier,
)
print(f"Downloading videos by: {c.channel_name}")

for video in tqdm(c.videos):
    title = video.title.replace("/", " or ") + ".m4a"
    url = video.watch_url

    if not os.path.exists(f"./videos/{title}"):
        video.streams.get_audio_only().download("videos", filename=title)
