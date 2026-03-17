"""Helpers for managing a local llama-server process."""

from __future__ import annotations

import subprocess
import time

import requests

from config import (
    LLAMA_BASE_URL,
    LLAMA_BATCH,
    LLAMA_CTX_SIZE,
    LLAMA_N_GPU_LAYERS,
    LLAMA_SERVER_BIN,
    LLAMA_SERVER_HOST,
    LLAMA_SERVER_PORT,
    LLAMA_THREADS,
    NEMOTRON_MODEL,
)


class LlamaServerManager:
    """Start and stop a local llama-server process when needed."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None

    def is_healthy(self) -> bool:
        """Return True when the llama-server health endpoint is reachable."""
        try:
            response = requests.get(f"{LLAMA_BASE_URL}/health", timeout=2)
            return response.ok
        except requests.RequestException:
            return False

    def start(self, wait_seconds: int = 60) -> None:
        """Start llama-server and wait for /health before returning."""
        if self.is_healthy():
            return

        if not LLAMA_SERVER_BIN:
            raise RuntimeError("LLAMA_SERVER_BIN is not set")
        if not NEMOTRON_MODEL:
            raise RuntimeError("NEMOTRON_MODEL is not set")

        command = [
            LLAMA_SERVER_BIN,
            "-m",
            NEMOTRON_MODEL,
            "--host",
            LLAMA_SERVER_HOST,
            "--port",
            str(LLAMA_SERVER_PORT),
            "-c",
            str(LLAMA_CTX_SIZE),
            "-ngl",
            str(LLAMA_N_GPU_LAYERS),
            "-t",
            str(LLAMA_THREADS),
            "-b",
            str(LLAMA_BATCH),
        ]

        self._process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if self.is_healthy():
                return
            if self._process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited early with code {self._process.returncode}"
                )
            time.sleep(1)

        self.stop()
        raise RuntimeError("llama-server did not become healthy in time")

    def stop(self) -> None:
        """Stop the llama-server process started by this manager."""
        if self._process is None:
            return

        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=5)

        self._process = None
