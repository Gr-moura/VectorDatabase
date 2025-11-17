# src/infrastructure/config.py

import os
from dotenv import load_dotenv

# This function will search for a .env file in the project root
# and load its variables into the environment.
load_dotenv()

# We can now access the variables using os.getenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if COHERE_API_KEY is None:
    print(
        "Warning: COHERE_API_KEY environment variable not found. Real embeddings client will fail."
    )
