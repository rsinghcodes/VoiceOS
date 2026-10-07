"""
Text chunking utilities for RAG document processing.
Supports chunk size and overlap limits while preserving sentence boundaries.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    """Represents a chunked segment of text with business metadata."""
    chunk_id: str
    text: str
    business_id: str
    document_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def recursive_chunk_text(
    text: str,
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> List[str]:
    """
    Split text into chunks aiming for chunk_size characters with overlap.
    Preserves paragraph or sentence boundaries where possible.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    # Split by paragraphs or sentences
    paragraphs = clean_text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself is longer than chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = para.replace(". ", ".\n").split("\n")
                sub_chunk = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(sub_chunk) + len(sent) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk} {sent}".strip()
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
