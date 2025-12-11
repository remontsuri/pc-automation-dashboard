"""PC Automation Dashboard - FastAPI Backend

Real-time process monitoring and automation system for Windows
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psutil
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PC Automation Dashboard",
    description="Windows PC Activity Automation Dashboard API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== DATA MODELS ====
class ProcessInfo:
    """Process information model"""
    def __init__(self, pid: int):
        try:
            self.process = psutil.Process(pid)
            self.pid = pid
            self.name = self.process.name()
            self.status = self.process.status()
            self.cpu_percent = self.process.cpu_percent(interval=0.1)
            self.memory_info = self.process.memory_info()
            self.create_time = datetime.fromtimestamp(self.process.create_time()).isoformat()
        except psutil.NoSuchProcess:
            self.pid = pid
            self.name = "Unknown"
            self.status = "terminated"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "status": self.status,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_info.rss / 1024 / 1024 if hasattr(self, 'memory_info') else 0,
            "create_time": self.create_time
        }

# ==== API ENDPOINTS ====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "PC Automation Dashboard",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/processes")
async def get_processes() -> Dict[str, Any]:
    """Get list of all running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                processes.append(ProcessInfo(proc.info['pid']).to_dict())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "count": len(processes),
            "processes": processes[:100],  # Limit to 100 for performance
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching processes: {e}")
        return {"error": str(e)}

@app.get("/api/system/status")
async def get_system_status() -> Dict[str, Any]:
    """Get system status and resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0
            },
            "memory": {
                "total_gb": memory.total / 1024**3,
                "available_gb": memory.available / 1024**3,
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / 1024**3,
                "free_gb": disk.free / 1024**3,
                "percent": disk.percent
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {"error": str(e)}

@app.post("/api/processes/{pid}/kill")
async def kill_process(pid: int):
    """Terminate a process by PID"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        return {"status": "killed", "pid": pid}
    except psutil.NoSuchProcess:
        return JSONResponse(status_code=404, content={"error": "Process not found"})
    except Exception as e:
        logger.error(f"Error killing process: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/processes/{pid}/suspend")
async def suspend_process(pid: int):
    """Suspend a process by PID"""
    try:
        process = psutil.Process(pid)
        process.suspend()
        return {"status": "suspended", "pid": pid}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/processes/{pid}/resume")
async def resume_process(pid: int):
    """Resume a suspended process by PID"""
    try:
        process = psutil.Process(pid)
        process.resume()
        return {"status": "resumed", "pid": pid}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ==== WEBSOCKET ====

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send system status every second
            status = await get_system_status()
            await websocket.send_json({
                "type": "system_update",
                "data": status
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
