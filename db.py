import aiosqlite

DB_NAME = 'mailings.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS mailings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                interval REAL,
                channel_id INTEGER,
                enabled INTEGER DEFAULT 1,
                last_sent REAL DEFAULT 0
            )
        ''')
        await db.commit()

async def add_mailing(text, interval, channel_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO mailings (text, interval, channel_id) VALUES (?, ?, ?)',
            (text, interval, channel_id)
        )
        await db.commit()

async def get_mailings():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM mailings') as cursor:
            return await cursor.fetchall()

async def get_mailing(mailing_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM mailings WHERE id=?', (mailing_id,)) as cursor:
            return await cursor.fetchone()

async def update_mailing(mailing_id, text=None, interval=None, enabled=None):
    async with aiosqlite.connect(DB_NAME) as db:
        if text is not None:
            await db.execute('UPDATE mailings SET text=? WHERE id=?', (text, mailing_id))
        if interval is not None:
            await db.execute('UPDATE mailings SET interval=? WHERE id=?', (interval, mailing_id))
        if enabled is not None:
            await db.execute('UPDATE mailings SET enabled=? WHERE id=?', (enabled, mailing_id))
        await db.commit()

async def delete_mailing(mailing_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM mailings WHERE id=?', (mailing_id,))
        await db.commit()

async def update_last_sent(mailing_id, timestamp):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE mailings SET last_sent=? WHERE id=?', (timestamp, mailing_id))
        await db.commit()