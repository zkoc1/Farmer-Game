import sqlite3
import json

class DatabaseFarmer:
    def __init__(self, db_name="farm_game.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                money INTEGER,
                level INTEGER,
                inventory TEXT
            )
        """)
        self.conn.commit()

    def save_player(self, username, money, level, inventory):
        inventory_json = json.dumps(inventory)
        self.cursor.execute("""
            INSERT INTO players (username, money, level, inventory)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                money=excluded.money,
                level=excluded.level,
                inventory=excluded.inventory
        """, (username, money, level, inventory_json))
        self.conn.commit()

    def load_player(self, username):
        self.cursor.execute("SELECT money, level, inventory FROM players WHERE username=?", (username,))
        result = self.cursor.fetchone()
        if result:
            money, level, inventory_json = result
            inventory = json.loads(inventory_json)
            return money, level, inventory
        else:
            # Kullanıcı yoksa varsayılan değerler
            return 0, 0, {}

    def close(self):
        self.conn.close()