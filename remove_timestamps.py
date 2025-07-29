import os
import re
import glob


def remove_timestamps(input_file, output_file=None):
    """
    Remove timestamps from transcript file and save to a new file or overwrite existing file.
    Timestamp format: [00:00:00.000 --> 00:00:04.640]
    """
    if output_file is None:
        output_file = (
            input_file  # Overwrite the original file if no output file is specified
        )

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Use regex to remove timestamp patterns
    # This matches patterns like [00:00:00.000 --> 00:00:04.640]
    cleaned_text = re.sub(
        r"\[\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\]\s*", "", content
    )

    # Write the cleaned text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    return output_file


def process_directory(directory, output_dir=None):
    """
    Process all .txt files in the given directory
    """
    # Get all .txt files in the directory
    transcript_files = glob.glob(os.path.join(directory, "*.txt"))

    for file_path in transcript_files:
        file_name = os.path.basename(file_path)

        if output_dir:
            # If output directory is specified, save cleaned files there
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, file_name)
            print(f"Processing {file_name} -> {output_path}")
            remove_timestamps(file_path, output_path)
        else:
            # Otherwise, overwrite the original files
            print(f"Processing {file_name} (overwriting)")
            remove_timestamps(file_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove timestamps from transcript files"
    )
    parser.add_argument("directory", help="Directory containing transcript files")
    parser.add_argument(
        "--output", "-o", help="Output directory for cleaned files (optional)"
    )
    parser.add_argument(
        "--backup", "-b", action="store_true", help="Create backup of original files"
    )

    args = parser.parse_args()

    if args.backup and not args.output:
        # If backup is requested but no output directory specified, create a 'cleaned' directory
        args.output = os.path.join(
            os.path.dirname(args.directory), "cleaned_transcripts"
        )

    process_directory(args.directory, args.output)

    print("All transcript files processed successfully!")
