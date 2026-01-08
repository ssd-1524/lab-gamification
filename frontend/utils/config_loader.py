import toml
import streamlit as st
from pathlib import Path


def load_config():
    # 1️⃣ Production (Streamlit Cloud secrets)
    try:
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            return st.secrets
    except Exception:
        pass

    # 2️⃣ Local dev (config.toml)
    config_path = Path("config.toml")
    if config_path.exists():
        return toml.load(config_path)

    # 3️⃣ No config anywhere = misconfigured system
    raise RuntimeError("No config found. Add secrets in Streamlit Cloud or create config.toml locally.")
