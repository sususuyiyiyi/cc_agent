#!/usr/bin/env python3
"""
Final auto-commit monitor for CC Agent
"""

import subprocess
import time
import os
from datetime import datetime

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def has_changes():
    """Check if there are uncommitted changes"""
    success, stdout, stderr = run_command(['git', 'status', '--porcelain'])
    if success:
        return bool(stdout.strip())
    return False

def auto_commit():
    """Perform auto-commit"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-commit triggered")

    # Stage all changes
    success, stdout, stderr = run_command(['git', 'add', '.'])
    if not success:
        print(f"❌ Failed to stage changes: {stderr}")
        return False

    # Commit
    commit_msg = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    success, stdout, stderr = run_command(['git', 'commit', '-m', commit_msg])
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return False

    print(f"✅ Committed successfully")

    # Push if remote exists
    success, _, _ = run_command(['git', 'remote', 'get', 'origin'])
    if success:
        success, stdout, stderr = run_command(['git', 'push'])
        if success:
            print(f"✅ Pushed successfully")
        else:
            print(f"⚠️ Push failed: {stderr}")

    return True

def main():
    # Check if we're in a git repo
    success, _, _ = run_command(['git', 'rev-parse', '--is-inside-work-tree'])
    if not success:
        print("❌ Not in a git repository")
        return

    print("🚀 Auto-commit monitor started")
    print("Checking for changes every 60 seconds...")
    print("Press Ctrl+C to stop")

    # Log file
    log_file = "logs/auto_commit_final.log"

    while True:
        try:
            if has_changes():
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Changes detected")

                # Write to log file
                with open(log_file, 'a') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-commit triggered\n")

                # Perform auto-commit
                if auto_commit():
                    with open(log_file, 'a') as f:
                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-commit successful\n")
                else:
                    with open(log_file, 'a') as f:
                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-commit failed\n")
            else:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No changes\n")

            time.sleep(60)

        except KeyboardInterrupt:
            print("\n👋 Auto-commit monitor stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()