import os
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-01-eb75fbb5d865")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
