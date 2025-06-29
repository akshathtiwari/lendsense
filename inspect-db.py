import sqlite3, os, sys
db = sys.argv[1] if len(sys.argv) > 1 else "checkpoints.db"

if not os.path.exists(db):
    print("DB file not found:", db); sys.exit(1)

con = sqlite3.connect(db)
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table'")]
print("Tables:", tables)
