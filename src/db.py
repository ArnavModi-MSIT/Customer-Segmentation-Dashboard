import os
import sys
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

_engine = None


def get_engine():
    """Returns a singleton SQLAlchemy engine built from config.DB_CONFIG."""
    global _engine
    if _engine is None:
        conn_str = (
            f"postgresql+psycopg2://{DB_CONFIG['username']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        _engine = create_engine(conn_str)
    return _engine
