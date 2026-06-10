
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.transformation_service import TransformationService
from models.entities import CargaEvidenciaSource
from typing import List

def test_transformation_capping():
    service = TransformationService()
    
    # Dates for tie-breaking
    date_old = datetime(2024, 1, 1)
    date_new = datetime(2025, 1, 1)
    
    # Mock Data
    # CargaEvidenciaSource(CargaEvidenciaID, ArchivoCargaEvidenciaID, IndicadorID, EvidenciaID, OrganismoID, NombreArchivo, Puntuacion, FechaArchivo)
    # Check entities.py for EXACT signature if not using keywords
    # CargaEvidenciaID, ArchivoCargaEvidenciaID, IndicadorID, EvidenciaID=, OrganismoID=, NombreArchivo=, Puntuacion=, FechaArchivo=
    
    items = [
        # Case 1: Tie in Score (100, 100). Total 200 > 100.
        CargaEvidenciaSource(1, 1, 10, 5, 100, "FileA_Old.pdf", 100.0, date_old),
        CargaEvidenciaSource(2, 2, 10, 5, 100, "FileB_New.pdf", 100.0, date_new),
        
        # Case 2: Max Score wins regardless of date (Newer is lower score)
        CargaEvidenciaSource(3, 3, 20, 5, 200, "FileC_New_Low.pdf", 80.0, date_new),
        CargaEvidenciaSource(4, 4, 20, 5, 200, "FileD_Old_High.pdf", 90.0, date_old),
    ]
    
    # SubEv Map mock
    service.sub_ev_map = {(10, 5): 999, (20, 5): 888}
    
    print("Running transformation with Tie-Breaking...")
    scores, files = service.transformar_puntuacion(items, start_file_id=1, start_score_id=1)
    
    print(f"Generated {len(scores)} scores.")
    
    vals = [s.Calificacion for s in scores]
    print(f"Values: {vals}")
    
    pass_1 = False
    pass_2 = False
    
    # Case 1: [100, 100] -> [0, 100] because 2nd file is NEWER.
    # Scores order follows ITEMS order. Item 0 is Old (should be 0). Item 1 is New (should be 100).
    if vals[0] == 0.0 and vals[1] == 100.0:
        print("PASS: Newer file kept in tie.")
        pass_1 = True
    else:
        print(f"FAIL Case 1: Expected [0.0, 100.0], Got {vals[:2]}")
    
    # Case 2: [80, 90] -> [0, 90] because 90 is higher score.
    # Item 2 is 80 (should be 0). Item 3 is 90 (kept).
    if vals[2] == 0.0 and vals[3] == 90.0:
        print("PASS: Higher score kept despite date.")
        pass_2 = True
    else:
        print(f"FAIL Case 2: Expected [0.0, 90.0], Got {vals[2:]}")
    
    if pass_1 and pass_2:
        print("VERIFICATION SUCCEEDED")
    else:
        print("VERIFICATION FAILED")

if __name__ == "__main__":
    test_transformation_capping()
