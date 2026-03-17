import os
from dotenv import load_dotenv

load_dotenv()

LLAMA_SERVER_BIN = os.getenv("LLAMA_SERVER_BIN")
NEMOTRON_MODEL = os.getenv("NEMOTRON_MODEL")

LLAMA_SERVER_HOST = os.getenv("LLAMA_SERVER_HOST", "127.0.0.1")
LLAMA_SERVER_PORT = int(os.getenv("LLAMA_SERVER_PORT", "8080"))

LLAMA_CTX_SIZE = int(os.getenv("LLAMA_CTX_SIZE", "4096"))
LLAMA_N_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "999"))
LLAMA_THREADS = int(os.getenv("LLAMA_THREADS", "8"))
LLAMA_BATCH = int(os.getenv("LLAMA_BATCH", "512"))

AUTO_START_MODEL_SERVER = os.getenv("AUTO_START_MODEL_SERVER", "false").lower() == "true"

LLAMA_BASE_URL = f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}"