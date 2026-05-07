from database import premium_db
import asyncio

async def reset_limits():

    while True:

        await premium_db.update_many(

            {
                "tier": "lite"
            },

            {
                "$set": {
                    "limit": 5
                }
            }

        )

        await premium_db.update_many(

            {
                "tier": "basic"
            },

            {
                "$set": {
                    "limit": 15
                }
            }

        )

        print("DAILY RESET DONE")

        await asyncio.sleep(86400)
