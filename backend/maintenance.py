import os
import shutil
import json
from datetime import datetime

def perform_maintenance():
    base_dir = r"d:\KMT\My class\AI\AI-Aero-Playwright-Gen"
    backend_dir = os.path.join(base_dir, "backend")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(base_dir, "backups", timestamp)
    
    os.makedirs(backup_root, exist_ok=True)
    print(f"Created backup directory: {backup_root}")

    # 1. Backup and Cleanup Directories
    targets = [
        os.path.join(base_dir, "tests_web"),
        os.path.join(base_dir, "reports"),
        os.path.join(backend_dir, "test_plans")
    ]

    for target in targets:
        if os.path.exists(target):
            dest = os.path.join(backup_root, os.path.basename(target))
            os.makedirs(dest, exist_ok=True)
            print(f"Backing up: {target} -> {dest}")
            
            for item in os.listdir(target):
                s = os.path.join(target, item)
                d = os.path.join(dest, item)
                if os.path.isfile(s):
                    shutil.move(s, d)
                elif os.path.isdir(s):
                    shutil.move(s, d)
            print(f"Cleaned up: {target}")
        else:
            print(f"Target does not exist: {target}")

    # 2. Reset Token Usage in usage_stats.json
    usage_file = os.path.join(backend_dir, "usage_stats.json")
    if os.path.exists(usage_file):
        with open(usage_file, 'r') as f:
            stats = json.load(f)
        
        stats['total_tokens'] = 0
        stats['date'] = datetime.now().strftime("%Y-%m-%d")
        
        with open(usage_file, 'w') as f:
            json.dump(stats, f)
        print(f"Reset token usage in {usage_file}")

if __name__ == "__main__":
    perform_maintenance()
