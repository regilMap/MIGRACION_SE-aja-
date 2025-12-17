# Migración SISMAPV1DB_ED → SISMAP_EDUCACION_M

## Estructura del proyecto

```
migracion/
├── config/
│   ├── __init__.py
│   └── database.py          # Conexiones a BD
├── models/
│   ├── __init__.py
│   └── entities.py          # Dataclasses (estructuras)
├── repositories/
│   ├── __init__.py
│   ├── fuente_repo.py       # Queries SELECT (fuente)
│   └── destino_repo.py      # Queries INSERT (destino)
├── services/
│   ├── __init__.py
│   └── migration_service.py # Lógica de migración
├── utils/
│   ├── __init__.py
│   └── logger.py            # Logging y estadísticas
├── exports/                  # Archivos JSON generados
├── logs/                     # Archivos de log
├── main.py                   # Punto de entrada
└── README.md
```

## Requisitos

```bash
pip install pyodbc
```

## Uso

### Migración completa (extrae + carga)
```bash
python main.py
```

### Solo extraer a JSON (sin cargar)
```bash
python main.py --solo-extraer
```

### Solo cargar desde exportación existente
```bash
python main.py --solo-cargar exports/migracion_20250115_143022
```

### Limpiar tablas antes de cargar
```bash
python main.py --limpiar
```

### Sin confirmación (para scripts)
```bash
python main.py --sin-confirmar
```

## Flujo de migración

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  BD FUENTE      │     │  Archivos JSON  │     │  BD DESTINO     │
│  SISMAPV1DB_ED  │ ──► │  (respaldo)     │ ──► │  SISMAP_EDUC_M  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        Puedes revisar
                        antes de cargar
```

## Rollback

Si la carga falla en cualquier punto:
1. Se ejecuta `ROLLBACK` automáticamente
2. Ningún dato queda insertado en destino
3. Los archivos JSON siguen disponibles para reintentar

## Agregar nuevas tablas

1. Agregar dataclass en `models/entities.py`
2. Agregar métodos de lectura en `repositories/fuente_repo.py`
3. Agregar métodos de escritura en `repositories/destino_repo.py`
4. Agregar extracción/carga en `services/migration_service.py`

## Logs

Los logs se guardan en `logs/` con timestamp:
```
logs/migracion_20250115_143022.log
```

Contienen:
- Hora de cada operación
- Registros extraídos/insertados
- Errores con detalle
- Resumen final
