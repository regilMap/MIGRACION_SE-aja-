import pyodbc

configs = [
    {
        "name": "I1491S con SQL Auth (SismapSeguridad_User)",
        "conn_str": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=I1491S;DATABASE=SISMAPV1DB_SG;UID=SismapSeguridad_User;PWD=SMS_2026;"
    },
    {
        "name": "I1491S con Windows Auth",
        "conn_str": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=I1491S;DATABASE=SISMAPV1DB_SG;Trusted_Connection=yes;"
    },
    {
        "name": "D1491N2023 con Windows Auth",
        "conn_str": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=D1491N2023;DATABASE=SISMAPV1DB_SG;Trusted_Connection=yes;"
    },
    {
        "name": "localhost / . con Windows Auth",
        "conn_str": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=SISMAPV1DB_SG;Trusted_Connection=yes;"
    }
]

for cfg in configs:
    print(f"\nProbando: {cfg['name']}...")
    try:
        conn = pyodbc.connect(cfg["conn_str"], timeout=5)
        print(f"  --> EXITO!")
        conn.close()
    except Exception as e:
        print(f"  --> FALLO: {e}")
