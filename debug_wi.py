import json
import os

path = r'c:\Users\yoonh\Desktop\AI\WI 검사 데이타\data\data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for line in data['lines']:
    trend = line.get('trend', [])
    print(f"Line ID: {line.get('line_id')} | Trend Count: {len(trend)}")
    if len(trend) > 0:
        print(f"  First Entry: {trend[0]}")
