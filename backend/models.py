from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProcessRecord(BaseModel):
    pid: int
    name: str
    memory_mb: float
    cpu_percent: float
    timestamp: datetime
    status: str  # running, terminated, error

class SystemMetric(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int

class ProcessAlert(BaseModel):
    id: str
    process_name: str
    alert_type: str  # high_memory, high_cpu, crashed
    threshold: float
    current_value: float
    timestamp: datetime
    severity: str  # low, medium, high

class SystemStatus(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    uptime_seconds: float
