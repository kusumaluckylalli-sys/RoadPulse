import sqlite3

DB_NAME = "potholes.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS potholes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            citizen_username TEXT,
            ward TEXT NOT NULL,
            road TEXT NOT NULL,
            landmark TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            image_path TEXT,
            size TEXT,
            depth TEXT,
            pothole_count TEXT,
            road_type TEXT,
            traffic_problem TEXT,
            accident_reported TEXT,
            urgency INTEGER,
            road_usage TEXT,
            water_filled TEXT,
            remarks TEXT,
            priority_score INTEGER,
            priority_level TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ai_result TEXT,
            ai_confidence REAL DEFAULT 0,
            ai_severity TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pothole_id INTEGER,
            alert_type TEXT,
            message TEXT,
            priority_level TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safe migrations for databases created by earlier RoadPulse versions.
    cur.execute("PRAGMA table_info(potholes)")
    existing = {row[1] for row in cur.fetchall()}
    migrations = {
        "citizen_username": "TEXT",
        "ai_result": "TEXT",
        "ai_confidence": "REAL DEFAULT 0",
        "ai_severity": "TEXT",
    }
    for column, definition in migrations.items():
        if column not in existing:
            cur.execute(f"ALTER TABLE potholes ADD COLUMN {column} {definition}")

    conn.commit()
    conn.close()


def add_pothole(**data):
    columns = list(data.keys())
    values = [data[c] for c in columns]
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(columns)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO potholes ({column_sql}) VALUES ({placeholders})", values)
    report_id = cur.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_all_potholes():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM potholes ORDER BY id DESC", conn)
    conn.close()
    return df


def get_report_by_id(report_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM potholes WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_status(report_id, status):
    conn = get_connection()
    conn.execute("UPDATE potholes SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()


def update_ai_result(report_id, result, confidence, severity):
    conn = get_connection()
    conn.execute(
        "UPDATE potholes SET ai_result = ?, ai_confidence = ?, ai_severity = ? WHERE id = ?",
        (result, float(confidence), severity, report_id),
    )
    conn.commit()
    conn.close()


def add_alert(report_id, alert_type, message, priority_level):
    conn = get_connection()
    conn.execute(
        "INSERT INTO alerts (pothole_id, alert_type, message, priority_level) VALUES (?, ?, ?, ?)",
        (report_id, alert_type, message, priority_level),
    )
    conn.commit()
    conn.close()


def get_alerts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_alert_read(alert_id):
    conn = get_connection()
    conn.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
