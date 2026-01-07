from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

ANOMALY_STATE = {}  # user_id -> {"start": datetime, "active": bool}

ANOMALY_INTERVAL = timedelta(seconds=60)
ANOMALY_DURATION = timedelta(seconds=15)


def get_anomaly_state(user_id: str):
    now = datetime.now(IST)

    state = ANOMALY_STATE.get(user_id)

    if not state:
        ANOMALY_STATE[user_id] = {"last": now, "start": None, "active": False}
        return False, None

    # trigger new anomaly
    if not state["active"] and now - state["last"] >= ANOMALY_INTERVAL:
        state["active"] = True
        state["start"] = now
        state["last"] = now

    # stop anomaly after duration
    if state["active"] and now - state["start"] >= ANOMALY_DURATION:
        state["active"] = False
        state["start"] = None

    return state["active"], state["start"]
