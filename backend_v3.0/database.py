import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def get_pool():
    return await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DB"),
        autocommit=True
    )

async def fetch_menu(branch):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM menu WHERE branch=%s", (branch,))
            return await cur.fetchall()

async def fetch_recent_orders(branch):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT item_name, COUNT(*) as cnt FROM orders WHERE branch=%s GROUP BY item_name", (branch,))
            rows = await cur.fetchall()
            return {row["item_name"]: row["cnt"] for row in rows}
