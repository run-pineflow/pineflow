from abc import ABC, abstractmethod
from typing import Optional

from pineflow.core.observability.types import PayloadRecord
from pineflow.core.prompts import PromptTemplate


class BaseObservability(ABC):
    """An interface for observability."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseObservability"


class ModelObservability(BaseObservability):
    """An interface for model observability."""

    def __init__(self, prompt_template: Optional[PromptTemplate] = None) -> None:
        self.prompt_template = prompt_template

    @classmethod
    def class_name(cls) -> str:
        return "ModelObservability"

    @abstractmethod
    def __call__(self, payload: PayloadRecord) -> None:
        """ModelObservability."""


class TelemetryObservability(BaseObservability):
    """An interface for telemetry observability."""

    @classmethod
    def class_name(cls) -> str:
        return "TelemetryObservability"
