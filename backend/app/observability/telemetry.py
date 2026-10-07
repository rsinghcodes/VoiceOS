"""
Observability and Telemetry setup per VoiceOS BRAIN §50 & §51.
Provides structured logging, OpenTelemetry tracing spans, and performance metrics timers.
"""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger("voiceos.observability")


class TelemetryTracker:
    """
    Lightweight telemetry & latency tracer for voice and agent workflows.
    Records stage latencies (STT, Intent, LLM, Tools, TTS, DB) for OpenTelemetry and CloudWatch.
    """

    def __init__(self, trace_id: Optional[str] = None):
        import uuid
        self.trace_id = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        self.stages: Dict[str, float] = {}
        self.metadata: Dict[str, Any] = {}

    @contextmanager
    def measure(self, stage_name: str):
        """Context manager to measure latency of a single processing stage in milliseconds."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.stages[stage_name] = round(elapsed_ms, 2)

    def record_metric(self, name: str, value: Any):
        """Record arbitrary metric or attribute."""
        self.metadata[name] = value

    def to_dict(self) -> Dict[str, Any]:
        """Export structured telemetry payload."""
        total_latency_ms = round(sum(self.stages.values()), 2)
        return {
            "trace_id": self.trace_id,
            "total_latency_ms": total_latency_ms,
            "stages": self.stages,
            "metadata": self.metadata,
        }
