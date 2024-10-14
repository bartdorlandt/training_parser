"""Notion class."""

import json
from dataclasses import dataclass

import requests

FILTER = dict


@dataclass
class TrainingData:
    """Training data."""

    name: str
    type: str
    tags: list[str]
    content: str = ""

    def __post_init__(self) -> None:
        """Post init."""
        self.tags = [tag.strip() for tag in self.tags if tag.strip()]


class Notion:
    """Notion class."""

    version = "2022-06-28"

    def __init__(self, token: str) -> None:
        """Initialize the Notion class."""
        self.token = token
        self.url = "https://api.notion.com/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.version,
        }
        self.properties: dict = {}
        self.database: dict = {}
        self.timeout = 15
        self.database_id: str = ""

    def _request_ret_json(self, func: requests.Request, url: str, data: dict | None = None) -> dict:
        """Request and return JSON."""
        r = func(url, timeout=self.timeout, headers=self.headers, json=data)
        return json.loads(r.content.decode("utf-8"))

    def get_database(self, database_id: str) -> dict:
        """Get the database, store it and its properties."""
        self.database_id = database_id
        url = f"{self.url}v1/databases/{database_id}"
        output = self._request_ret_json(requests.get, url)
        self.database = output
        self.properties = output.get("properties", {})
        return output

    def create_page_in_db(self, database_id: str, data: TrainingData) -> dict:
        """Create a page."""
        url = f"{self.url}v1/pages"
        data = self.generate_page_properties(data)
        data["parent"] = {"database_id": database_id}
        return self._request_ret_json(requests.post, url, data=data)

    def generate_page_properties(self, data: TrainingData) -> dict:
        """Create page properties."""
        return {
            "properties": {
                "Name": {"title": [{"text": {"content": data.name}}]},
                "Type": {"select": {"name": data.type}},
                "Tags": {"multi_select": [{"name": tag} for tag in data.tags]},
            }
        }

    def create_child_block(self, page_id: str, content: str) -> dict:
        """Create a child block."""
        url = f"{self.url}v1/blocks/{page_id}/children"
        data = {
            "children": [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": "Uitleg"}}]},
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content,
                                },
                            }
                        ]
                    },
                },
            ]
        }
        return self._request_ret_json(requests.patch, url, data=data)

    def create_page_with_content(self, database_id: str, data: TrainingData) -> dict:
        """Create a page with content."""
        page = self.create_page_in_db(database_id, data)
        if data.content and page.get("id"):
            return self.create_child_block(page.get("id"), data.content)
        else:
            return page

    def query_db_with_filter(self, database_id: str, filter: FILTER) -> dict:
        """Query the database using a filter."""
        url = f"{self.url}v1/databases/{database_id}/query"
        return self._request_ret_json(requests.post, url, data=filter)
