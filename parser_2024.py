#!/usr/bin/env python
"""Parsing the 2024 training files."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from training_parser import training_parser as tp

if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    t_path = os.getenv("TRAINING_PATH")
    output = os.getenv("OUTPUT_DIRNAME")

    if t_path is None:
        print(f"Path {t_path} is not provided.")
        sys.exit(1)
    elif Path(t_path).exists() is False:
        print(f"Path {t_path} does not exist.")
        sys.exit(1)
    else:
        training_path = Path(t_path)

    YEAR_PATH = training_path.joinpath("trainingen 2024")

    files = tp.get_files([YEAR_PATH])
    for file in files:
        tp.parse_xlsx_2024_file(file)
    print(f"LOPEN: {len(tp.mapper['lopen'])}, {tp.mapper['lopen']}")
    print(f"KLIMMEN: {len(tp.mapper['klimmen'])}, {tp.mapper['klimmen']}")
    print(f"EINDSPEL: {len(tp.mapper['eind spel'])}, {tp.mapper['eind spel']}")
    for x, v in tp.mapper.items():
        out = training_path / output / f"{x}.txt"
        out.write_text("\n".join(v))
    print("Done.")
