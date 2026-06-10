
import sys
import os
from config.database import conectar_fuente
from repositories.fuente_repo import FuenteRepository
from services.transformation_service import TransformationService

def check_orphans():
    conn = conectar_fuente()
    repo = FuenteRepository(conn)
    service = TransformationService()
    
    codigos = ['01.2', '01.5', '02.8', '01.4', '02.5', '01.1', '02.6', '05.05', '03.4', '05.04', '01.6', '02.1', '02.3', '02.2', '05.10', '02.4', '05.09', '05.02', '06.3', '01.3', '02.7', '06.5', '06.4', '05.01', '05.03', '05.07', 'Np 07.1', '05.08', '03.3', 'Ns 07.1', '06.1', 'Ns 07.2']
    
    # 1. Load Evidences (to populate sub_ev_map)
    print("Fetching evidences...")
    evidencias_source = repo.obtener_evidencias() # Ideally filtered, but getting all for safety of map population
    # To properly filter, we'd need the JOIN logic from the repo, but for diagnosis let's get what we can.
    # Actually, obtener_evidencias in original repo didn't filter by code effectively without params?
    # Let's trust that the repo returns what's needed or get all. obtain_evidencias returns all in the file view.
    
    service.transformar_evidencia(evidencias_source)
    print(f"Map populated with {len(service.sub_ev_map)} keys.")
    
    # 2. Load Scores
    print("Fetching scores...")
    puntuaciones_source = repo.obtener_puntuaciones(codigos)
    print(f"Total Source Scores: {len(puntuaciones_source)}")
    
    orphans = 0
    null_scores = 0
    valid = 0
    
    for item in puntuaciones_source:
        key = (item.IndicadorID, item.EvidenciaID)
        sub_ev_id = service.sub_ev_map.get(key)
        
        if sub_ev_id is None:
            orphans += 1
            # print(f"Orphan found: IndicadorID={item.IndicadorID}, EvidenciaID={item.EvidenciaID}")
        
        if item.Puntuacion is None:
            null_scores += 1
        
        if sub_ev_id is not None and item.Puntuacion is not None:
            valid += 1
            
    print(f"Orphans (No Evidence Match): {orphans}")
    print(f"NULL Scores: {null_scores}")
    print(f"Valid (To be migrated): {valid}")

if __name__ == "__main__":
    check_orphans()
