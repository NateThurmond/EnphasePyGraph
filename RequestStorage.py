import sqlite3
from threading import Lock
import time

class RequestStorage:
    def __init__(self, db_path="py_enphase_db.sqlite", reqPullLimit=96, runMode="cumulative"):
        self.reqPullLimit = reqPullLimit
        self.runMode = runMode
        self.db_path = db_path
        self.lock = Lock()

        # Connect to the SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()
        self.prune_old_data()

    def _create_table(self):
        with self.lock:
            """Create a table to store prev requests if it doesn't already exist."""
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS apiReqWattage (
                    id INTEGER PRIMARY KEY,
                    reqEpoch INTEGER,
                    prod_cumu_currW INTEGER,
                    net_cumu_currW INTEGER,
                    total_cumu_currW INTEGER,
                    prod_cumu_whDlvd INTEGER,
                    net_cumu_whDlvd INTEGER,
                    total_cumu_whDlvd INTEGER,
                    prod_cumu_whRcvd INTEGER,
                    net_cumu_whRcvd INTEGER,
                    total_cumu_whRcvd INTEGER
                )
            """)
            self.conn.commit()

    def get_saved_req(self):
        with self.lock:
            """Retrieve the saved api req data and time from the database."""

            # Limit API fetched data to the last 3 days
            current_time = int(time.time())
            time_72_hours_ago = current_time - (72 * 60 * 60)

            # whDlvdCum used for cumulative/average mode and currW for current mode
            powerAttrKeys = "prod_cumu_whDlvd, net_cumu_whDlvd, total_cumu_whDlvd"
            if self.runMode == "current":
                powerAttrKeys = "prod_cumu_currW, net_cumu_currW, total_cumu_currW"

            # Retrieve historical API data
            self.cursor.execute(
                f"SELECT reqEpoch, {powerAttrKeys} "
                + "FROM apiReqWattage WHERE reqEpoch >= ? ORDER BY reqEpoch DESC LIMIT ?",
                (time_72_hours_ago, self.reqPullLimit,)
            )
            result = self.cursor.fetchall()
            if result:
                return self._transform_saved_data(result)
            else: return {}

    def save_req(self, epoch, prod, net, total):
        with self.lock:
            try:
                """Save the new api request data and time in the database."""
                self.cursor.execute("REPLACE INTO apiReqWattage "
                    + "(reqEpoch, prod_cumu_currW, net_cumu_currW, total_cumu_currW, "
                    + "prod_cumu_whDlvd, net_cumu_whDlvd, total_cumu_whDlvd, "
                    + "prod_cumu_whRcvd, net_cumu_whRcvd, total_cumu_whRcvd) "
                    + "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        epoch, prod['currW'], net['currW'], total['currW'],
                        prod['whDlvdCum'], net['whDlvdCum'], total['whDlvdCum'],
                        prod['whRcvdCum'], net['whRcvdCum'], total['whRcvdCum']
                    )
                )
                self.conn.commit()
            except sqlite3.OperationalError as e:
                print(f"Database error: {e}. Reconnecting...")
                self._reconnect()

    def _transform_saved_data(self, rows):
        # print(json.dumps(rows))
        return {row[0]: [row[1], row[2], row[3]] for row in rows}

    def prune_old_data(self, max_records=10000):
        """Remove old data beyond the specified limit."""
        with self.lock:
            self.cursor.execute("""
                DELETE FROM apiReqWattage
                WHERE id NOT IN (
                    SELECT id FROM apiReqWattage ORDER BY reqEpoch DESC LIMIT ?
                )
            """, (max_records,))
            self.conn.commit()

    def close(self):
        """Close the database connection."""
        with self.lock:
            self.conn.close()

    def _reconnect(self):
        """Reconnect to the database in case of connection issues."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        """Ensure the database connection is open."""
        if not self.conn or not self.cursor:
            self._reconnect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self.conn = None
        self.cursor = None