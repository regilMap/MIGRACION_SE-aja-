import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.transformation_service import TransformationService

def main():
    service = TransformationService()
    
    # Format indicator code test cases
    test_cases_format = [
        ("01.1", "1.01"),
        ("01.2", "1.02"),
        ("01.3", "1.03"),
        ("01.4", "1.04"),
        ("01.5", "1.05"),
        ("01.6", "1.06"),
        ("02.1", "2.01"),
        ("02.8", "2.08"),
        ("03.1", "3.01"),
        ("03.6", "3.06"),
        ("04.3", "4.03"),
        ("06.1", "6.01"),
        ("06.5", "6.05"),
        ("07.2", "Ns 7.02"), # assuming transformed to Ns 07.2 first or we format Ns 07.2
        ("Ns 07.2", "Ns 7.02"),
        ("08.1", "8.01"),
        ("09.1", "9.01"),
        ("5.01", "5.01"),
        ("5.10", "5.10"),
        ("Np 07.1", "Np 7.01"),
        ("Ns 07.1", "Ns 7.01"),
        ("01.1.1", "1.01.1"),
        ("01.1.2", "1.01.2"),
        ("Np 07.1.3", "Np 7.01.3"),
    ]
    
    print("--- Testing format_indicator_code ---")
    all_passed = True
    for inp, expected in test_cases_format:
        if inp == "07.2":
            # 07.2 is first changed to Ns 07.2 in the transformation logic
            code = "Ns 07.2"
        else:
            code = inp
            
        res = service.format_indicator_code(code)
        if res == expected:
            print(f"[PASS] {inp} -> {res}")
        else:
            print(f"[FAIL] {inp} -> Expected {expected}, got {res}")
            all_passed = False
            
    # Map to source code test cases
    test_cases_source = [
        ("1.01", "01.1"),
        ("1.02", "01.2"),
        ("1.03", "01.3"),
        ("1.04", "01.4"),
        ("1.05", "01.5"),
        ("1.06", "01.6"),
        ("2.01", "02.1"),
        ("2.08", "02.8"),
        ("3.01", "03.1"),
        ("3.06", "03.6"),
        ("4.03", "04.3"),
        ("6.01", "06.1"),
        ("6.05", "06.5"),
        ("Ns 7.02", "07.2"),
        ("8.01", "08.1"),
        ("9.01", "09.1"),
        ("5.01", "5.01"),
        ("5.10", "5.10"),
        ("Np 7.01", "Np 07.1"),
        ("Ns 7.01", "Ns 07.1"),
    ]
    
    print("\n--- Testing map_to_source_code ---")
    for inp, expected in test_cases_source:
        res = service.map_to_source_code(inp)
        if res == expected:
            print(f"[PASS] {inp} -> {res}")
        else:
            print(f"[FAIL] {inp} -> Expected {expected}, got {res}")
            all_passed = False
            
    if all_passed:
        print("\nALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("\nSOME TESTS FAILED!")

if __name__ == '__main__':
    main()
