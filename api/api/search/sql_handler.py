


"""
Azure SQL Database Connector
-----------------------------
Provides a class-based interface for connecting to an Azure SQL Database,
querying by ID, and returning results as JSON for use by a UI.

Dependencies:
    pip install pyodbc python-dotenv

ODBC Driver:
    Requires 'ODBC Driver 18 for SQL Server' (or 17).
    Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
"""

import pyodbc
import json
import logging
import os
import dotenv
from typing import Any

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ===========================================================================
# CONNECTION CONFIGURATION  ← replace placeholders with your actual values
# ===========================================================================
server = os.environ["AZURE_SQL_SERVER"]
database = os.environ["AZURE_SQL_DATABASE"] 
username = os.environ["AZURE_SQL_USERNAME"]
password = os.environ["AZURE_SQL_PASSWORD"]
DB_CONFIG = {
    "server":   server,   
    "database": database, 
    "username": username, 
    "password": password, 
    "driver":   "ODBC Driver 18 for SQL Server",         # or "ODBC Driver 17 for SQL Server"
    # Optional extras — uncomment if needed:
    # "port":   "1433",
    # "encrypt": "yes",
    # "trust_server_certificate": "no",
    # "connection_timeout": "30",
}

# Table / column to query  ← replace with your actual table and column names
DEFAULT_TABLE    = "person_details"
DEFAULT_ID_FIELD = "PERSON_ID_LEGACY" 
# ===========================================================================

class AzureSQLConnector:
    """
    Manages a connection to an Azure SQL Database and exposes helper methods
    for ID-based querying with JSON-serialisable responses.
    """

    def __init__(self, config: dict = None):
        """
        Initialise the connector and open a database connection.

        Args:
            config: Optional dict that overrides the module-level DB_CONFIG.
        """
        self.config = config or DB_CONFIG
        self.connection: pyodbc.Connection | None = None
        self._connect()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_connection_string(self) -> str:
        cfg = self.config
        conn_str = (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['username']};"
            f"PWD={cfg['password']};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conn_str

    def _connect(self) -> None:
        """Open (or re-open) the database connection."""
        try:
            conn_str = self._build_connection_string()
            self.connection = pyodbc.connect(conn_str)
            logger.info("Connected to Azure SQL Database: %s", self.config["database"])
        except pyodbc.Error as e:
            logger.error("Failed to connect: %s", e)
            raise

    def _ensure_connection(self) -> None:
        """Reconnect automatically if the connection has been closed."""
        try:
            self.connection.cursor()          # lightweight liveness check
        except (pyodbc.Error, AttributeError):
            logger.warning("Connection lost — reconnecting…")
            self._connect()

    @staticmethod
    def _rows_to_json(cursor: pyodbc.Cursor) -> list[dict]:
        """Convert cursor rows to a list of dicts (JSON-serialisable)."""
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query_by_id(
        self,
        record_id: Any,
        table: str = DEFAULT_TABLE,
        id_field: str = DEFAULT_ID_FIELD,
    ) -> str:
        """
        Query all columns from *table* where *id_field* equals *record_id*.

        Args:
            record_id:  The ID value supplied by the UI (int, str, etc.).
            table:      Table name including schema, e.g. "dbo.Customers".
            id_field:   The name of the ID column, e.g. "CustomerID".

        Returns:
            A JSON string — either a list of matching row objects,
            or an error object: {"error": "<message>"}.

        Example:
            connector = AzureSQLConnector()
            json_str  = connector.query_by_id(42)
            data      = json.loads(json_str)
        """
        self._ensure_connection()

        # Parameterised query — protects against SQL injection
        sql = f"SELECT * FROM {table} WHERE {id_field} = ?"

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (record_id,))
            rows = self._rows_to_json(cursor)
            logger.info(
                "query_by_id(%s) on %s.%s → %d row(s)",
                record_id, table, id_field, len(rows),
            )
            return json.dumps(rows, default=str, indent=2)

        except pyodbc.Error as e:
            logger.error("Query error: %s", e)
            return json.dumps({"error": str(e)})

    def execute_query(self, sql: str, params: tuple = ()) -> str:
        """
        Run an arbitrary SELECT statement and return results as JSON.

        Useful for custom queries beyond simple ID lookups.

        Args:
            sql:    A parameterised SQL string, e.g.
                    "SELECT * FROM dbo.Orders WHERE Status = ? AND Amount > ?"
            params: A tuple of values to bind, e.g. ("shipped", 100).

        Returns:
            JSON string (list of row objects) or {"error": "<message>"}.
        """
        self._ensure_connection()

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            rows = self._rows_to_json(cursor)
            logger.info("execute_query → %d row(s)", len(rows))
            return json.dumps(rows, default=str, indent=2)

        except pyodbc.Error as e:
            logger.error("Query error: %s", e)
            return json.dumps({"error": str(e)})
    
    def execute_insert(self, sql: str, params: tuple = ()) -> str:
        """
        Run an arbitrary INSERT statement and return results as JSON.

        Useful for custom queries beyond simple ID lookups.

        Args:
            sql:    A parameterised SQL string, e.g.
                    "INSERT INTO dbo.Orders (Status, Amount) VALUES (?, ?)"
            params: A tuple of values to bind, e.g. ("shipped", 100).

        Returns:
            JSON string (list of row objects) or {"error": "<message>"}.
        """
        self._ensure_connection()

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            logger.info("execute_insert → %d row(s) affected", cursor.rowcount)
            return json.dumps({"rows_affected": cursor.rowcount}, default=str, indent=2)

        except pyodbc.Error as e:
            logger.error("Query error: %s", e)
            return json.dumps({"error": str(e)})

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed.")

    # Support use as a context manager: `with AzureSQLConnector() as db:`
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False   # do not suppress exceptions


# ===========================================================================
# Example usage (runs only when the script is executed directly)
# ===========================================================================
# if __name__ == "__main__":

#     # --- Basic usage -------------------------------------------------------
#     with AzureSQLConnector() as db:

#         # Query a single record by ID (e.g. value passed in from a UI)
#         record_id_from_ui = 1
#         result = db.query_by_id(record_id_from_ui)
#         print("query_by_id result:")
#         print(result)

#         # Custom query example
#         custom_result = db.execute_query(
#             f"SELECT TOP 10 * FROM {DEFAULT_TABLE} ORDER BY {DEFAULT_ID_FIELD} DESC"
#         )
#         print("\nTop-10 records:")
#         print(custom_result)