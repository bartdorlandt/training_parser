#!/usr/bin/env python
"""Filter out unique lines from the training files."""
from pathlib import Path

from training_parser import training_parser as tp

TRAINING_PATH = Path("/Users/bart/Documents/Sport/Fit Jeugd Training")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    for x, v in tp.mapper.items():
        p = TRAINING_PATH.joinpath(f"{x}.txt")
        t = p.read_text()
        a = set(t.split("\n"))

        out = TRAINING_PATH / "Bart" / f"{x}_unique.txt"
        out.write_text("\n".join(a))
    print("Done.")
