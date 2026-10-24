import csv
from collections import Counter
from pathlib import Path

HEADERS = [
    "id", "title", "url", "category", "status", "priority",
    "human_reply_count", "solved", "created_at", "last_posted_at"
]

class ReporterService():

    def __init__(self):
        pass

    def _sanitize_cell(self,value):
        text = "Not determined" if value is None else str(value)
        if text.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + text
        return text

    def write_csv(self,topics, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            for topic in topics:
                writer.writerow({
                    key: self._sanitize_cell(topic.get(key)) for key in HEADERS
                })
        return path

    def count_topics_by_status(self, topics):
        counts = Counter(t["status"] for t in topics)
        return {key: counts.get(key, 0) for key in (
            "UNANSWERED", "FOLLOW_UP", "NEEDS_REVIEW", "ACTIVE",
            "SOLVED", "EXCLUDED"
        )}

