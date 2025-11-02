
import asyncio

loop: asyncio.AbstractEventLoop | None = None

async def setupQLoop():
    global loop
    if loop:
        return
    loop = asyncio.get_event_loop()
