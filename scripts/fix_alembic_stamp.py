"""One-shot script to create platform.alembic_version and stamp at 0005."""
import asyncio
import asyncpg

DB_URL = "postgresql://postgres:SecretPassword123@localhost:5434/agridecision_user"
TARGET_REV = "0005"


async def fix():
    conn = await asyncpg.connect(DB_URL)

    # Ensure the alembic_version table exists in the platform schema
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS platform.alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        )
        """
    )
    print("Table platform.alembic_version ensured.")

    existing = await conn.fetch("SELECT version_num FROM platform.alembic_version")
    if not existing:
        await conn.execute(
            "INSERT INTO platform.alembic_version (version_num) VALUES ($1)",
            TARGET_REV,
        )
        print(f"Stamped at revision {TARGET_REV}.")
    else:
        print("Already stamped at:", [r["version_num"] for r in existing])

    ver = await conn.fetch("SELECT version_num FROM platform.alembic_version")
    print("Current Alembic version:", [r["version_num"] for r in ver])
    await conn.close()


asyncio.run(fix())
