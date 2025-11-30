# src/infrastructure/config.py

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Fail Fast: Prevent the app from starting without critical config
if not COHERE_API_KEY:
    raise ValueError("FATAL: COHERE_API_KEY environment variable is not set.")
