import extract_data_wi
import build_dashboard
import os
import sys

def run_full_build():
    print("=== Starting Full WI Dashboard Update ===")
    
    try:
        # 1. Extract Data
        print("\nStep 1: Extracting WI data from Excel...")
        extract_data_wi.process_file()
        
        # 2. Build Dashboard
        print("\nStep 2: Building WI dashboard HTML files...")
        build_dashboard.build()
        
        print("\n=== Full WI Dashboard Update Success! ===")
        return True
    except Exception as e:
        print(f"\n!!! WI Update Failed: {e}")
        return False

if __name__ == "__main__":
    run_full_build()
