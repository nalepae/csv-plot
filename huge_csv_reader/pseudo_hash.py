import hashlib
import os
from pathlib import Path


def pseudo_hash(path: Path, string: str = "") -> str:
    """Compute a pseudo hash based on :
    - The file size
    - The file last modificationdate
    - A given string

    (Real hash is too long to compute for big file.)
    """
    string = "-".join([str(os.path.getsize(path)), str(os.path.getmtime(path)), string])
    return str(hashlib.md5(bytes(string, "utf-8")).hexdigest())
