import os
import modal
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from openai import OpenAI
from fastapi.responses import StreamingResponse


image = modal.Image.from_registry("python:3.11-slim-bookworm").pip_install(
    ["fastapi[standard]", "openai", "chromadb"]
)

app = modal.App("Leela-FAQuantum", image=image)
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)


def llm_streamer(question: str, text: str, urls: list):
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"I will give you some information that I have selected from video transcriptions. I want you to answer my question only using the information from the given text. Provide as much useful detail in your answer as possible from the text. Prioritize information from the first texts and do not use any other information besides the text I give you to answer my question. \n\nText: {text}\n\nQuestion: {question}",
            },
        ],
        stream=True,
    )

    for chunk in completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content.encode()
    yield "\n\n<END>".encode()
    yield "\n".join(urls).encode()


def timestamp_to_seconds(timestamp: str) -> int:
    return int(sum(x * float(t) for x, t in zip([3600, 60, 1], timestamp.split(":"))))


@app.function(
    volumes={"/mnt/data": modal.Volume.from_name("leela-faquantum")},
)
@modal.fastapi_endpoint()
def rag(question: str, n_results: int):
    print("Received question:", question)
    client = chromadb.PersistentClient(path="/mnt/data/chroma")
    collection = client.get_or_create_collection("k-elmer-video-transcripts")
    print("Querying ChromaDB...")

    results = collection.query(
        query_embeddings=openai_ef([question]),
        n_results=n_results,
    )

    print("Streaming response...")
    urls = [
        result["url"] + f"&t={timestamp_to_seconds(result['start'])}"
        for result in results["metadatas"][0]
    ]

    return StreamingResponse(
        llm_streamer(question, results["documents"], urls),
        media_type="text/event-stream",
    )
