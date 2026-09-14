# Migración SISMAPV1DB_SG → SISMAP_SEGURIDAD

Sistema ETL de migración para mover la información de la base de datos previa de SISMAP Seguridad (`SISMAPV1DB_SG`) a la nueva estructura modular por esquemas (`SISMAP_SEGURIDAD`).

## Estructura del proyecto

```
migracion/
├── config/
│   ├── __init__.py
│   └── database.py          # Conexiones a BD FUENTE y DESTINO
├── models/
│   ├── __init__.py
│   └── entities.py          # Dataclasses (estructuras de datos)
├── repositories/
│   ├── __init__.py
│   ├── fuente_repo.py       # Queries SELECT (SISMAPV1DB_SG)
│   └── destino_repo.py      # Queries INSERT/MERGE (SISMAP_SEGURIDAD)
├── services/
│   ├── __init__.py
│   ├── transformation_service.py # Lógica de mapeo y transformación
│   └── migration_service.py # Orquestación del flujo ETL
├── utils/
│   ├── __init__.py
│   └── logger.py            # Logging y estadísticas
├── exports/                  # Archivos JSON intermedios generados
├── logs/                     # Archivos de log
├── main.py                   # Punto de entrada CLI
└── README.md
```

## Requisitos

```bash
pip install pyodbc
```

## Uso

### Migración completa (extrae de fuente + carga a destino)
```bash
python main.py
```

### Solo extraer a JSON (sin cargar)
```bash
python main.py --solo-extraer
```

### Solo cargar desde exportación existente
```bash
python main.py --solo-cargar exports/migracion_seguridad_20260911_100000
```

### Limpiar tablas destino antes de cargar
```bash
python main.py --limpiar
```

### Sin confirmación manual (modo desatendido / scripts)
```bash
python main.py --sin-confirmar
```

## Flujo de migración

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  BD FUENTE          │     │  Archivos JSON      │     │  BD DESTINO         │
│  SISMAPV1DB_SG      │ ──► │  (respaldo interm.) │ ──► │  SISMAP_SEGURIDAD   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```
