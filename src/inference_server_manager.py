import os
import time
import subprocess
import requests

from config import (
    LLAMA_SERVER_BIN,
    NEMOTRON_MODEL,
    LLAMA_SERVER_HOST,
    LLAMA_SERVER_PORT,
    LLAMA_CTX_SIZE,
    LLAMA_N_GPU_LAYERS,
    LLAMA_THREADS,
    LLAMA_BATCH,
)

class LlamaServerManager:
    def __init__(self):
        self.proc = None
        self.base_url = f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}"

    def is_healthy(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            return resp.ok
        except Exception:
            return False

    def start(self, wait_seconds: int = 60) -> None:
        if self.is_healthy():
            return

        if not LLAMA_SERVER_BIN:
            raise RuntimeError("LLAMA_SERVER_BIN is not set")
        if not NEMOTRON_MODEL:
            raise RuntimeError("NEMOTRON_MODEL is not set")

        cmd = [
            LLAMA_SERVER_BIN,
            "-m", NEMOTRON_MODEL,
            "--host", LLAMA_SERVER_HOST,
            "--port", str(LLAMA_SERVER_PORT),
            "-c", str(LLAMA_CTX_SIZE),
            "-ngl", str(LLAMA_N_GPU_LAYERS),
            "-t", str(LLAMA_THREADS),
            "-b", str(LLAMA_BATCH),
        ]

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        start_time = time.time()
        while time.time() - start_time < wait_seconds:
            if self.is_healthy():
                return
            time.sleep(1)

        raise RuntimeError("llama-server did not become healthy in time")

    def stop(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            self.proc.wait(timeout=10)
            self.proc = None