import json
with open('data/data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('=== 전체 일별 데이터 (daily_averages) ===')
for da in d['daily_averages']:
    print(f'  {da["date"]}: pass_rate={da["pass_rate"]}%')

print()
print('=== 2A 라인 3월17일/18일 trend ===')
line_2a = next((l for l in d['lines'] if l['line_id'] == '2A'), None)
if line_2a:
    for t in line_2a['trend']:
        if '17' in t['date'] or '18' in t['date']:
            print(f'  {t["date"]}: total={t["total"]}, pass={t["pass"]}, fail={t["fail"]}, pass_rate={t["pass_rate"]}%')
else:
    print('2A 라인 없음')
