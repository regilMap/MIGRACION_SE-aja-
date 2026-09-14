import pyodbc
from typing import Optional

class DatabaseConfig:
    """Configuración de conexiones a bases de datos"""
    
    FUENTE = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'server': 'D1491N2023',
        'database': 'SISMAPV1DB_SG',
        'trusted_connection': True
    }
    
    DESTINO = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'server': 'I1491S',
        'database': 'SISMAP_SEGURIDAD',
        'uid': 'SismapSeguridad_User',
        'pwd': 'SMS_2026'
    }


def conectar_fuente() -> Optional[pyodbc.Connection]:
    """Conexión a BD FUENTE (SISMAPV1DB_SG) - Windows Auth"""
    cfg = DatabaseConfig.FUENTE
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            "Trusted_Connection=yes;",
            timeout=10
        )
        conn.autocommit = False
        print(f"[OK] Conexión BD FUENTE exitosa ({cfg['database']})")
        return conn
    except pyodbc.Error as e:
        print(f"[ERROR] Error BD FUENTE: {e}")
        return None


def conectar_destino() -> Optional[pyodbc.Connection]:
    """Conexión a BD DESTINO (SISMAP_SEGURIDAD) - SQL Auth"""
    cfg = DatabaseConfig.DESTINO
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['uid']};"
            f"PWD={cfg['pwd']};",
            timeout=10
        )
        conn.autocommit = False
        print(f"[OK] Conexión BD DESTINO exitosa ({cfg['database']})")
        return conn
    except pyodbc.Error as e:
        print(f"[ERROR] Error BD DESTINO: {e}")
        return None
