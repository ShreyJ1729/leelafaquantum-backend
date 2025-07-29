import subprocess
import os

os.mkdir("videos_wav")


def convert_to_wav(title):
    return f'ffmpeg -i "./videos/{title}.m4a" -ar 16000 -ac 1 -c:a pcm_s16le "./videos_wav/{title}.wav"'


# iterate over videos directory, converting each m4a file to wav and saving to videos_wav directory
for video in os.listdir("videos"):
    if video.endswith(".m4a"):
        title = video[:-4]
        os.system(convert_to_wav(title))
        print(f"Converted {title}.m4a to {title}.wav")
