import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Literal

from pydantic.v1 import BaseModel, validator


class ToolInputSchema(BaseModel):
    """Tool input schema."""
    
    description: str
    input_type: Literal["integer", "string"]
    
    def to_dict(self) -> Dict[str, Any]:     
        self.dict()

class BaseTool(ABC, BaseModel):
    """Interface that Pineflow tools must implement."""
    
    name: str
    description: str
    input_schema: Dict[str, ToolInputSchema]
     
    @validator("name")
    def _validate_name(cls, v):
        if not re.match(r"^[A-Za-z0-9_]+$", v):
            raise ValueError("Invalid name: only letters, digits, and underscores are allowed. No spaces or special characters.")
        return v

    @classmethod
    def class_name(cls) -> str:
        return "BaseTool"
    
    @abstractmethod
    def run(self, tool_input) -> Any:
        """Run the tool."""