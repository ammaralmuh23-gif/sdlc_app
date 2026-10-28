import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import create_app
from models.db import execute_query

application = create_app()

try:
    sql = open('database.sql', 'r', encoding='utf-8').read()
    for stmt in sql.split(';'):
        if stmt.strip():
            try:
                execute_query(stmt)
            except Exception:
                pass
except Exception:
    pass
