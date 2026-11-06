import uvicorn
import os
import sys

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"===========================================================")
    print(f" Starting KratosSecure Healthcare Operational Environment")
    print(f" Dashboard URL: http://localhost:{port}")
    print(f" OpenAPI Docs:  http://localhost:{port}/docs")
    print(f"===========================================================")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
