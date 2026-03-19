import extract_data_ft1
import build_dashboard
import os
import sys

def run_full_build():
    print("=== Starting Full FT1 Dashboard Update ===")
    
    try:
        # 1. Extract Data
        print("\nStep 1: Extracting FT1 data from Excel...")
        extract_data_ft1.process_file()
        
        # 2. Build Dashboard
        print("\nStep 2: Building FT1 dashboard HTML files...")
        build_dashboard.build()
        
        print("\n=== Full FT1 Dashboard Update Success! ===")
        return True
    except Exception as e:
        print(f"\n!!! FT1 Update Failed: {e}")
        return False

if __name__ == "__main__":
    run_full_build()
