import json
import tempfile
import unittest
from pathlib import Path

from scripts.rag.records import (
    ChunkRecord,
    InvalidChunkRecordError,
    build_chunk_record,
    read_jsonl,
    write_jsonl,
)
from scripts.rag.settings import SELECTED_ISSUES
from scripts.rag.upload_nomic import _validate_selected_issues


class RagRecordTests(unittest.TestCase):
    def test_builds_normalized_chunk_record(self) -> None:
        record = build_chunk_record(
            issue=69,
            sequence=3,
            text="  Un destino interesante.  ",
            source="traveling69.pdf",
            headings=["Europa", " España "],
            pages=[5, 4, 5],
        )

        self.assertEqual(record.id, "traveling69-00003")
        self.assertEqual(record.text, "Un destino interesante.")
        self.assertEqual(record.headings, "Europa > España")
        self.assertEqual(record.pages, "4,5")

    def test_rejects_record_without_pages(self) -> None:
        with self.assertRaises(InvalidChunkRecordError):
            build_chunk_record(
                issue=69,
                sequence=1,
                text="Contenido",
                source="traveling69.pdf",
                headings=[],
                pages=[],
            )

    def test_writes_and_reads_jsonl(self) -> None:
        records = [
            ChunkRecord(
                id="traveling69-00001",
                text="Contenido",
                source="traveling69.pdf",
                issue=69,
                headings="Chile",
                pages="10",
            )
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "traveling69.jsonl"
            count = write_jsonl(path, records)
            loaded = list(read_jsonl([path]))

        self.assertEqual(count, 1)
        self.assertEqual(loaded, records)

    def test_rejects_duplicate_ids_across_files(self) -> None:
        value = {
            "id": "traveling69-00001",
            "text": "Contenido",
            "source": "traveling69.pdf",
            "issue": 69,
            "headings": "Chile",
            "pages": "10",
        }

        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / "first.jsonl", Path(directory) / "second.jsonl"]
            for path in paths:
                path.write_text(json.dumps(value) + "\n", encoding="utf-8")

            with self.assertRaises(InvalidChunkRecordError):
                list(read_jsonl(paths))

    def test_rejects_upload_when_selected_issues_are_incomplete(self) -> None:
        records = [{"issue": issue} for issue in SELECTED_ISSUES[:-1]]

        with self.assertRaises(ValueError):
            _validate_selected_issues(records)

    def test_accepts_complete_issue_selection(self) -> None:
        records = [{"issue": issue} for issue in SELECTED_ISSUES]

        _validate_selected_issues(records)


if __name__ == "__main__":
    unittest.main()
