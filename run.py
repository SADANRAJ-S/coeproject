import uvicorn
import sys
from pathlib import Path
from backend.seed_data import seed_database
from backend.database import DB_PATH

def main():
    print("=" * 70)
    print(" Verified Resolution Assistant - 24/7 Hospital IT Support Team")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print("[+] Initializing SQLite database and seeding synthetic hospital IT data...")
        seed_database()
    else:
        print(f"[+] Database verified at: {DB_PATH}")

    print("[+] Starting FastAPI server on http://127.0.0.1:8000 ...")
    print("[+] Press Ctrl+C to stop the server.")
    print("=" * 70)

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
