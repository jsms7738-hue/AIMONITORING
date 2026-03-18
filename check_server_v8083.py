import urllib.request
try:
    with urllib.request.urlopen('http://localhost:8083/smps_dashboard.html', timeout=5) as response:
        print(f"Status Code: {response.getcode()}")
        content = response.read().decode('utf-8')
        print(f"Content Length: {len(content)}")
        if "type: 'bar'" in content:
            print("Found 'type: bar' in mini charts section!")
        else:
            print("FAILED: 'type: bar' NOT found.")
except Exception as e:
    print(f"Error: {e}")
