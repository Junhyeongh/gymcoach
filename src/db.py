import os
import sqlite3
import pandas as pd


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Return a SQLite connection with rows as dict-like objects."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_from_csv(db_path: str = "data/gymcoach.db",
                     csv_path: str = "data/megaGymDataset.csv") -> None:
    """Create or replace the 'exercises' table in the SQLite database
    using the megaGymDataset CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Drop the index-like column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Rename to nicer column names
    rename_map = {
        "Title": "title",
        "Desc": "description",
        "Type": "type",
        "BodyPart": "body_part",
        "Equipment": "equipment",
        "Level": "level",
        "Rating": "rating",
        "RatingDesc": "rating_desc",
    }
    df = df.rename(columns=rename_map)

    conn = get_db_connection(db_path)

    # Replace the table completely each time
    df.to_sql("exercises", conn, if_exists="replace", index=False)

    conn.close()
