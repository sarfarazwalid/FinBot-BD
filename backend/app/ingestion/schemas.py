from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class Document(BaseModel):
    text: str = Field(..., description="Raw document text content")
    source: str = Field(..., description="Source file name or identifier")
    file_type: str = Field(..., description="File extension type")


class Chunk(BaseModel):
    id: str = Field(..., description="Unique deterministic chunk identifier")
    text: str = Field(..., description="Chunked text content")
    source: str = Field(..., description="Source document name")
    language: str = Field(..., description="Detected language: en, bn, or mixed")
    chunk_index: int = Field(..., description="Zero-based chunk sequence number")
    created_at: str = Field(..., description="ISO-8601 timestamp of chunk creation")