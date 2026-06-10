
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CargaEvidenciaSource:
    CargaEvidenciaID: int
    OrganismoID: int
    Puntuacion: Optional[float]
    NombreArchivo: str

def adjust_scores(items: List[CargaEvidenciaSource]):
    # Group by OrganismoID
    grouped = {}
    for item in items:
        if item.OrganismoID not in grouped:
            grouped[item.OrganismoID] = []
        grouped[item.OrganismoID].append(item)
    
    # Process each group
    for org_id, group_items in grouped.items():
        # Calculate total score
        total_score = sum(item.Puntuacion for item in group_items if item.Puntuacion is not None)
        
        if total_score > 100:
            print(f"Institution {org_id} has total score {total_score} > 100. Adjusting...")
            
            # Find max score item
            # We filter for items with score to avoid issues, though None scores usually ignored or 0
            scored_items = [i for i in group_items if i.Puntuacion is not None]
            
            if not scored_items:
                continue
                
            # Find the item with the max score
            # Determine logic for ties: Keep the first one encountered or specific rule?
            # User says: "Mantener la puntuación más alta sin cambios"
            # We will sort by Puntuacion descending
            scored_items.sort(key=lambda x: x.Puntuacion, reverse=True)
            
            max_item = scored_items[0]
            print(f"  Keeping Max Score: {max_item.Puntuacion} (ID: {max_item.CargaEvidenciaID})")
            
            # Set others to 0
            for item in scored_items[1:]:
                print(f"  Setting Score {item.Puntuacion} (ID: {item.CargaEvidenciaID}) -> 0")
                item.Puntuacion = 0.0

def test_logic():
    # Setup Data
    items = [
        # Institution 123 (Total 115 > 100)
        CargaEvidenciaSource(1, 123, 60.0, "File1"),
        CargaEvidenciaSource(2, 123, 30.0, "File2"),
        CargaEvidenciaSource(3, 123, 25.0, "File3"),
        
        # Institution 456 (Total 90 < 100)
        CargaEvidenciaSource(4, 456, 50.0, "File4"),
        CargaEvidenciaSource(5, 456, 40.0, "File5"),
        
        # Institution 789 (Total 100 == 100)
        CargaEvidenciaSource(6, 789, 100.0, "File6"),
        
        # Institution 999 (Mixed with None)
        CargaEvidenciaSource(7, 999, 150.0, "File7"),
        CargaEvidenciaSource(8, 999, 10.0, "File8"),
        CargaEvidenciaSource(9, 999, None, "File9"),
    ]
    
    print("Before:")
    for i in items:
        print(f"ID: {i.CargaEvidenciaID}, Org: {i.OrganismoID}, Score: {i.Puntuacion}")
        
    adjust_scores(items)
    
    print("\nAfter:")
    for i in items:
        print(f"ID: {i.CargaEvidenciaID}, Org: {i.OrganismoID}, Score: {i.Puntuacion}")
        
    # Assertions
    # 123
    assert items[0].Puntuacion == 60.0
    assert items[1].Puntuacion == 0.0
    assert items[2].Puntuacion == 0.0
    
    # 456
    assert items[3].Puntuacion == 50.0
    assert items[4].Puntuacion == 40.0
    
    # 999
    # 150 + 10 = 160 > 100. Max is 150. 10 -> 0.
    assert items[6].Puntuacion == 150.0
    assert items[7].Puntuacion == 0.0
    
    print("\nTest Passed!")

if __name__ == "__main__":
    test_logic()
