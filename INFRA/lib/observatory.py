import time
import functools
import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class StepMetric:
    name: str
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsTracker:
    """
    Monitor central de performance e telemetria do Ecossistema GARE.
    """
    def __init__(self, log_path: Optional[str] = None):
        self.steps: List[StepMetric] = []
        self.start_time = None
        self.total_duration = 0
        
        # Detectar raiz do projeto GARE
        if log_path:
            self.log_path = log_path
        else:
            # Encontra a raiz baseando-se na localização deste arquivo (INFRA/lib/observatory.py)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.log_path = os.path.join(base_dir, "INFRA", "logs", "rag_metrics.json")
        
        # Garantir diretório de logs
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def start(self):
        self.steps = []
        self.start_time = time.perf_counter()

    def add_step(self, name: str, duration: float, **metadata):
        self.steps.append(StepMetric(name=name, duration=duration, metadata=metadata))

    def stop(self):
        if self.start_time:
            self.total_duration = time.perf_counter() - self.start_time
            self._persist()

    def _persist(self):
        """Salva as métricas em arquivo persistente."""
        report = self.get_report()
        report["timestamp"] = datetime.now().isoformat()
        
        try:
            # Carregar logs existentes
            logs = []
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r') as f:
                    content = f.read()
                    if content:
                        logs = json.loads(content)
            
            # Adicionar novo log
            logs.append(report)
            
            # Salvar de volta
            with open(self.log_path, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar métricas: {e}")

    def get_report(self) -> Dict[str, Any]:
        return {
            "total_latency_sec": round(self.total_duration, 3),
            "breakdown": [
                {"step": s.name, "duration_ms": round(s.duration * 1000, 2), "meta": s.metadata}
                for s in self.steps
            ]
        }

def track_step(step_name: str):
    """
    Decorator para medir o tempo de um passo específico do RAG.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Procura por um tracker nos argumentos (geralmente passado via self ou context)
            tracker = None
            if args and hasattr(args[0], 'tracker'):
                tracker = args[0].tracker
            
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            
            if tracker:
                tracker.add_step(step_name, duration)
            
            return result
        return wrapper
    return decorator
