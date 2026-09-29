"""Print advice ids of real-dataset needs: `without_qc` or `without_draft`. Loads ~/.hautel/engine.env like the CLI."""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

env = pathlib.Path.home() / ".hautel" / "engine.env"
if env.exists():
    for line in env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

from engine import db  # noqa: E402

SQL = {
    "without_qc": (
        "select a.id::text id from advice a join marketing_needs n on n.id=a.need_id "
        "where n.dataset='real' and a.kind='advice' and a.qc is null order by a.created_at"
    ),
    "without_draft": (
        "select a.id::text id from advice a join marketing_needs n on n.id=a.need_id "
        "where n.dataset='real' and a.kind='advice' and not exists "
        "(select 1 from advice d where d.parent_id=a.id and d.kind='draft') order by a.created_at"
    ),
}

with db.connect() as conn:
    for row in conn.execute(SQL[sys.argv[1]]).fetchall():
        print(row["id"])
