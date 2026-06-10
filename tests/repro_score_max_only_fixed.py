
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CargaEvidenciaSource:
    CargaEvidenciaID: int
    OrganismoID: int
    IndicadorID: int
    Puntuacion: Optional[float]
    NombreArchivo: str

def adjust_scores(items: List[CargaEvidenciaSource]):
    # Group by (OrganismoID, IndicadorID)
    grouped = {}
    for item in items:
        if item.Puntuacion is None:
            continue
            
        key = (item.OrganismoID, item.IndicadorID)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    # Process each group
    for (org_id, ind_id), group_items in grouped.items():
        total_score = sum(item.Puntuacion for item in group_items)
        
        if total_score > 100:
            print(f"Group ({org_id}, {ind_id}) Sum: {total_score} > 100. Applying MAX ONLY rule.")
            
            # Find item with Max Puntuacion
            # Sort descending by Score
            group_items.sort(key=lambda x: x.Puntuacion, reverse=True)
            
            # Keep the first one (Highest)
            highest_item = group_items[0]
            print(f"  Keeping Highest: {highest_item.Puntuacion} (ID: {highest_item.CargaEvidenciaID})")
            
            # Set all others to 0
            for item in group_items[1:]:
                print(f"  Setting {item.Puntuacion} (ID: {item.CargaEvidenciaID}) -> 0")
                item.Puntuacion = 0.0
        else:
             print(f"Group ({org_id}, {ind_id}) Sum: {total_score} <= 100. No change.")

def test_logic():
    # Setup Data
    items = [
        # Case 1: 100, 80, 60 (Sum 240 > 100) -> Keep 100, others 0
        CargaEvidenciaSource(1, 100, 1, 100.0, "File1"),
        CargaEvidenciaSource(2, 100, 1, 80.0, "File2"),
        CargaEvidenciaSource(3, 100, 1, 60.0, "File3"),
        
        # Case 2: 60, 30, 25 (Sum 115 > 100) -> Keep 60, others 0
        CargaEvidenciaSource(4, 200, 1, 60.0, "File4"),
        CargaEvidenciaSource(5, 200, 1, 30.0, "File5"),
        CargaEvidenciaSource(6, 200, 1, 25.0, "File6"),
        
        # Case 3: 50, 50 (Sum 100) -> No Change
        CargaEvidenciaSource(7, 300, 1, 50.0, "File7"),
        CargaEvidenciaSource(8, 300, 1, 50.0, "File8"),
        
        # Case 4: 51, 50 (Sum 101 > 100) -> Keep 51, others 0
        CargaEvidenciaSource(10, 400, 1, 50.0, "File10"),
        CargaEvidenciaSource(11, 400, 1, 51.0, "File11"),
    ]
    # Total items: 3+3+2+2 = 10 items. Indices 0..9
    
    adjust_scores(items)
    
    # Assertions
    
    # Case 1: 100, 0, 0
    assert items[0].Puntuacion == 100.0
    assert items[1].Puntuacion == 0.0
    assert items[2].Puntuacion == 0.0
    
    # Case 2: 60, 0, 0
    assert items[3].Puntuacion == 60.0
    assert items[4].Puntuacion == 0.0  # Changed from 30 to 0
    assert items[5].Puntuacion == 0.0
    
    # Case 3: 50, 50
    assert items[6].Puntuacion == 50.0
    assert items[7].Puntuacion == 50.0
    
    # Case 4: 51, 0
    # ID=10 is 50.0 (index 8)
    # ID=11 is 51.0 (index 9)
    # 51 is max, so index 9 kept. Index 8 zeroed.
    
    assert items[8].Puntuacion == 0.0
    assert items[9].Puntuacion == 51.0
    
    print("\nTest Passed!")

if __name__ == "__main__":
    test_logic()
