import pandas as pd
import json
import os

# Get the directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "3월데이타 ICT.xlsx")
output_dir = r"C:\Users\yoonh\.gemini\antigravity\brain\69bb9edf-8aaa-4b06-9beb-1982cfe6f16c"
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
                        "trend": []
                    }
                
                lines_summary[line]["total"] += l_total
                lines_summary[line]["pass"] += int(l_g)
                lines_summary[line]["fail"] += int(l_n)
                for m in l_models: lines_summary[line]["models"].add(str(m))
                
                lines_summary[line]["trend"].append({
                    "date": display_sheet_name,
                    "total": l_total,
                    "pass": int(l_g),
                    "fail": int(l_n),
                    "pass_rate": round((l_g / l_total * 100) if l_total > 0 else 0, 1)
                })

        # Finalize Daily Averages
        daily_averages = []
        for d in sorted(daily_averages_map.keys()):
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

        # Process lines
        final_lines = []
        for lid in sorted(lines_summary.keys()):
            data = lines_summary[lid]
            data["models"] = sorted(list(data["models"]))
            data["pass_rate"] = round((data["pass"] / data["total"] * 100) if data["total"] > 0 else 0, 1)
            
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
