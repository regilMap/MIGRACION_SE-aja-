import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from services.transformation_service import TransformationService
from models.entities import EvidenciaSource

class TestTransformationService(unittest.TestCase):
    def test_exclude_template_files(self):
        service = TransformationService()
        
        # Mock EvidenciaSource that looks like a template
        mock_evidence = EvidenciaSource(
            EvidenciaID=1,
            Codigo="E01",
            Descipcion="Test Template",
            NombreArchivo="Template.pdf", # Should be ignored
            Prerequisito=None,
            IndicadorID=100,
            Criterio="Criterio",
            Valor=10.0,
            AplicaVencimiento=False,
            TipoVencimiento=1,
            FechaVencimiento=datetime.now(),
            CantDias="30",
            Estado="Activo"
        )
        
        evidencias, fechas, sub_ind_evs, archivos = service.transformar_evidencia([mock_evidence])
        
        # Verify NO file is created
        self.assertEqual(len(archivos), 0, "Should not create ArchivoDest for template Evidence")
        
        # Verify other entities are created
        self.assertEqual(len(evidencias), 1)
        self.assertEqual(len(sub_ind_evs), 1)

if __name__ == '__main__':
    unittest.main()
