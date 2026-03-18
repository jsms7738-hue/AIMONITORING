import json

with open('data/aggregated_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

wi = d.get('WI', {})
lines = wi.get('lines', [])

print(f'WI lines: {[l["line_id"] for l in lines]}')
print()

for line in lines[:2]:  # Check first 2 lines
    lid = line['line_id']
    ht = line.get('hourly_trend', [])
    trend = line.get('trend', [])
    print(f'=== Line {lid} ===')
    print(f'  trend days: {[t["date"] for t in trend]}')
    print(f'  hourly_trend total slots: {len(ht)}')
    # Show slots for 17일 and 18일
    slots_17 = [h for h in ht if '17' in h.get('time_slot','')]
    slots_18 = [h for h in ht if '18' in h.get('time_slot','')]
    print(f'  3월 17일 hourly slots: {len(slots_17)}')
    for s in slots_17[:3]:
        print(f'    {s["time_slot"]} -> total={s["total"]}')
    print(f'  3월 18일 hourly slots: {len(slots_18)}')
    for s in slots_18[:3]:
        print(f'    {s["time_slot"]} -> total={s["total"]}')
    print()
