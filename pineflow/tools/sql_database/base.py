from typing import Type

from pydantic.v1 import BaseModel, Field

from pineflow.core.tools.base import BaseTool
from pineflow.core.utilities.sql_database import SQLAlchemyDatabase


class _SQLQueryToolInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute.")
    
class SQLQueryTool(BaseTool):
    db: SQLAlchemyDatabase
    name: str = "sql_query_tool"
    description: str = "Execute a SQL query against the data and get back the result."
    
    input_schema: Type[BaseModel] = _SQLQueryToolInput
    
    def _run(self, query):
        """Execute the SQL query."""
        return self.db.execute(query)