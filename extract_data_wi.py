import pandas as pd
import json
import os

# Get the directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "3월데이타 WI.xlsx")
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

        # Overall failure details aggregation
        overall_fail_details = {"models": {}, "steps": {}}
        
        for sheet in sheet_names:
            
            print(f"Processing sheet: {sheet}")
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

            # Overall failure aggregation
            if 'RESULT' in df.columns and total_rows > g_count:
                nf_overall = df[df['RESULT'] == 'N']
                for _, f_row in nf_overall.iterrows():
                    m_name = str(f_row.get('MAT_NM', 'Unknown'))
                    overall_fail_details["models"][m_name] = overall_fail_details["models"].get(m_name, 0) + 1
                    
                    for i in range(1, 11):
                        cid_col = f'CHAR_ID_{i:02d}'
                        if cid_col in f_row and pd.notna(f_row[cid_col]):
                            step_name = str(f_row[cid_col])
                            overall_fail_details["steps"][step_name] = overall_fail_details["steps"].get(step_name, 0) + 1
            
            if 'LINE_ID' not in df.columns:
                continue

            unique_lines = df['LINE_ID'].dropna().unique()

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

                if "hourly_trend" not in lines_summary[line]:
                    lines_summary[line]["hourly_trend"] = {}

                def get_time_slot(ct):
                    try:
                        ct_str = str(int(ct))
                        if len(ct_str) >= 10: # Assuming at least MMDDHHMMSS
                            # Format could be YYYYMMDDHHMMSS
                            if len(ct_str) >= 14:
                                hour = int(ct_str[8:10])
                                minute = int(ct_str[10:12])
                            else:
                                # For shorter strings, adjust logic if needed
                                hour = int(ct_str[-6:-4])
                                minute = int(ct_str[-4:-2])
                                
                            total_minutes = hour * 60 + minute
                            
                            if 6*60 <= total_minutes < 8*60: return "A-1(06:00~07:59)"
                            if 8*60 <= total_minutes <= 10*60: return "A(08:00~10:00)"
                            if 10*60 + 10 <= total_minutes <= 12*60: return "B(10:10~12:00)"
                            if 13*60 <= total_minutes <= 15*60: return "C(13:00~15:00)"
                            if 15*60 + 10 <= total_minutes <= 17*60: return "D(15:10~17:00)"
                            if 17*60 + 30 <= total_minutes <= 20*60: return "E(17:30~20:00)"
                            
                            return f"기타({hour:02d}:{minute:02d})"
                    except:
                        pass
                    return "기타"

                # Aggregate hourly trend per day
                time_col = 'TRAN_TIME' if 'TRAN_TIME' in ldf.columns else ('CREATE_TIME' if 'CREATE_TIME' in ldf.columns else None)
                if time_col:
                    for _, row in ldf.iterrows():
                        slot = get_time_slot(row[time_col])
                        date_slot = f"{display_sheet_name} {slot}"
                        ht = lines_summary[line]["hourly_trend"]
                        if date_slot not in ht:
                            ht[date_slot] = {"total": 0, "pass": 0, "fail": 0}
                        ht[date_slot]["total"] += 1
                        if str(row.get('RESULT', '')) == 'G': ht[date_slot]["pass"] += 1
                        else: ht[date_slot]["fail"] += 1

                # Failure details for this line on this day
                l_fail_details = {"models": {}, "steps": {}}
                if l_n > 0:
                    nf = ldf[ldf['RESULT'] == 'N']
                    for _, f_row in nf.iterrows():
                        m_name = str(f_row.get('MAT_NM', 'Unknown'))
                        l_fail_details["models"][m_name] = l_fail_details["models"].get(m_name, 0) + 1
                        
                        # WI data has CHAR_ID_01 to CHAR_ID_10
                        for i in range(1, 11):
                            cid_col = f'CHAR_ID_{i:02d}'
                            val_col = f'VALUE_{i:02d}'
                            if cid_col in f_row and pd.notna(f_row[cid_col]):
                                step_name = str(f_row[cid_col])
                                l_fail_details["steps"][step_name] = l_fail_details["steps"].get(step_name, 0) + 1

                lines_summary[line]["trend"].append({
                    "date": display_sheet_name,
                    "total": l_total,
                    "pass": int(l_g),
                    "fail": int(l_n),
                    "pass_rate": round((l_g / l_total * 100) if l_total > 0 else 0, 1),
                    "fail_details": {
                        "models": l_fail_details["models"],
                        "steps": dict(sorted(l_fail_details["steps"].items(), key=lambda x: x[1], reverse=True)[:10]) # Top 10 fail steps
                    }
                })

        def parse_korean_date_key(d_str):
            try:
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

        final_lines = []
        for lid in sorted(lines_summary.keys()):
            data = lines_summary[lid]
            data["models"] = sorted(list(data["models"]))
            data["pass_rate"] = round((data["pass"] / data["total"] * 100) if data["total"] > 0 else 0, 1)

            # Finalize model_stats
            ms_raw = data.get("model_stats", {})
            data["model_stats"] = []
            for model_name in sorted(ms_raw.keys()):
                ms = ms_raw[model_name]
                pr = round((ms["pass"] / ms["total"] * 100) if ms["total"] > 0 else 0, 1)
                data["model_stats"].append({
                    "name": model_name,
                    "total": ms["total"],
                    "pass": ms["pass"],
                    "fail": ms["fail"],
                    "pass_rate": pr,
                    "worst1_step": ""
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
                    parts = k.split(' ')
                    m = int(parts[0].replace('월',''))
                    d = int(parts[1].replace('일',''))
                    slot_part = parts[2]
                    slot_order = {"A-1": 1, "A": 2, "B": 3, "C": 4, "D": 5, "E": 6}
                    slot_name = slot_part.split('(')[0]
                    order = slot_order.get(slot_name, 99)
                    return (m, d, order)
                except:
                    return (99, 99, 99)
            
            ht_list.sort(key=lambda x: parse_time_slot_key(x['time_slot']))
            data["hourly_trend"] = ht_list

            # Weekly Trend
            weekly_stats = {}
            for day_data in data["trend"]:
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

            data["trend"].sort(key=lambda x: parse_korean_date_key(x["date"]))
            final_lines.append(data)

        final_data = {
            "overall": {
                "total": int(overall_total),
                "pass": int(overall_g),
                "fail": int(overall_n),
                "pass_rate": round((overall_g / (overall_g + overall_n) * 100) if (overall_g + overall_n) > 0 else 0, 1),
                "fail_details": {
                    "models": overall_fail_details["models"],
                    "steps": dict(sorted(overall_fail_details["steps"].items(), key=lambda x: x[1], reverse=True)[:20]) # Top 20 overall
                }
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
