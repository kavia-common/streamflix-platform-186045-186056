import os
from typing import Iterator, Optional, Tuple

from starlette.responses import StreamingResponse, Response


CHUNK_SIZE = 1024 * 1024  # 1MB default chunk size


def _parse_range(range_header: Optional[str], file_size: int) -> Tuple[int, int]:
    """
    Parse a Range header into start and end bytes.
    Returns a tuple (start, end) inclusive. If no range, returns (0, file_size - 1).
    """
    if not range_header or "=" not in range_header:
        return 0, file_size - 1

    units, _, range_spec = range_header.partition("=")
    if units.strip().lower() != "bytes":
        return 0, file_size - 1

    start_str, _, end_str = range_spec.partition("-")
    if start_str == "":
        # suffix range, e.g., bytes=-500
        suffix = int(end_str) if end_str.isdigit() else 0
        start = max(file_size - suffix, 0)
        end = file_size - 1
    else:
        start = int(start_str) if start_str.isdigit() else 0
        end = int(end_str) if end_str.isdigit() else file_size - 1

    start = max(0, start)
    end = min(end, file_size - 1)
    if start > end:
        start, end = 0, file_size - 1
    return start, end


def _file_chunk_generator(file_path: str, start: int, end: int) -> Iterator[bytes]:
    with open(file_path, "rb") as f:
        f.seek(start)
        bytes_remaining = end - start + 1
        while bytes_remaining > 0:
            read_length = min(CHUNK_SIZE, bytes_remaining)
            data = f.read(read_length)
            if not data:
                break
            bytes_remaining -= len(data)
            yield data


# PUBLIC_INTERFACE
def range_stream_response(file_path: str, filename: Optional[str], range_header: Optional[str], content_type: str = "video/mp4") -> Response:
    """
    Return a StreamingResponse supporting HTTP Range requests for the given file.
    """
    file_size = os.path.getsize(file_path)
    start, end = _parse_range(range_header, file_size)
    content_length = end - start + 1
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Content-Length": str(content_length),
        "Content-Type": content_type,
    }
    if filename:
        headers["Content-Disposition"] = f'inline; filename="{filename}"'

    status_code = 206 if start > 0 or end < file_size - 1 else 200
    return StreamingResponse(
        _file_chunk_generator(file_path, start, end),
        status_code=status_code,
        headers=headers,
        media_type=content_type,
    )
