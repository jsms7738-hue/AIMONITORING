import extract_data
import build_dashboard
import os
import sys

def run_full_build():
    print("=== Starting Full Dashboard Update ===")
    
    try:
        # 1. Extract Data
        print("\nStep 1: Extracting data from Excel...")
        extract_data.process_file()
        
        # 2. Build Dashboard
        print("\nStep 2: Building dashboard HTML files...")
        build_dashboard.build()
        
        print("\n=== Full Dashboard Update Success! ===")
        return True
    except Exception as e:
        print(f"\n!!! Update Failed: {e}")
        return False

if __name__ == "__main__":
    run_full_build()
