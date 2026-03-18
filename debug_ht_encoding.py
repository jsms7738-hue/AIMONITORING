import json
import os

for key, path in [('ICT', r'c:\Users\yoonh\Desktop\AI\ICT데이타\data\data.json'), ('WI', r'c:\Users\yoonh\Desktop\AI\WI 검사 데이타\data\data.json')]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"--- {key} ---")
    for line in data['lines']:
        ht = line.get('hourly_trend', [])
        if ht:
            print(f"Line {line.get('line_id')} | First HT Entry: {ht[0]['time_slot']}")
        else:
            print(f"Line {line.get('line_id')} | NO HT")
