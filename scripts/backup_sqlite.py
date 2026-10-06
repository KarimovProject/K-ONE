"""Daily consistent backup of the SQLite database (shared-hosting deployment).

Uses SQLite's online backup API, so it is safe while the app is writing.
Keeps the newest KEEP copies and deletes older ones.

Usage: python scripts/backup_sqlite.py <db_path> <backup_dir> [keep]
"""

import datetime
import pathlib
import sqlite3
import sys

KEEP = 14


def main() -> None:
    db_path = pathlib.Path(sys.argv[1]).expanduser()
    backup_dir = pathlib.Path(sys.argv[2]).expanduser()
    keep = int(sys.argv[3]) if len(sys.argv) > 3 else KEEP

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    target = backup_dir / f"db-{stamp}.sqlite3"

    source = sqlite3.connect(db_path)
    dest = sqlite3.connect(target)
    try:
        source.backup(dest)
    finally:
        dest.close()
        source.close()

    copies = sorted(backup_dir.glob("db-*.sqlite3"))
    for old in copies[:-keep]:
        old.unlink()
    print(f"backup written: {target}")


if __name__ == "__main__":
    main()
