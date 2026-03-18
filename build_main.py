import os
import sys
import json
import aggregate_data

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
TEMPLATE_PATH = os.path.join(BASE_DIR, "main_dashboard_template.html")
OUTPUT_PATH = os.path.join(BASE_DIR, "smps_dashboard.html")

def build():
    print("=== Starting SMPS Main Dashboard Build ===")
    
    # 1. Aggregate Data
    data = aggregate_data.aggregate()
    json_str = json.dumps(data, ensure_ascii=False)
    
    # 2. Read Template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return
        
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()
        
    # 3. Inject Data
    result = template.replace("{{AGGREGATED_DATA_JSON}}", json_str)
    
    # 4. Save Output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(result)
        
    print(f"=== Build Success! Dashboard created at: {OUTPUT_PATH} ===")

if __name__ == "__main__":
    build()
