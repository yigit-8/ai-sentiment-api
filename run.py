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

# 1. Start the Backend (FastAPI) in the background
print("🚀 Starting AI Backend (FastAPI) on internal port 8000...")
backend = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])

# 2. Wait for the API to be ready
print("⏳ Waiting for backend to be ready...")
if not wait_for_port(8000, process=backend):
    print("❌ Error: Backend failed to start or timed out.")
    backend.terminate()
    exit(1)

# 3. Start the Frontend (Streamlit) in the background
print("🎨 Starting Web Frontend (Streamlit) on public port 7860...")
frontend = subprocess.Popen([
    "streamlit", "run", "frontend.py", 
    "--server.port", "7860", 
    "--server.address", "0.0.0.0"
])

# 4. Monitor both processes to keep the container alive
try:
    while True:
        if backend.poll() is not None:
            print("\n⚠️ Backend service stopped unexpectedly.")
            break
        if frontend.poll() is not None:
            print("\n⚠️ Frontend service stopped unexpectedly.")
            break
        time.sleep(5)
except KeyboardInterrupt:
    print("\n🛑 Shutting down services...")
finally:
    # Clean up processes on exit
    backend.terminate()
    frontend.terminate()
    sys.exit(0)