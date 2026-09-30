import sqlite3
from pathlib import Path
import pandas as pd

RAW = Path("data/raw")
DB = Path("data/olist.db")

conn = sqlite3.connect(DB)
for csv in RAW.glob("*.csv"):
    name = csv.stem.replace("olist_", "").replace("_dataset", "")
    df = pd.read_csv(csv)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"Loaded {name}: {len(df):,} rows")
conn.close()
