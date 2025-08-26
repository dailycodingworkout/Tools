#!/bin/bash

# Demo Script for Git Branch Migrator
# This script demonstrates how to use the git branch migration tool

echo "=== Git Branch Migrator Demo ==="
echo
echo "This demo shows how to migrate branches from a 'doo' repository to a 'base' repository"
echo "with complete history preservation and GitHub Copilot compatibility."
echo

# Check if tools exist
if [[ ! -f "git-branch-migrator.sh" ]]; then
    echo "❌ git-branch-migrator.sh not found in current directory"
    exit 1
fi

if [[ ! -f "validate-migration.sh" ]]; then
    echo "❌ validate-migration.sh not found in current directory"
    exit 1
fi

echo "✅ Migration tools found"
echo

# Show configuration example
echo "📋 Step 1: Configuration"
echo "Before migration, edit your configuration file:"
echo
cat << 'EOF'
# example-doo-to-base.conf
SOURCE_REPO="https://github.com/username/doo.git"
TARGET_REPO="https://github.com/yourusername/base.git"
BRANCHES=("master" "18.0" "17.0" "16.0" "15.0")
TARGET_FOLDERS=("master" "v18" "v17" "v16" "v15")
EOF
echo

# Show migration command
echo "🚀 Step 2: Run Migration"
echo "Execute the migration with:"
echo
echo "  ./git-branch-migrator.sh -c example-doo-to-base.conf"
echo

# Show what happens during migration
echo "⚙️  Step 3: Migration Process"
echo "The tool will:"
echo "  1. Clone source repository 'doo' with full history"
echo "  2. Prepare target repository 'base'"
echo "  3. For each branch (master, 18.0, 17.0, 16.0, 15.0):"
echo "     - Fetch branch with complete history"
echo "     - Create corresponding folder (master, v18, v17, v16, v15)"
echo "     - Move all content to the folder"
echo "     - Preserve all commit messages and author info"
echo "  4. Generate migration report"
echo "  5. Push everything to your 'base' repository"
echo

# Show expected result
echo "📁 Step 4: Expected Result"
echo "Your 'base' repository will have this structure:"
echo
echo "  base/"
echo "  ├── master/           # All files from master branch"
echo "  ├── v18/              # All files from 18.0 branch"
echo "  ├── v17/              # All files from 17.0 branch"
echo "  ├── v16/              # All files from 16.0 branch"
echo "  ├── v15/              # All files from 15.0 branch"
echo "  ├── MIGRATION_REPORT.md"
echo "  └── README.md"
echo

# Show validation
echo "✅ Step 5: Validation"
echo "Validate your migration with:"
echo
echo "  ./validate-migration.sh -r /path/to/base/repository"
echo

# Show GitHub Copilot benefits
echo "🤖 Step 6: GitHub Copilot Benefits"
echo "After migration, GitHub Copilot will be able to:"
echo "  • Understand the complete development history"
echo "  • Analyze code evolution across versions"
echo "  • Provide context-aware suggestions based on all commits"
echo "  • Access commit messages for better understanding"
echo "  • See relationships between different versions"
echo

# Show help commands
echo "📚 Additional Help"
echo "  • Migration help:   ./git-branch-migrator.sh --help"
echo "  • Validation help:  ./validate-migration.sh --help"
echo "  • Full guide:       cat MIGRATION_GUIDE.md"
echo

echo "=== Demo Complete ==="
echo
echo "To perform your actual migration:"
echo "1. Edit 'example-doo-to-base.conf' with your real repository URLs"
echo "2. Ensure you have access to both repositories"
echo "3. Run: ./git-branch-migrator.sh -c example-doo-to-base.conf"