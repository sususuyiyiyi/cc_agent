#!/bin/bash

# Auto-commit script for CC Agent
# This script automatically commits and pushes changes when they are detected

set -e

echo "🔄 Auto-commit script running..."

# Check if there are changes
if ! git diff-index --quiet HEAD --; then
    echo "📝 Changes detected, committing..."

    # Stage all changes
    git add .

    # Create a commit with a descriptive message
    git commit -m "$(cat <<'EOF'
Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')

- Auto-commit feature enabled
- Changes detected and committed

Co-Authored-By: susu <lsynina0210@gmail.com>
EOF
)"

    echo "✅ Changes committed successfully"

    # Check if remote exists
    if git remote | grep -q "^origin$"; then
        echo "🚀 Pushing to remote..."
        git push
        echo "✅ Changes pushed to remote"
    else
        echo "⚠️ No remote configured, skipping push"
    fi
else
    echo "ℹ️ No changes to commit"
fi