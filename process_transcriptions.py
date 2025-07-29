import os
import re
import json
from datetime import datetime, timedelta


def parse_timestamp(timestamp):
    return datetime.strptime(timestamp, "%H:%M:%S.%f")


def format_timestamp(timestamp):
    return timestamp.strftime("%H:%M:%S.%f")[:-3]


def process_transcriptions(directory):
    transcription_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    for file in transcription_files:
        file_path = os.path.join(directory, file)
        with open(file_path, "r") as f:
            lines = f.readlines()

        transcription_data = []
        for line in lines:
            match = re.match(
                r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s+(.*)",
                line,
            )
            if match:
                start, end, text = match.groups()
                transcription_data.append({"start": start, "end": end, "text": text})

        combined_data = []
        current_chunk = {"start": None, "end": None, "text": ""}
        current_duration = timedelta()

        for entry in transcription_data:
            start_time = parse_timestamp(entry["start"])
            end_time = parse_timestamp(entry["end"])
            duration = end_time - start_time

            if current_chunk["start"] is None:
                current_chunk["start"] = entry["start"]

            if current_duration + duration <= timedelta(seconds=30):
                current_chunk["text"] += " " + entry["text"]
                current_chunk["end"] = entry["end"]
                current_duration += duration
            else:
                combined_data.append(current_chunk)
                current_chunk = {
                    "start": entry["start"],
                    "end": entry["end"],
                    "text": entry["text"],
                }
                current_duration = duration

        if current_chunk["start"] is not None:
            combined_data.append(current_chunk)

        # print data

        # # Save combined data to a new file
        os.makedirs("transcriptions_new", exist_ok=True)
        output_file_path = os.path.join("transcriptions_new", f"{file}")
        with open(output_file_path, "w") as f:
            json.dump(combined_data, f, indent=4)


if __name__ == "__main__":
    process_transcriptions("./transcriptions")
