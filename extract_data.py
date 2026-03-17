import pandas as pd
import json
import os

# Get the directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "3월데이타 ICT.xlsx")
output_dir = os.path.join(base_dir, "data")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
json_path = os.path.join(output_dir, "data.json")

def process_file():
    try:
        xl = pd.ExcelFile(file_path)
        sheet_names = sorted(xl.sheet_names)
        
        all_sheets_data = []
        overall_total = 0
        overall_g = 0
        overall_n = 0
        
        # Line-centric aggregation
        lines_summary = {} # {line_id: {total, pass, fail, pass_rate, models: set(), dates: []}}
         # Daily average aggregation (across all lines)
        daily_averages_map = {} # {date: {total, pass}}
        
        for sheet in sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            
            # Format sheet name as date (MMDD -> M월 D일)
            display_sheet_name = sheet
            if len(sheet) == 4 and sheet.isdigit():
                display_sheet_name = f"{int(sheet[:2])}월 {int(sheet[2:])}일"

            # Basic stats
            total_rows = len(df)
            g_count = 0
            if 'RESULT' in df.columns:
                counts = df['RESULT'].value_counts()
                g_count = int(counts.get('G', 0))
            
            # Track for overall daily average
            if display_sheet_name not in daily_averages_map:
                daily_averages_map[display_sheet_name] = {"total": 0, "pass": 0}
            daily_averages_map[display_sheet_name]["total"] += total_rows
            daily_averages_map[display_sheet_name]["pass"] += g_count

            overall_total += total_rows
            overall_g += g_count
            overall_n += (total_rows - g_count)
            
            # ... rest of the loop remains focused on line-centric until here ...
            if 'LINE_ID' not in df.columns:
                continue

            unique_lines = df['LINE_ID'].dropna().unique()
            step_cols = [f'STEP_{i}' for i in range(1, 21) if f'STEP_{i}' in df.columns]

            for line in unique_lines:
                ldf = df[df['LINE_ID'] == line]
                l_total = len(ldf)
                l_g = (ldf['RESULT'] == 'G').sum() if 'RESULT' in ldf.columns else 0
                l_n = l_total - l_g
                l_models = ldf['MAT_NM'].unique().tolist() if 'MAT_NM' in ldf.columns else []

                if line not in lines_summary:
                    lines_summary[line] = {
                        "line_id": str(line),
                        "total": 0,
                        "pass": 0,
                        "fail": 0,
                        "models": set(),
                        "model_stats": {},  # {model_name: {total, pass, fail}}
                        "trend": [],
                        "fail_steps": {}    # {model: {step_name: count}}
                    }

                lines_summary[line]["total"] += l_total
                lines_summary[line]["pass"] += int(l_g)
                lines_summary[line]["fail"] += int(l_n)
                for m in l_models: lines_summary[line]["models"].add(str(m))

                # Aggregate per-model production stats
                if 'MAT_NM' in ldf.columns:
                    for model_name, mdf in ldf.groupby('MAT_NM'):
                        m_key = str(model_name)
                        m_total = len(mdf)
                        m_pass = int((mdf['RESULT'] == 'G').sum()) if 'RESULT' in mdf.columns else 0
                        m_fail = m_total - m_pass
                        ms = lines_summary[line]["model_stats"]
                        if m_key not in ms:
                            ms[m_key] = {"total": 0, "pass": 0, "fail": 0}
                        ms[m_key]["total"] += m_total
                        ms[m_key]["pass"]  += m_pass
                        ms[m_key]["fail"]  += m_fail

                # Aggregate STEP failure data per model
                fail_df = ldf[ldf['RESULT'] == 'N']
                for _, row in fail_df.iterrows():
                    model = str(row.get('MAT_NM', '알수없음'))
                    fs = lines_summary[line]["fail_steps"]
                    if model not in fs:
                        fs[model] = {}
                    for sc in step_cols:
                        val = str(row.get(sc, '')).strip()
                        if val and val not in ('', 'nan', ' '):
                            step_name = val.split(' ')[0] if ' ' in val else val
                            step_key = step_name[:30]
                            fs[model][step_key] = fs[model].get(step_key, 0) + 1

                if "hourly_trend" not in lines_summary[line]:
                    lines_summary[line]["hourly_trend"] = {}

                def get_time_slot(ct):
                    try:
                        # Assuming ct like 20260302080456 (YYYYMMDDHHMMSS)
                        ct_str = str(int(ct))
                        if len(ct_str) >= 14:
                            hour = int(ct_str[8:10])
                            minute = int(ct_str[10:12])
                            total_minutes = hour * 60 + minute
                            
                            # Custom intervals:
                            # A-1: 06:00 ~ 07:59
                            if 6*60 <= total_minutes < 8*60: return "A-1(06:00~07:59)"
                            # A: 08:00 ~ 10:00 (user specified 08:00~10:00, interpreting as 08:00~09:59 or inclusive of 10:00)
                            if 8*60 <= total_minutes <= 10*60: return "A(08:00~10:00)"
                            # B: 10:10 ~ 12:00
                            if 10*60 + 10 <= total_minutes <= 12*60: return "B(10:10~12:00)"
                            # C: 13:00 ~ 15:00
                            if 13*60 <= total_minutes <= 15*60: return "C(13:00~15:00)"
                            # D: 15:10 ~ 17:00
                            if 15*60 + 10 <= total_minutes <= 17*60: return "D(15:10~17:00)"
                            # E: 17:30 ~ 20:00
                            if 17*60 + 30 <= total_minutes <= 20*60: return "E(17:30~20:00)"
                            
                            return f"기타({hour:02d}:{minute:02d})"
                    except:
                        pass
                    return "기타"

                # Aggregate hourly trend per day
                if 'CREATE_TIME' in ldf.columns:
                    for _, row in ldf.iterrows():
                        slot = get_time_slot(row['CREATE_TIME'])
                        # If you want to skip '기타', you could do: if slot == '기타': continue 
                        date_slot = f"{display_sheet_name} {slot}"
                        ht = lines_summary[line]["hourly_trend"]
                        if date_slot not in ht:
                            ht[date_slot] = {"total": 0, "pass": 0, "fail": 0}
                        ht[date_slot]["total"] += 1
                        if str(row.get('RESULT', '')) == 'G': ht[date_slot]["pass"] += 1
                        else: ht[date_slot]["fail"] += 1

                lines_summary[line]["trend"].append({
                    "date": display_sheet_name,
                    "total": l_total,
                    "pass": int(l_g),
                    "fail": int(l_n),
                    "pass_rate": round((l_g / l_total * 100) if l_total > 0 else 0, 1)
                })

        def parse_korean_date_key(d_str):
            try:
                # "3월 10일" -> (3, 10)
                parts = d_str.replace("월", "").replace("일", "").split(" ")
                return (int(parts[0]), int(parts[1]))
            except:
                return (99, 99)

        # Finalize Daily Averages
        daily_averages = []
        for d in sorted(daily_averages_map.keys(), key=parse_korean_date_key):
            stats = daily_averages_map[d]
            daily_averages.append({
                "date": d,
                "pass_rate": round((stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0, 1)
            })

        def get_week_name(sheet_name):
            # Sheet names are MMDD like "0301"
            if not (len(sheet_name) == 4 and sheet_name.isdigit()):
                return "기타"
            day = int(sheet_name[2:])
            # 2026 March: 1(Sun) is Week 1, 8(Sun) is Week 2, etc.
            if day <= 7: return "Week 1 (3/1~)"
            if day <= 14: return "Week 2 (3/8~)"
            if day <= 21: return "Week 3 (3/15~)"
            if day <= 28: return "Week 4 (3/22~)"
            return "Week 5 (3/29~)"

        final_lines = []
        for lid in sorted(lines_summary.keys()):
            data = lines_summary[lid]
            data["models"] = sorted(list(data["models"]))
            data["pass_rate"] = round((data["pass"] / data["total"] * 100) if data["total"] > 0 else 0, 1)

            # Serialize fail_steps: {model: [{step, count}]} sorted by count desc
            fs_raw = data.pop("fail_steps", {})
            data["fail_steps"] = {}
            for model, steps in fs_raw.items():
                sorted_steps = sorted(steps.items(), key=lambda x: -x[1])
                data["fail_steps"][model] = [{"step": s, "count": c} for s, c in sorted_steps[:20]]

            # Finalize model_stats: compute pass_rate + attach worst1_step
            ms_raw = data.get("model_stats", {})
            data["model_stats"] = []
            for model_name in sorted(ms_raw.keys()):
                ms = ms_raw[model_name]
                pr = round((ms["pass"] / ms["total"] * 100) if ms["total"] > 0 else 0, 1)
                worst1 = ""
                if model_name in data["fail_steps"] and data["fail_steps"][model_name]:
                    worst1 = data["fail_steps"][model_name][0]["step"]
                data["model_stats"].append({
                    "name": model_name,
                    "total": ms["total"],
                    "pass": ms["pass"],
                    "fail": ms["fail"],
                    "pass_rate": pr,
                    "worst1_step": worst1
                })

            # Serialize hourly_trend
            ht_raw = data.pop("hourly_trend", {})
            ht_list = []
            for k, v in ht_raw.items():
                pr = round((v["pass"] / v["total"] * 100) if v["total"] > 0 else 0, 1)
                ht_list.append({
                    "time_slot": k,
                    "total": v["total"],
                    "pass": v["pass"],
                    "fail": v["fail"],
                    "pass_rate": pr
                })
            
            def parse_time_slot_key(k):
                try:
                    # Key looks like "3월 17일 A(08:00~10:00)" or "3월 17일 A-1(06:00~07:59)"
                    parts = k.split(' ')
                    m = int(parts[0].replace('월',''))
                    d = int(parts[1].replace('일',''))
                    slot_part = parts[2]
                    
                    slot_order = {
                        "A-1": 1, "A": 2, "B": 3, "C": 4, "D": 5, "E": 6
                    }
                    # Extract the slot name (A-1, A, B, etc.) before the bracket
                    slot_name = slot_part.split('(')[0]
                    order = slot_order.get(slot_name, 99)
                    
                    return (m, d, order)
                except:
                    return (99, 99, 99)
            
            ht_list.sort(key=lambda x: parse_time_slot_key(x['time_slot']))
            data["hourly_trend"] = ht_list

            # Weekly Trend Aggregation
            weekly_stats = {}
            for day_data in data["trend"]:
                # Map back from "M월 D일" or find index in original sheet names
                # Actually, it's easier to find the week during the main loop, 
                # but let's just use the day_data["date"] which is "M월 D일"
                try:
                    day_part = day_data["date"].split(" ")[1].replace("일", "")
                    day_int = int(day_part)
                    if day_int <= 7: w = "Week 1 (3/1~)"
                    elif day_int <= 14: w = "Week 2 (3/8~)"
                    elif day_int <= 21: w = "Week 3 (3/15~)"
                    elif day_int <= 28: w = "Week 4 (3/22~)"
                    else: w = "Week 5 (3/29~)"
                except:
                    w = "기타"

                if w not in weekly_stats:
                    weekly_stats[w] = {"total": 0, "pass": 0, "fail": 0, "days": []}
                weekly_stats[w]["total"] += day_data["total"]
                weekly_stats[w]["pass"] += day_data["pass"]
                weekly_stats[w]["fail"] += day_data["fail"]
                weekly_stats[w]["days"].append(day_data)

            data["weekly_trend"] = []
            for w in sorted(weekly_stats.keys()):
                ws = weekly_stats[w]
                data["weekly_trend"].append({
                    "week": w,
                    "total": ws["total"],
                    "pass": ws["pass"],
                    "fail": ws["fail"],
                    "pass_rate": round((ws["pass"] / ws["total"] * 100) if ws["total"] > 0 else 0, 1),
                    "days": ws["days"]
                })

            # Sort trend by date
            data["trend"].sort(key=lambda x: parse_korean_date_key(x["date"]))

            final_lines.append(data)

        final_data = {
            "overall": {
                "total": int(overall_total),
                "pass": int(overall_g),
                "fail": int(overall_n),
                "pass_rate": round((overall_g / (overall_g + overall_n) * 100) if (overall_g + overall_n) > 0 else 0, 1)
            },
            "daily_averages": daily_averages,
            "lines": final_lines
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        print(f"Data extraction successful. JSON saved to: {json_path}")
        
    except Exception as e:
        print(f"Error extracting data: {e}")

if __name__ == "__main__":
    process_file()
