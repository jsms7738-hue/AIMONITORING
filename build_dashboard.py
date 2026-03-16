
import json
import os

def build():
    try:
        base_dir = r"c:\Users\yoonh\Desktop\AI\ICT데이타"
        template_path = os.path.join(base_dir, "dashboard_template.html")
        data_path = r"C:\Users\yoonh\.gemini\antigravity\brain\26c13193-f223-4e18-949a-d50e3d670777\data.json"
        output_path = os.path.join(base_dir, "dashboard.html")

        print(f"Loading template from: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        print(f"Loading data from: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            data_json = f.read()
            # Validate JSON
            json.loads(data_json)

        print("Merging data into template as direct JS assignment...")
        # Inject data as a direct JS assignment
        data_injection = f"const rawData = {data_json};"
        output = template.replace("// DATA_INJECTION_PLACEHOLDER", data_injection)

        print(f"Saving final dashboard to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

        print("Dashboard build successful!")
    except Exception as e:
        print(f"Build failed: {e}")

if __name__ == "__main__":
    build()
