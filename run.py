import subprocess
import time
import socket
import sys

def wait_for_port(port, host='127.0.0.1', timeout=300, process=None):
    """Wait until a port starts accepting TCP connections."""
    start_time = time.time()
    while True:
        if process is not None and process.poll() is not None:
            print("\n❌ Backend process crashed before binding to port.")
            return False
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(1)
            if time.time() - start_time > timeout:
                return False

print("Starting backend on port 8000...")
backend = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])

print("Waiting for backend to be ready...")
if not wait_for_port(8000, process=backend):
    print("Error: Backend failed to start or timed out.")
    backend.terminate()
    exit(1)

print("Starting frontend on port 7860...")
frontend = subprocess.Popen([
    "streamlit", "run", "frontend.py",
    "--server.port", "7860",
    "--server.address", "0.0.0.0"
])

try:
    while True:
        if backend.poll() is not None:
            print("Backend stopped unexpectedly.")
            break
        if frontend.poll() is not None:
            print("Frontend stopped unexpectedly.")
            break
        time.sleep(5)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    backend.terminate()
    frontend.terminate()
    sys.exit(0)