import os
import shutil
import re
from datetime import datetime

def get_next_rev(backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        return "REV01"
    
    rev_dirs = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d)) and re.match(r'REV\d+', d)]
    if not rev_dirs:
        return "REV01"
    
    rev_numbers = [int(re.search(r'\d+', d).group()) for d in rev_dirs]
    next_num = max(rev_numbers) + 1
    return f"REV{next_num:02d}"

def create_backup():
    # Source directory (current directory)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # Backup base directory
    backup_base = os.path.join(src_dir, "backups")
    
    # Determine next REV
    rev_name = get_next_rev(backup_base)
    target_dir = os.path.join(backup_base, rev_name)
    
    print(f"Creating backup: {rev_name}...")
    
    # Files/Dirs to exclude from backup (matches .gitignore logic)
    exclude_patterns = [
        'backups', '__pycache__', '.git', '.vscode', '.idea', 'venv', 'env', 'build', 'dist'
    ]
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    for item in os.listdir(src_dir):
        if item in exclude_patterns:
            continue
            
        src_path = os.path.join(src_dir, item)
        target_path = os.path.join(target_dir, item)
        
        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, target_path)
            else:
                shutil.copy2(src_path, target_path)
        except Exception as e:
            print(f"Error copying {item}: {e}")

    # Create a simple info file
    with open(os.path.join(target_dir, "backup_info.txt"), "w", encoding="utf-8") as f:
        f.write(f"Backup Name: {rev_name}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Files backed up successfully.\n")

    print(f"Backup completed successfully in {target_dir}")

if __name__ == "__main__":
    create_backup()
