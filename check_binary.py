import json
import os

path = r'c:\Users\yoonh\Desktop\AI\SMPS_MONITORING\data\aggregated_data.json'
with open(path, 'rb') as f:
    content = f.read(50000) # Read enough to get some ICT/WI data

# Find "ICT" and looking for "trend"
pos = content.find(b'"ICT"')
if pos != -1:
    snippet = content[pos:pos+5000]
    print(f"Snippet around ICT: {snippet[:200]!r}")
else:
    print("Could not find ICT in first 50KB")
