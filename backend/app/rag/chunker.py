"""Text chunking engine with overlap for context preservation."""

import re
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger()

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 50


@dataclass
class Chunk:
    """A text chunk with metadata."""

    content: str
    index: int
    start_char: int
    end_char: int
    metadata: dict = field(default_factory=dict)


class TextChunker:
    """Split documents into semantic chunks with overlap."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """Split text into overlapping chunks using paragraph/heading boundaries."""
        if not text or not text.strip():
            return []

        base_metadata = metadata or {}

        # Normalize whitespace but preserve structure
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        chunks: list[Chunk] = []
        current_text = ""
        current_start = 0
        char_offset = 0

        for para in paragraphs:
            para_start = text.find(para, char_offset)
            if para_start == -1:
                para_start = char_offset
            para_end = para_start + len(para)

            # If adding this paragraph exceeds chunk size, finalize current chunk
            if current_text and len(current_text) + len(para) + 2 > self.chunk_size:
                chunks.append(Chunk(
                    content=current_text.strip(),
                    index=len(chunks),
                    start_char=current_start,
                    end_char=char_offset,
                    metadata={**base_metadata, "chunk_type": "paragraph"},
                ))

                # Overlap: keep last portion of current text
                overlap_text = current_text[-self.chunk_overlap:] if len(current_text) > self.chunk_overlap else ""
                current_text = overlap_text + "\n\n" + para
                current_start = para_start
            else:
                if not current_text:
                    current_start = para_start
                current_text = (current_text + "\n\n" + para).strip()

            char_offset = para_end

        # Don't forget the last chunk
        if current_text.strip():
            chunks.append(Chunk(
                content=current_text.strip(),
                index=len(chunks),
                start_char=current_start,
                end_char=char_offset,
                metadata={**base_metadata, "chunk_type": "paragraph"},
            ))

        # Merge very small chunks
        merged = self._merge_small_chunks(chunks, base_metadata)

        # Re-index
        for i, chunk in enumerate(merged):
            chunk.index = i

        logger.info(
            "text_chunked",
            total_chunks=len(merged),
            avg_size=sum(len(c.content) for c in merged) // max(len(merged), 1),
        )

        return merged

    def _merge_small_chunks(self, chunks: list[Chunk], metadata: dict) -> list[Chunk]:
        """Merge chunks that are too small with adjacent chunks."""
        if not chunks:
            return []

        merged: list[Chunk] = []
        buffer: list[Chunk] = []

        for chunk in chunks:
            buffer.append(chunk)
            combined_text = "\n\n".join(c.content for c in buffer)

            if len(combined_text) >= MIN_CHUNK_SIZE:
                merged.append(Chunk(
                    content=combined_text,
                    index=0,
                    start_char=buffer[0].start_char,
                    end_char=buffer[-1].end_char,
                    metadata={**metadata, "chunk_type": "merged"},
                ))
                buffer = []

        # Flush remaining
        if buffer:
            combined_text = "\n\n".join(c.content for c in buffer)
            if merged:
                # Merge with last chunk
                last = merged[-1]
                merged[-1] = Chunk(
                    content=last.content + "\n\n" + combined_text,
                    index=last.index,
                    start_char=last.start_char,
                    end_char=buffer[-1].end_char,
                    metadata=last.metadata,
                )
            else:
                merged.append(Chunk(
                    content=combined_text,
                    index=0,
                    start_char=buffer[0].start_char,
                    end_char=buffer[-1].end_char,
                    metadata={**metadata, "chunk_type": "merged"},
                ))

        return merged
