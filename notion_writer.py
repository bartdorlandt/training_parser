#!/usr/bin/env python3
"""Writing the training schema to Notion."""

import csv
import os
import re

from dotenv import load_dotenv

from notion.notion import FILTER, Notion, TrainingData


def filter_name_type_tags(data: TrainingData) -> FILTER:
    """Filter on name, type and tags."""
    tags = [
        {
            "property": "Tags",
            "multi_select": {
                "contains": tag,
            },
        }
        for tag in data.tags
    ]
    return {
        "filter": {
            "and": [
                {
                    "property": "Name",
                    "rich_text": {
                        "equals": data.name,
                    },
                },
                {
                    "property": "Type",
                    "select": {
                        "equals": data.type,
                    },
                },
            ]
            + tags
        }
    }


def name_extend(name: str) -> str:
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    """Extend the name."""
    r = re.compile(r"(.*?)(\d+)$")
    if m := r.search(name):
        i = int(m[2]) + 1
        return f"{m[1]}{i}"
    else:
        return f"{name}1"


def read_csv(filename: str) -> list[TrainingData]:
    """Read the csv file."""
    training_data = []
    with open(filename, newline="") as csvfile:
        rows = csv.reader(csvfile, delimiter=",")
        for row in rows:
            if rows.line_num == 1:
                continue
            name = row[0].strip()
            name = unique_name(training_data, name)

            training_data.append(
                TrainingData(
                    name=name,
                    type=row[1].strip(),
                    tags=[x.strip() for x in re.split(r"[,&]", row[2]) if x],
                    content=row[3],
                )
            )
    return training_data


def unique_name(training_data: list[TrainingData], name: str) -> str:
    """Make the name unique."""
    if name in [data.name for data in training_data if data]:
        if short_list := [
            data.name for data in training_data if re.search(rf"{name}\d+", data.name)
        ]:
            name = name_extend(short_list[-1])
        else:
            name = name_extend(name)
    return name


def main():
    """Execute the main function."""
    load_dotenv()
    filename = os.environ["TRAINING_FILE"]
    training_datas = read_csv(filename)
    token = os.getenv("NOTION_TOKEN")
    n = Notion(token)
    db_id = os.getenv("NOTION_DB")

    _ = n.get_database(db_id)

    for training_data in training_datas:
        f = filter_name_type_tags(training_data)
        exists = n.query_db_with_filter(db_id, filter=f)
        if exists.get("results"):
            print("Found. No need to add.")
            print("--", training_data)
        try:
            n.create_page_with_content(database_id=db_id, data=training_data)
        except Exception as e:
            print(e)
            print("Failed:", training_data)


if __name__ == "__main__":
    main()
