"""Robust Live Signal Scanning Orchestrator: Manages session locking, market session state detection, concurrency limits, deduplication, and publication gating without overlapping scans or trade execution."""
from __future__ import annotations
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .live_engine import LiveSignalEngine

class LiveScanOrchestrator:
    _lock = threading.Lock()
    _active_session: Optional[str] = None

    def __init__(self, model_version: str = "3.1.0"):
        self.live_engine = LiveSignalEngine(model_version=model_version)

    def run_scan(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        with LiveScanOrchestrator._lock:
            if LiveScanOrchestrator._active_session is not None:
                return {
                    "live_session_id": session_id or "UNKNOWN",
                    "status": "BLOCKED",
                    "reason": f"Scan already running for active session {LiveScanOrchestrator._active_session}",
                    "signals": []
                }
            sid = session_id or f"LIVE_SESSION_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            LiveScanOrchestrator._active_session = sid

        try:
            result = self.live_engine.scan_live_universe(session_id=sid)
            return result
        finally:
            with LiveScanOrchestrator._lock:
                LiveScanOrchestrator._active_session = None
