import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import starlette
print("Starlette version:", starlette.__version__)

from backend.app.main import app
print("App imported successfully.")

from fastapi.testclient import TestClient
print("Imported TestClient.")

c = TestClient(app)
print("Instantiated TestClient.")
r = c.get("/health")
print("Response:", r.status_code, r.json())

