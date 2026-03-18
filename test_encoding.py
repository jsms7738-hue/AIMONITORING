import json
import os

path = r'c:\Users\yoonh\Desktop\AI\ICT데이타\data\data.json'
try:
    with open(path, 'r', encoding='cp949') as f:
        data = json.load(f)
    print("Successfully read with cp949")
    print(f"First line trend date: {data['lines'][0]['trend'][0]['date']}")
except Exception as e:
    print(f"Failed to read with cp949: {e}")

try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Read with utf-8 fallback (may have errors)")
    print(f"First line trend date: {data['lines'][0]['trend'][0]['date']}")
except Exception as e:
    print(f"Failed to read with utf-8: {e}")
