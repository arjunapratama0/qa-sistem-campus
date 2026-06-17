import json
from pathlib import Path

from app.application.schemas.example import QAExampleRead
from app.core.config import get_settings

settings = get_settings()


class ExampleService:
    def list_examples(self, limit: int = 12) -> list[QAExampleRead]:
        path = Path(settings.qa_dataset_path)
        if not path.is_absolute():
            path = Path.cwd() / path

        if not path.exists():
            return []

        raw_examples = json.loads(path.read_text(encoding="utf-8-sig"))
        examples = [
            QAExampleRead(
                category=item.get("kategori", "Umum"),
                question=item.get("pesan_user", ""),
                ideal_answer=item.get("jawaban_ideal", ""),
            )
            for item in raw_examples
            if item.get("pesan_user")
        ]
        return examples[:limit]
