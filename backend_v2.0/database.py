import os
from dotenv import load_dotenv
import aiomysql

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "restaurant_db")

_pool = None

async def _get_pool():
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            autocommit=True,
            minsize=1,
            maxsize=10
        )
    return _pool

async def fetch_menu(branch: int):
    pool = await _get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT name, category, portion, price FROM menu WHERE branch=%s",
                (branch,)
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def fetch_recent_orders(branch: int, days: int = 30):
    pool = await _get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT item_name, COUNT(*) as cnt FROM orders WHERE branch=%s AND order_date >= NOW() - INTERVAL %s DAY GROUP BY item_name",
                (branch, days)
            )
            rows = await cur.fetchall()
            return {row[0]: int(row[1]) for row in rows}
