import voyageai
from config.settings import settings
import re

client = voyageai.Client(api_key=settings.voyage_api_key)


def chunk_by_section(document_text):
    chunks = re.split(r"(?m)(?=^## )", document_text)

    return [s.strip() for s in chunks if s.strip()]


def embed_texts(texts: list[str], model: str = "voyage-4") -> list[list[float]]:
    result = client.embed(texts, model=model, output_dimension=2048)

    return result.embeddings
