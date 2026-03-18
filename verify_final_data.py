import json
import os

path = r'c:\Users\yoonh\Desktop\AI\SMPS_MONITORING\data\aggregated_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for project_key in ['ICT', 'WI']:
    project = data.get(project_key, {})
    lines = project.get('lines', [])
    if lines:
        line = lines[0]
        trend = line.get('trend', [])
        print(f"--- {project_key} Line {line.get('line_id')} ---")
        print(f"Trend Count: {len(trend)}")
        if trend:
            print(f"First Entry: {trend[0]}")
            print(f"Last Entry: {trend[-1]}")
