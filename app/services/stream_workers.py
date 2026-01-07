# app/services/stream_workers.py
import asyncio
import logging

logger = logging.getLogger(__name__)

async def start_stream_workers():
    """
    Async background loop for synthetic stream workers.
    This function MUST be async and must never block.
    """
    logger.info("Stream workers started")

    while True:
        try:
            # Your periodic logic here
            # Example: refresh in-memory anomaly / optimizer data
            # await refresh_anomaly_cache()
            # await refresh_optimizer_cache()
            pass
        except Exception as exc:
            logger.exception("Stream worker error: %s", exc)

        # NEVER use time.sleep here
        await asyncio.sleep(10)
