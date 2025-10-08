# =============================================================================
# SQLDriver.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   SQL Server connection driver for Python. Handles connection and query
#   execution using environment variables for credentials.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

from os import getenv
from dotenv import load_dotenv
from pymssql import connect, Cursor

class SQLConnection:
    def __init__(self) -> Cursor:
        load_dotenv()
        conn = connect(getenv("SQL_SERVER"),getenv("SQL_USER"),getenv("SQL_PASSWORD"),getenv("SQL_DATABASE"))
        self.cursor = conn.cursor(as_dict=True)

        return conn

    def getCursor(self) -> Cursor:
        return self.cursor
    
    def execute(self, query: str):
        self.cursor.execute(query)
        return self.cursor.fetchall()