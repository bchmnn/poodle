import asyncio
import sys

from poodle import Poodle


async def main():
    async with Poodle("https://your.moodle.instance") as moodle:
        await moodle.authenticate()
    return None


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
