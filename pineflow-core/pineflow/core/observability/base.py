from abc import ABC, abstractmethod
from typing import Dict


class BaseObservability(ABC):
    """An interface for observability."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseObservability"


class ModelObservability(BaseObservability):
    """An interface for model observability."""

    @classmethod
    def class_name(cls) -> str:
        return "ModelObservability"
    
    @abstractmethod
    def __call__(self, payload: Dict) -> None:
        ...

    
class TelemetryObservability(BaseObservability):
    """An interface for telemetry observability."""

    @classmethod
    def class_name(cls) -> str:
        return "TelemetryObservability"