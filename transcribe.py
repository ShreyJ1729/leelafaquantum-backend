import os
import subprocess
import multiprocessing
from tqdm import tqdm

whisper_cli = "/Users/shreyjoshi/dev/whisper.cpp/build/bin/whisper-cli"

os.makedirs("transcriptions", exist_ok=True)


def transcribe(video):
    if video.endswith(".wav"):
        title = video.rsplit(".", 1)[0]
        with open(f"transcriptions/{title}.txt", "w+") as output_file:
            subprocess.run([whisper_cli, f"videos_wav/{video}"], stdout=output_file)


def main():
    videos = [video for video in os.listdir("videos_wav") if video.endswith(".wav")]

    with multiprocessing.Pool(processes=4) as pool:
        list(
            tqdm(pool.imap(transcribe, videos), total=len(videos), desc="Transcribing")
        )


if __name__ == "__main__":
    main()
