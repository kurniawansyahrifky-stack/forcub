from database import premium_db
import asyncio

async def main():

    await premium_db.create_index(
        "user_id"
    )

asyncio.run(main())
