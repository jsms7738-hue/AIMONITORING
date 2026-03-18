import json
import os

path = r'c:\Users\yoonh\Desktop\AI\ICT데이타\data\data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Project overall keys: {data.keys()}")
if 'lines' in data:
    print(f"Number of lines: {len(data['lines'])}")
    for line in data['lines']:
        print(f"Line ID: {line.get('line_id')} | Keys: {list(line.keys())[:10]}...")
        if 'hourly_trend' in line:
            print(f"  FOUND hourly_trend for {line.get('line_id')}")
        else:
            print(f"  NOT FOUND hourly_trend for {line.get('line_id')}")
