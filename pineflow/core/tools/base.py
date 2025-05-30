import re
from abc import ABC, abstractmethod
from typing import Annotated, Any, Dict

from pydantic import SkipValidation
from pydantic.v1 import BaseModel, Field, validator


class BaseTool(ABC, BaseModel):
    """Interface that Pineflow tools must implement."""
    
    name: str
    description: str
    input_schema: Annotated[Dict[str, Any], SkipValidation()] = Field(
        default=None, description="The tool input schema."
    )
     
    @validator("name")
    def _validate_name(cls, v):
        if not re.match(r"^[A-Za-z0-9_]+$", v):
            raise ValueError("Invalid name: only letters, digits, and underscores are allowed. No spaces or special characters.")
        return v

    @classmethod
    def class_name(cls) -> str:
        return "BaseTool"
    
    @abstractmethod
    def _run(
        self, 
        *args: Any, 
        **kwargs: Any) -> Any:
        """Implementation of the tool."""

    def run(self, tool_input: dict[str, Any]) -> Any:
        """Run the tool."""
        return self._run(**tool_input)
         
    def get_input_schema(self) -> Dict:
        """The tool input schema."""
        if self.input_schema is not None:
            return self.input_schema.schema["properties"]
        else:
            return None