import json
import os
import sys
from datetime import datetime

# Determine BASE_DIR relative to this script's location (SMPS_MONITORING is inside AI)
if getattr(sys, 'frozen', False):
    CURRENT_DIR = os.path.dirname(sys.executable)
else:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(CURRENT_DIR)

PROJECTS = {
    "PBA": os.path.join(BASE_DIR, "PBA 생산 결과", "data", "data.json"),
    "ICT": os.path.join(BASE_DIR, "ICT데이타", "data", "data.json"),
    "FT1": os.path.join(BASE_DIR, "FT1검사 데이타", "data", "data.json"),
    "WI": os.path.join(BASE_DIR, "WI 검사 데이타", "data", "data.json")
}

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def aggregate():
    print("Aggregating data from all projects...")
    
    raw_data = {
        "PBA": load_json(PROJECTS["PBA"]),
        "ICT": load_json(PROJECTS["ICT"]),
        "FT1": load_json(PROJECTS["FT1"]),
        "WI": load_json(PROJECTS["WI"])
    }

    # Normalize ICT and WI data - they lack a daily 'trend' array per line
    for project_key in ["ICT", "WI"]:
        project = raw_data[project_key]
        if not project:
            print(f"Skipping normalization for {project_key}: No data found.")
            continue
        
        print(f"Normalizing {project_key} with {len(project.get('lines', []))} lines")
        
        for line in project.get("lines", []):
            if "hourly_trend" in line:
                print(f"  Line {line.get('line_id', 'N/A')} in {project_key} has hourly_trend, (re)normalizing...")
                # Group hourly_trend by date
                daily_groups = {}
                for h in line["hourly_trend"]:
                    # Robustly extract month and day digits from "3월 10일 A..." or "3 10 A..."
                    import re
                    matches = re.findall(r'(\d+)', h["time_slot"])
                    if len(matches) < 2: continue
                    
                    month_int = int(matches[0])
                    day_int = int(matches[1])
                    date_key = f"{month_int}월 {day_int}일"
                    
                    if date_key not in daily_groups:
                        daily_groups[date_key] = {"total": 0, "pass": 0, "fail": 0}
                    
                    daily_groups[date_key]["total"] += h.get("total", 0)
                    daily_groups[date_key]["pass"] += h.get("pass", 0)
                    daily_groups[date_key]["fail"] += h.get("fail", 0)
                
                # Keep old fail_details if they exist
                old_trend_details = {}
                for t in line.get("trend", []):
                    if "fail_details" in t:
                        old_trend_details[t["date"]] = t["fail_details"]

                # Convert to trend array
                trend_list = []
                for d, stats in daily_groups.items():
                    pass_rate = round((stats["pass"] / stats["total"] * 100), 1) if stats["total"] > 0 else 0
                    
                    trend_item = {
                        "date": d,
                        "total": stats["total"],
                        "pass": stats["pass"],
                        "fail": stats["fail"],
                        "pass_rate": pass_rate
                    }
                    if d in old_trend_details:
                        trend_item["fail_details"] = old_trend_details[d]
                        
                    trend_list.append(trend_item)
                
                # Sort by date
                def sort_key(x):
                    try:
                        # "3월 10일" -> 10
                        day_str = x["date"].split(' ')[1].replace('일', '')
                        return int(day_str)
                    except: return 0
                
                line["trend"] = sorted(trend_list, key=sort_key)

    all_data = {
        **raw_data,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save the aggregated data
    output_dir = os.path.join(CURRENT_DIR, "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "aggregated_data.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"Aggregation complete. Saved to {output_path}")
    return all_data

if __name__ == "__main__":
    aggregate()
