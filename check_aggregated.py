import json

with open('data/aggregated_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('=== AGGREGATED DATA CHECK ===')
print(f'Generated at: {d.get("generated_at")}')
print()

for key in ['PBA', 'ICT', 'FT1', 'WI']:
    proj = d.get(key)
    if proj:
        lines = proj.get('lines', [])
        print(f'{key}: {len(lines)} lines found')
        for l in lines[:3]:
            trend_len = len(l.get('trend', []))
            ht_len = len(l.get('hourly_trend', []))
            print(f'  Line {l["line_id"]}: trend={trend_len} days, hourly_trend={ht_len} slots')
        if len(lines) > 3:
            print(f'  ... and {len(lines)-3} more lines')
    else:
        print(f'{key}: NO DATA FOUND!')
    print()

print('=== LINE MAPPING CHECK ===')
# Check if ICT/WI line IDs match expected 2A-2I format
ict = d.get('ICT', {})
wi = d.get('WI', {})
ft1 = d.get('FT1', {})
pba = d.get('PBA', {})

ict_lines = [l['line_id'] for l in ict.get('lines', [])]
wi_lines = [l['line_id'] for l in wi.get('lines', [])]
ft1_lines = [l['line_id'] for l in ft1.get('lines', [])]
pba_lines = [l['line_id'] for l in pba.get('lines', [])]

print(f'ICT lines: {ict_lines}')
print(f'WI lines: {wi_lines}')
print(f'FT1 lines: {ft1_lines}')
print(f'PBA lines: {pba_lines}')

print()
print('=== POTENTIAL MAPPING PROBLEM ===')
# The lineMapping in main_dashboard_template.html maps MPD -> 2X
# but only maps MPDA/B/C/D/E/F/G together
lineMapping = {
    "MPDA": "2A", "MPDB": "2B", "MPDC": "2C", "MPDD": "2D",
    "MPDE": "2E", "MPDF": "2F", "MPDG": "2G", "MPH": "2H", "MPI": "2I"
}
print('HTML lineMapping:', lineMapping)
print()
print('Checking if each PBA line maps to a valid ICT/WI line:')
for pba_line in pba_lines:
    mapped = lineMapping.get(pba_line, pba_line)
    in_ict = mapped in ict_lines
    in_wi = mapped in wi_lines
    in_ft1 = pba_line in ft1_lines
    status = []
    if not in_ict: status.append(f'ICT not found (looking for "{mapped}")')
    if not in_wi: status.append(f'WI not found (looking for "{mapped}")')
    if not in_ft1: status.append(f'FT1 not found (looking for "{pba_line}")')
    if status:
        print(f'  PBA {pba_line} -> {mapped}: ISSUES: {", ".join(status)}')
    else:
        print(f'  PBA {pba_line} -> {mapped}: OK')
