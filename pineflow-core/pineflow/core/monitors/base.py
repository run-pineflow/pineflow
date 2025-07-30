from abc import ABC, abstractmethod
from typing import Optional

from pineflow.core.monitors.types import PayloadRecord
from pineflow.core.prompts import PromptTemplate


class BaseMonitor(ABC):
    """An interface for observability."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseMonitor"


class ModelMonitor(BaseMonitor):
    """An interface for model observability."""

    def __init__(self, prompt_template: Optional[PromptTemplate] = None) -> None:
        self.prompt_template = prompt_template

    @classmethod
    def class_name(cls) -> str:
        return "ModelMonitor"

    @abstractmethod
    def __call__(self, payload: PayloadRecord) -> None:
        """ModelMonitor."""


class TelemetryMonitor(BaseMonitor):
    """An interface for telemetry observability."""

    @classmethod
    def class_name(cls) -> str:
        return "TelemetryMonitor"
