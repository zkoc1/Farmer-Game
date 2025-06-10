import sqlite3
import json

class DatabaseFarmer:
    def __init__(self, db_path="farmer_game.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                city TEXT,
                level INTEGER,
                money INTEGER,
                money1 INTEGER,
                milk INTEGER,
                eggs INTEGER,
                fruits INTEGER,
                market_x INTEGER,
                market_y INTEGER,
                chicken_x INTEGER,
                chicken_y INTEGER,
                cow_x INTEGER,
                cow_y INTEGER,
                wheat_positions TEXT, -- JSON string of list of tuples
                inventory_data TEXT -- JSON string of dict
            )
        ''')
        self.conn.commit()

    def save_player(self, data):
        # JSON'a dönüştür: crops listesi ve inventory dict gibi karmaşık tipler için
        wheat_json = json.dumps(data.get("wheat_positions", []))
        inventory_json = json.dumps(data.get("inventory_data", {}))

        self.cursor.execute('''
            INSERT INTO players (
                username, city, level, money,money1,
                milk, eggs, fruits,
                market_x, market_y,
                chicken_x, chicken_y,
                cow_x, cow_y,
                wheat_positions,
                inventory_data
            ) VALUES (?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                city=excluded.city,
                level=excluded.level,
                money=excluded.money,
                money1=excluded.money1,
                milk=excluded.milk,
                eggs=excluded.eggs,
                fruits=excluded.fruits,
                market_x=excluded.market_x,
                market_y=excluded.market_y,
                chicken_x=excluded.chicken_x,
                chicken_y=excluded.chicken_y,
                cow_x=excluded.cow_x,
                cow_y=excluded.cow_y,
                wheat_positions=excluded.wheat_positions,
                inventory_data=excluded.inventory_data
        ''', (
            data["username"], data["city"], data["level"], data["money"],data["money1"],
            data["milk"], data["eggs"], data["fruits"],
            data["market_x"], data["market_y"],
            data["chicken_x"], data["chicken_y"],
            data["cow_x"], data["cow_y"],
            wheat_json,
            inventory_json
        ))
        self.conn.commit()

    def load_player(self, username):
        self.cursor.execute("SELECT * FROM players WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row:
            return {
                "username": row[0],
                "city": row[1],
                "level": row[2],
                "money": row[3],
                "money1":row[4],
                "milk": row[5],
                "eggs": row[6],
                "fruits": row[7],
                "market_pos": (row[8], row[9]),
                "chicken_pos": (row[10], row[11]),
                "cow_pos": (row[12], row[13]),
                "wheat_positions": json.loads(row[14]) if row[14] else [],
                "inventory_data": json.loads(row[15]) if row[15] else {}
            }
        else:
            return None

    def close(self):
        self.conn.close()
