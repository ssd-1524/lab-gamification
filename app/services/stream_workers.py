from __future__ import annotations

import asyncio
import random
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

ANOMALY_BUFFER: list[dict] = []
OPTIMIZER_BUFFER: list[dict] = []

MAX_ANOMALY_LEN = 60
MAX_OPTIMIZER_LEN = 24

anomaly_task: asyncio.Task | None = None
optimizer_task: asyncio.Task | None = None


async def anomaly_worker() -> None:
    base = random.randint(45, 55)

    while True:
        value = base + random.randint(-4, 5)
        if random.random() < 0.05:
            value += random.randint(25, 45)

        ANOMALY_BUFFER.append({
            "ts": datetime.now(IST).isoformat(),
            "value": value,
        })

        if len(ANOMALY_BUFFER) > MAX_ANOMALY_LEN:
            ANOMALY_BUFFER.pop(0)

        await asyncio.sleep(10)


async def optimizer_worker() -> None:
    while True:
        OPTIMIZER_BUFFER.append({
            "ts": datetime.now(IST).isoformat(),
            "efficiency": random.randint(65, 95),
            "cost": random.randint(700, 1200),
            "throughput": random.randint(18, 38),
        })

        if len(OPTIMIZER_BUFFER) > MAX_OPTIMIZER_LEN:
            OPTIMIZER_BUFFER.pop(0)

        await asyncio.sleep(3600)


def start_stream_workers() -> None:
    global anomaly_task, optimizer_task

    if anomaly_task is None or anomaly_task.done():
        anomaly_task = asyncio.create_task(anomaly_worker(), name="anomaly_worker")

    if optimizer_task is None or optimizer_task.done():
        optimizer_task = asyncio.create_task(optimizer_worker(), name="optimizer_worker")
