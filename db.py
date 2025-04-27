import aiosqlite
from datetime import datetime

class Database:
    def __init__(self, path="appeals.db"):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS appeals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT,
                    status TEXT,
                    created_at TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appeal_id INTEGER,
                    sender TEXT,
                    text TEXT,
                    created_at TEXT
                )
            ''')
            await db.commit()

    async def create_appeal(self, user_id, text):
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "INSERT INTO appeals (user_id, text, status, created_at) VALUES (?, ?, 'active', ?)",
                (user_id, text, now)
            )
            appeal_id = cursor.lastrowid
            await db.execute(
                "INSERT INTO messages (appeal_id, sender, text, created_at) VALUES (?, 'user', ?, ?)",
                (appeal_id, text, now)
            )
            await db.commit()
            return appeal_id

    async def get_active_appeals(self, user_id):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT * FROM appeals WHERE user_id=? AND status='active'", (user_id,)
            )
            return await cursor.fetchall()

    async def get_closed_appeals(self, user_id):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT * FROM appeals WHERE user_id=? AND status='closed'", (user_id,)
            )
            return await cursor.fetchall()

    async def get_appeal(self, appeal_id):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT * FROM appeals WHERE id=?", (appeal_id,)
            )
            return await cursor.fetchone()

    async def close_appeal(self, appeal_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE appeals SET status='closed' WHERE id=?", (appeal_id,)
            )
            await db.commit()

    async def add_message(self, appeal_id, sender, text):
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO messages (appeal_id, sender, text, created_at) VALUES (?, ?, ?, ?)",
                (appeal_id, sender, text, now)
            )
            await db.commit()

    async def get_messages(self, appeal_id):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT * FROM messages WHERE appeal_id=? ORDER BY id", (appeal_id,)
            )
            return await cursor.fetchall()

    async def get_all_active_appeals(self):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT * FROM appeals WHERE status='active'"
            )
            return await cursor.fetchall()