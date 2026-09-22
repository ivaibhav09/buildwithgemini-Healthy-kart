"""Script to create a Serverless Vertex AI RAG corpus and import pg49513.txt."""

import json
import os
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-01-eb75fbb5d865"
LOCATION = "us-central1"
GCS_PATH = "gs://smart-pantry-chef-media-qwiklabs-gcp-01-eb75fbb5d865/rag/pg49513.txt"

print(f"Initializing Vertex AI for project={PROJECT_ID}, location={LOCATION}...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

print("1. Updating RAG Engine config to Serverless mode...")
cfg_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
try:
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg_name,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
    print("Serverless RAG Engine config updated successfully.")
except Exception as e:
    print(f"Note on RAG Engine config update: {e}")

print("2. Creating Serverless RAG Corpus...")
corpus = rag.create_corpus(
    display_name="smart-pantry-chef-herbal-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print(f"Corpus created: {corpus.name}")

print(f"3. Importing file from {GCS_PATH}...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
)
print(f"Import task triggered. Imported files count: {resp.imported_rag_files_count}")

# Save corpus info for the application tools
os.makedirs("data", exist_ok=True)
corpus_info = {
    "corpus_name": corpus.name,
    "project_id": PROJECT_ID,
    "location": LOCATION,
    "gcs_path": GCS_PATH,
}
with open("data/rag_corpus_info.json", "w") as f:
    json.dump(corpus_info, f, indent=2)

print("Saved corpus info to data/rag_corpus_info.json")
