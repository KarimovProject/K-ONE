import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Minimal structured formatter; message producers must never include secrets."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "scope"):
            payload["scope"] = record.scope
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
