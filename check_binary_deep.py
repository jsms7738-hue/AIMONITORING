import json
import os

path = r'c:\Users\yoonh\Desktop\AI\SMPS_MONITORING\data\aggregated_data.json'
with open(path, 'rb') as f:
    f.seek(1500000) # Jump ahead
    content = f.read(100000) 

# Find "ICT"
pos = content.find(b'"ICT"')
if pos != -1:
    snippet = content[pos:pos+1000]
    print(f"Snippet around ICT: {snippet!r}")
else:
    print("Could not find ICT in the checked chunk")
