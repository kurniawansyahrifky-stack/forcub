from database import anonymous_db, request_db
import asyncio

async def main():

    await anonymous_db.create_index(
        "owner"
    )

    await anonymous_db.create_index(
        "partner"
    )

    await request_db.create_index(
        "owner"
    )

asyncio.run(main())
