import os
import sys
import shutil

# Ensure project root is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# On Vercel's serverless environment, filesystem is read-only except /tmp.
# If running on Vercel and SQLite is used, copy pre-seeded database to /tmp or configure /tmp path.
if os.getenv("VERCEL"):
    tmp_db_path = "/tmp/kratos_hospital.db"
    bundled_db_path = os.path.join(root_dir, "kratos_hospital.db")
    if not os.path.exists(tmp_db_path) and os.path.exists(bundled_db_path):
        try:
            shutil.copyfile(bundled_db_path, tmp_db_path)
        except Exception:
            pass
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{tmp_db_path}")

from backend.app.main import app
