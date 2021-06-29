import os
from pathlib import Path
from shutil import copy2
from tempfile import NamedTemporaryFile


def pad(path: Path) -> None:
    """Pad the text file (in place) pointed by `path` with white spaces.
    
    path: The path of the file
    """
    with path.open() as lines:
        line_lenghts = set(len(line.rstrip(os.linesep)) for line in lines)

    if len(line_lenghts) == 1:
        # Every lines have the same lenght, so we can skip.
        # Warning: There is case where the length of two consecutive lines could sum up
        #          to the unique value of line_lengths. We choose to skip this case for
        #          now, and hope this case does not happen.
        return

    max_line_lenght = max(line_lenghts)

    with NamedTemporaryFile("w") as dest_file:
        with path.open() as source_lines:
            for source_line in source_lines:
                stripped_source_line = source_line.rstrip()
                padding = max_line_lenght - len(stripped_source_line)
                dest_file.write(f"{stripped_source_line}{' '*padding}\n")

        dest_file.flush()
        copy2(dest_file.name, path)
