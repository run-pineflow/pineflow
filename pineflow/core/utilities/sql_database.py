from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


class SQLAlchemyDatabase:
    """
    A unified database class that wraps a SQLAlchemy Engine instance,
    allowing for execution of SQL queries across any supported SQL dialect.
    """
    
    def __init__(self, engine: Engine) -> None:
        if not isinstance(engine, Engine):
            raise TypeError("Expected a SQLAlchemy Engine instance.")
        self._engine = engine

    def _execute(
        self, 
        query: str):
        """Executes SQL query with SQLAlchemy."""
        with self._engine.connect() as conn:
            cursor = conn.execute(text(query))
                
            if cursor.returns_rows:
                return [x._asdict() for x in cursor.fetchall()]
                
        return []

    # def _execute_driver_sql(self, sql_query: str, params: tuple = None):
    #     """Execute raw SQL directly via the DBAPI driver."""
    #     try:
    #         with self.engine.connect() as conn:
    #             result = conn.exec_driver_sql(sql, params or ())
    #             if result.returns_rows:
    #                 return result.fetchall()
    #             return result.rowcount
    #     except SQLAlchemyError as e:
    #         print(f"SQLAlchemy error in exec_driver_sql(): {e}")
    #         return None
    
    def execute(
        self, 
        query: str, 
        include_columns: bool = True,
        no_throw: bool = True):
        """Execute a SQL query and return a string representing the results."""
        try:
            query_result = self._execute(query)
            
            result = [
                {
                    column: value
                    for column, value in r.items()
                }
                for r in query_result
                ]
            
            if not include_columns:
                result = [tuple(row.values()) for row in result]
            
            if not result:
                return ""
            else:
                return str(result)
  
        except SQLAlchemyError as e:
            if no_throw:
                return f"Error executing SQL query: {e}"
            
            raise SQLAlchemyError(f"Error executing SQL query: {e}")

    # def get_all_tables(self, schema: str = None, view_support: bool = False):
    #     """
    #     Return a list of all tables, including views if `view_support=True`.
    #     Filters out any table/view names that are not actually present in the database.
    #     """
    #     try:
    #         inspector = inspect(self.engine)
    #         tables = set(inspector.get_table_names(schema=schema))
    #         if view_support:
    #             views = set(inspector.get_view_names(schema=schema))
    #             tables.update(views)
    #         return sorted(tables)
    #     except SQLAlchemyError as e:
    #         print(f"SQLAlchemy error in get_all_tables(): {e}")
    #         return []
