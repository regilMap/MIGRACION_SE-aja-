import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from services.transformation_service import TransformationService
    print("Syntax Check: OK")
except Exception as e:
    print(f"Syntax Check: FAILED - {e}")
