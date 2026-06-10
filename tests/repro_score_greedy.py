
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
        # Sort by Score Descending to keep highest scores
        group_items.sort(key=lambda x: x.Puntuacion, reverse=True)
        
        current_sum = 0.0
        
        print(f"Processing Org {org_id}, Ind {ind_id}...")
        
        for item in group_items:
            # Check if adding this score keeps us <= 100
            # Condition: "encima del 100... necesito que le pongas la puntuacion real a aquellas evidencias que en si sola o sumadas en conjunto dan 100"
            # Does "dan 100" mean EXACTLY 100 or "up to 100"?
            # Typically "up to 100".
            # "que sumada con las otras da mas de 100 le pongas 0"
            # This implies if Sum + New > 100, reject New.
            
            if current_sum + item.Puntuacion <= 100:
                current_sum += item.Puntuacion
                print(f"  Keep {item.Puntuacion} (ID: {item.CargaEvidenciaID}). New Sum: {current_sum}")
            else:
                print(f"  Reject {item.Puntuacion} (ID: {item.CargaEvidenciaID}). Would be {current_sum + item.Puntuacion} > 100.")
                item.Puntuacion = 0.0

def test_logic():
    # Setup Data
    items = [
        # Case 1: 100, 80, 60 (From User Image)
        CargaEvidenciaSource(1, 100, 1, 100.0, "File1"),
        CargaEvidenciaSource(2, 100, 1, 80.0, "File2"),
        CargaEvidenciaSource(3, 100, 1, 60.0, "File3"),
        
        # Case 2: 60, 30, 25 (Previous Example)
        CargaEvidenciaSource(4, 200, 1, 60.0, "File4"),
        CargaEvidenciaSource(5, 200, 1, 30.0, "File5"),
        CargaEvidenciaSource(6, 200, 1, 25.0, "File6"),
        
        # Case 3: 50, 50, 10 (Strict 100 match)
        CargaEvidenciaSource(7, 300, 1, 50.0, "File7"),
        CargaEvidenciaSource(8, 300, 1, 50.0, "File8"),
        CargaEvidenciaSource(9, 300, 1, 10.0, "File9"),
        
        # Case 4: 51, 50 (Greedy choice)
        CargaEvidenciaSource(10, 400, 1, 50.0, "File10"),
        CargaEvidenciaSource(11, 400, 1, 51.0, "File11"),
    ]
    
    adjust_scores(items)
    
    # Assertions
    
    # Case 1: 100, 0, 0
    # ID 1
    assert items[0].Puntuacion == 100.0
    # ID 2
    assert items[1].Puntuacion == 0.0
    # ID 3
    assert items[2].Puntuacion == 0.0
    
    # Case 2: 60, 30, 0 (Total 90)
    # ID 4 (60)
    assert items[3].Puntuacion == 60.0
    # ID 5 (30)
    assert items[4].Puntuacion == 30.0
    # ID 6 (25) -> 0
    assert items[5].Puntuacion == 0.0
    
    # Case 3: 50, 50, 0
    items_case3 = sorted([items[6], items[7], items[8]], key=lambda x: x.CargaEvidenciaID)
    # Sorted by ID again to check index, but logic sorted by score
    # 50, 50 are kept. 10 is dropped.
    assert items[6].Puntuacion == 50.0
    assert items[7].Puntuacion == 50.0
    assert items[8].Puntuacion == 0.0
    
    # Case 4: 51, 0 (51 > 50, greedy takes 51. 51+50 > 100)
    # ID 11 is 51. ID 10 is 50.
    assert items[10].Puntuacion == 51.0
    assert items[9].Puntuacion == 0.0
    
    print("\nTest Passed!")

if __name__ == "__main__":
    test_logic()
