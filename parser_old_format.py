#!/usr/bin/env python
"""Parsing the old format training files."""
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

    years = [2019, 2020, 2021, 2022, 2023]
    year_paths = tp.generate_year_paths(training_path, years)
    files = tp.get_files(year_paths)
    total_list = []
    for file in files:
        total_list.extend(tp.parse_xlsx_2023_file(file))
    out = training_path / output / "2023.txt"
    out.write_text("\n".join(list(set(total_list))))
