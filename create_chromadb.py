import chromadb
import os
import json
import chromadb.utils.embedding_functions as embedding_functions
from tqdm import tqdm

client = chromadb.PersistentClient()
collection = client.create_collection("k-elmer-video-transcripts")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)

# read title_url_map.json
url_map = {}
with open("title_url_map.json", "r") as file:
    url_map = json.load(file)

transcriptions_dir = "./transcriptions_new"

for filename in tqdm(os.listdir(transcriptions_dir)):
    if filename.endswith(".txt"):
        filepath = os.path.join(transcriptions_dir, filename)
        with open(filepath, "r") as file:
            url = url_map[filename[:-4] + ".m4a"]
            data = json.load(file)
            texts = [obj["text"] for obj in data]
            start_times = [obj["start"] for obj in data]
            end_times = [obj["end"] for obj in data]
            embeddings = openai_ef(texts)
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=[
                    {"source": filename, "start": start, "end": end, "url": url}
                    for start, end in zip(start_times, end_times)
                ],
                ids=[f"{filename}_{i}" for i in range(len(texts))],
            )
