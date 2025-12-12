from __future__ import annotations

import mimetypes
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Tuple

from fastapi import HTTPException, status

from app.core.config import get_settings

_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


@dataclass(frozen=True)
class FileRange:
    start: int
    end: int  # inclusive
    size: int
    content_type: str


def _guess_content_type(path: Path, fallback: str) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or fallback


def _parse_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    """
    Parse `Range: bytes=start-end` (single range only).

    Supports:
      - bytes=0-499
      - bytes=500-
      - bytes=-500 (suffix range)

    Returns:
      (start, end) inclusive

    Raises:
      HTTPException(416) for invalid ranges.
    """
    match = _RANGE_RE.fullmatch(range_header.strip())
    if not match:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    start_s, end_s = match.group(1), match.group(2)

    if start_s == "" and end_s == "":
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    if start_s == "":
        # Suffix range: last N bytes
        suffix_len = int(end_s)
        if suffix_len <= 0:
            raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        start = max(0, file_size - suffix_len)
        end = file_size - 1
        return start, end

    start = int(start_s)
    end = int(end_s) if end_s != "" else file_size - 1

    if start >= file_size:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
    if end < start:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    end = min(end, file_size - 1)
    return start, end


# PUBLIC_INTERFACE
def build_file_range(file_path: str, content_type_fallback: str, range_header: str | None) -> FileRange:
    """Build a FileRange for a given file and optional Range header."""
    settings = get_settings()
    base = Path(settings.video_library_path)

    path = Path(file_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    # If the file is within the library path by relative reference, also allow joining:
    if not path.exists():
        candidate = (base / file_path).resolve()
        if candidate.exists():
            path = candidate

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found")

    size = os.stat(path).st_size
    content_type = _guess_content_type(path, fallback=content_type_fallback)

    if range_header:
        start, end = _parse_range_header(range_header, size)
    else:
        start, end = 0, size - 1

    return FileRange(start=start, end=end, size=size, content_type=content_type)


# PUBLIC_INTERFACE
def iter_file_bytes(path: Path, start: int, end: int) -> Generator[bytes, None, None]:
    """Stream bytes from `path` from start..end inclusive in chunks."""
    settings = get_settings()
    chunk_size = max(64 * 1024, settings.stream_chunk_size)

    with path.open("rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            data = f.read(min(chunk_size, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data
