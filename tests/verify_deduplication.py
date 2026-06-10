
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.transformation_service import TransformationService
from models.entities import CargaEvidenciaSource
from typing import List

def test_deduplication_and_capping():
    service = TransformationService()
    
    date_old = datetime(2024, 1, 1)
    date_mid = datetime(2024, 6, 1)
    date_new = datetime(2025, 1, 1)
    
    # Mock Data
    items = [
        # Scenario 1: Duplicates for SAME EvidenciaID.
        # Evid 101. File A (Old) 50 pts. File B (New) 50 pts.
        # Expected: Keep File B. Zero File A.
        # Total for SubInd 10: 50 (not 100).
        CargaEvidenciaSource(1, 1, 10, 101, 100, "FileA_Old.pdf", 50.0, date_old),
        CargaEvidenciaSource(2, 2, 10, 101, 100, "FileB_New.pdf", 50.0, date_new),
        
        # Scenario 2: Two DIFFERENT EvidenciaIDs. Sum > 100.
        # Evid 201 (60 pts). Evid 202 (60 pts).
        # Total 120 > 100.
        # Expected: Max Only applies. Keep Higher Score (Tie -> Newer?).
        # Let's say Evid 202 is newer.
        CargaEvidenciaSource(3, 3, 20, 201, 200, "FileC_Evid1.pdf", 60.0, date_mid),
        CargaEvidenciaSource(4, 4, 20, 202, 200, "FileD_Evid2.pdf", 60.0, date_new),
        
        # Scenario 3: Mixed. Duplicates + Different Evid.
        # Evid 301: V1(40, Old), V2(40, New). -> Keep V2(40).
        # Evid 302: 50 pts.
        # Total = 40 + 50 = 90. <= 100.
        # Expected: Keep V2 and Evid 302. V1 is zeroed by dedup.
        CargaEvidenciaSource(5, 5, 30, 301, 300, "FileE_V1.pdf", 40.0, date_old),
        CargaEvidenciaSource(6, 6, 30, 301, 300, "FileF_V2.pdf", 40.0, date_new),
        CargaEvidenciaSource(7, 7, 30, 302, 300, "FileG_Other.pdf", 50.0, date_mid),
    ]
    
    service.sub_ev_map = {} # Not needed for score internal logic
    
    print("Running transformation with Deduplication...")
    scores, files = service.transformar_puntuacion(items, start_file_id=1, start_score_id=1)
    
    print(f"Generated {len(scores)} scores.")
    vals = [s.Calificacion for s in scores]
    print(f"Values: {vals}")
    
    # Scenario 1: [0, 50]
    assert vals[0] == 0.0, "Old Duplicate should be 0"
    assert vals[1] == 50.0, "New Duplicate should be kept"
    
    # Scenario 2: [0, 60] (Max Only triggered)
    # Both 60. Newest (FileD) wins. FileC (Old) -> 0.
    assert vals[2] == 0.0
    assert vals[3] == 60.0
    
    # Scenario 3: [0, 40, 50]
    assert vals[4] == 0.0, "Old V1 should be 0"
    assert vals[5] == 40.0, "New V2 should be kept"
    assert vals[6] == 50.0, "Different evidence should be kept (Total 90 <= 100)"
    
    print("VERIFICATION SUCCEEDED")

if __name__ == "__main__":
    test_deduplication_and_capping()
