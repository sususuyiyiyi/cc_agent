#!/usr/bin/env python3
"""
Auto-commit monitor for CC Agent
Monitors for file changes and auto-commits them
"""

import os
import time
import subprocess
from pathlib import Path
import hashlib

class AutoCommitMonitor:
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.last_hash = self.get_current_hash()

    def get_current_hash(self):
        """Get hash of all tracked files"""
        # Get all tracked files in git
        result = subprocess.run(['git', 'ls-files'],
                              capture_output=True, text=True)
        tracked_files = result.stdout.strip().split('\n') if result.stdout else []

        # Calculate hash
        hash_md5 = hashlib.md5()
        for file_path in tracked_files:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    hash_md5.update(f.read())

        return hash_md5.hexdigest()

    def has_changes(self):
        """Check if there are uncommitted changes"""
        result = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True)
        return bool(result.stdout.strip())

    def auto_commit(self):
        """Perform auto-commit"""
        print(f"⏰ Auto-commit check at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        current_hash = self.get_current_hash()

        if current_hash != self.last_hash:
            print("📝 Changes detected, committing...")

            # Run the auto-commit script
            result = subprocess.run(['./auto_commit.sh'],
                                 capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Auto-commit successful")
                self.last_hash = current_hash
            else:
                print(f"❌ Auto-commit failed: {result.stderr}")
        else:
            print("ℹ️ No changes detected")

    def run(self):
        """Run the monitor"""
        print(f"🚀 Auto-commit monitor started (checking every {self.check_interval}s)")
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.auto_commit()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n👋 Auto-commit monitor stopped")

if __name__ == "__main__":
    monitor = AutoCommitMonitor()
    monitor.run()