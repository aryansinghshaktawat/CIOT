import sqlite3
from typing import List, Dict, Any, Optional
import datetime

class HistoricalDataManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                carrier TEXT,
                location TEXT,
                owner TEXT,
                ported INTEGER DEFAULT 0,
                change_type TEXT,
                change_date TEXT,
                confidence_score REAL,
                investigation_id TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_record(self, phone_number: str, carrier: str, location: str, owner: str, ported: bool, change_type: str, confidence_score: float, investigation_id: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO phone_history (phone_number, carrier, location, owner, ported, change_type, change_date, confidence_score, investigation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (phone_number, carrier, location, owner, int(ported), change_type, datetime.datetime.now().isoformat(), confidence_score, investigation_id))
        conn.commit()
        conn.close()

    def get_history(self, phone_number: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT carrier, location, owner, ported, change_type, change_date, confidence_score, investigation_id
            FROM phone_history WHERE phone_number = ? ORDER BY change_date ASC
        ''', (phone_number,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "carrier": row[0],
                "location": row[1],
                "owner": row[2],
                "ported": bool(row[3]),
                "change_type": row[4],
                "change_date": row[5],
                "confidence_score": row[6],
                "investigation_id": row[7]
            } for row in rows
        ]

    def detect_porting(self, phone_number: str) -> List[Dict[str, Any]]:
        history = self.get_history(phone_number)
        transitions = []
        prev_carrier = None
        for record in history:
            if prev_carrier and record["carrier"] != prev_carrier:
                transitions.append(record)
            prev_carrier = record["carrier"]
        return transitions

    def detect_ownership_change(self, phone_number: str) -> List[Dict[str, Any]]:
        history = self.get_history(phone_number)
        changes = []
        prev_owner = None
        for record in history:
            if prev_owner and record["owner"] != prev_owner:
                changes.append(record)
            prev_owner = record["owner"]
        return changes

    def score_change_confidence(self, record: Dict[str, Any]) -> float:
        # Placeholder: implement scoring logic based on available data
        return record.get("confidence_score", 0.5)

    def get_investigation_history(self, investigation_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT phone_number, carrier, location, owner, ported, change_type, change_date, confidence_score
            FROM phone_history WHERE investigation_id = ? ORDER BY change_date ASC
        ''', (investigation_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "phone_number": row[0],
                "carrier": row[1],
                "location": row[2],
                "owner": row[3],
                "ported": bool(row[4]),
                "change_type": row[5],
                "change_date": row[6],
                "confidence_score": row[7]
            } for row in rows
        ]
