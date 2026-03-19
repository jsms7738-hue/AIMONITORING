import json
import os

def build():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "dashboard_template.html")
        json_dir = os.path.join(base_dir, "data")
        json_path = os.path.join(json_dir, "data.json")

        if not os.path.exists(template_path):
            print(f"Template not found at: {template_path}")
            return
        if not os.path.exists(json_path):
            print(f"Data JSON not found at: {json_path}")
            return

        print(f"Reading template from: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        print(f"Reading data from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_json = json.dumps(data, ensure_ascii=False)

        # Get all line IDs
        all_line_ids = sorted([str(line['line_id']) for line in data['lines']])
        print(f"Detected lines: {all_line_ids}")

        # 1. Generate main dashboard.html (Overview)
        print("Generating dashboard.html (Overview)")
        context_overview = f"const activeLineId = null;\nconst allLineIds = {json.dumps(all_line_ids)};"
        output_overview = template.replace("// DATA_INJECTION_PLACEHOLDER", f"const rawData = {data_json};")
        output_overview = output_overview.replace("// CONTEXT_INJECTION_PLACEHOLDER", context_overview)
        
        overview_path = os.path.join(base_dir, "dashboard.html")
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(output_overview)

        # 2. Generate dashboard_LINE.html for each line
        for line_id in all_line_ids:
            print(f"Generating dashboard_{line_id}.html (Deep-Dive)")
            context_line = f"const activeLineId = '{line_id}';\nconst allLineIds = {json.dumps(all_line_ids)};"
            output_line = template.replace("// DATA_INJECTION_PLACEHOLDER", f"const rawData = {data_json};")
            output_line = output_line.replace("// CONTEXT_INJECTION_PLACEHOLDER", context_line)
            
            line_path = os.path.join(base_dir, f"dashboard_{line_id}.html")
            with open(line_path, 'w', encoding='utf-8') as f:
                f.write(output_line)

        print(f"\nDashboard build successful! Total files created: {len(all_line_ids) + 1}")
    except Exception as e:
        print(f"Build failed: {e}")

if __name__ == "__main__":
    build()
