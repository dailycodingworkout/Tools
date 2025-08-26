# Git Branch Migration Guide

This guide helps you migrate multiple branches from a source repository to your personal repository while preserving complete git history and organizing content into folders.

## Overview

The Git Branch Migrator tool allows you to:
- Copy multiple branches from a remote repository to your personal repository
- Preserve complete git history, commit messages, and author information
- Organize branches into separate folders for better structure
- Maintain GitHub Copilot compatibility for code analysis
- Generate detailed migration reports

## Quick Start

### Step 1: Configure the Migration

Edit the `migration-config.conf` file with your specific details:

```bash
# Your source repository (the one you want to copy from)
SOURCE_REPO="https://github.com/username/doo.git"

# Your target repository (where you want to copy to)
TARGET_REPO="https://github.com/yourusername/base.git"

# Branches to migrate
BRANCHES=("master" "18.0" "17.0" "16.0" "15.0")

# Target folder names
TARGET_FOLDERS=("master" "v18" "v17" "v16" "v15")
```

### Step 2: Run the Migration

```bash
# Make the script executable
chmod +x git-branch-migrator.sh

# Run the migration
./git-branch-migrator.sh -c migration-config.conf
```

## Detailed Usage

### Command Line Options

```bash
./git-branch-migrator.sh [OPTIONS]

Options:
  -s, --source-repo URL       Source repository URL or path
  -t, --target-repo URL       Target repository URL or path
  -b, --branches LIST         Comma-separated list of branches to migrate
  -f, --folders LIST          Comma-separated list of target folder names
  -c, --config FILE           Configuration file path
  -v, --verbose               Enable verbose output
  -h, --help                  Show help message
```

### Examples

#### Using Command Line Arguments
```bash
./git-branch-migrator.sh \
  -s "https://github.com/username/doo.git" \
  -t "https://github.com/yourusername/base.git" \
  -b "master,18.0,17.0,16.0,15.0" \
  -f "master,v18,v17,v16,v15"
```

#### Using Configuration File (Recommended)
```bash
./git-branch-migrator.sh -c migration-config.conf
```

#### Verbose Output
```bash
./git-branch-migrator.sh -c migration-config.conf -v
```

## What the Tool Does

### 1. Repository Setup
- Creates a temporary working directory
- Clones the source repository with full history
- Prepares the target repository (creates if it doesn't exist)

### 2. Branch Migration
For each branch specified:
- Fetches the branch from the source repository
- Creates a new folder structure in the target repository
- Moves all branch content into the designated folder
- Preserves complete git history and commit messages
- Creates descriptive merge commits with migration metadata

### 3. History Preservation
- All original commit messages are preserved
- Author information and timestamps are maintained
- Branch relationships are documented
- GitHub Copilot can analyze the complete history

### 4. Final Organization
- Generates a comprehensive migration report
- Pushes all changes to the target repository
- Cleans up temporary files

## Result Structure

After migration, your target repository will have this structure:

```
your-base-repo/
├── master/
│   └── (all files from master branch)
├── v18/
│   └── (all files from 18.0 branch)
├── v17/
│   └── (all files from 17.0 branch)
├── v16/
│   └── (all files from 16.0 branch)
├── v15/
│   └── (all files from 15.0 branch)
├── MIGRATION_REPORT.md
└── README.md
```

## GitHub Copilot Compatibility

The migrated repository maintains full GitHub Copilot compatibility:

- **Complete History**: All commit messages are preserved for context understanding
- **Author Information**: Original authorship is maintained for better analysis
- **File Relationships**: Git history shows how files evolved across versions
- **Commit Context**: Merge commits provide clear migration documentation

## Verification

After migration, verify the results:

### Check Overall History
```bash
git log --oneline --graph --all
```

### Verify Specific Folder Content
```bash
# Check files in a specific version folder
ls -la v18/

# Check commit history for a specific folder
git log --oneline -- v18/
```

### Verify Migration Integrity
```bash
# Find all migration-related commits
git log --grep="Migration timestamp"

# Check that all original commits are present
git log --all --oneline | wc -l
```

## Troubleshooting

### Common Issues

#### 1. Authentication Problems
If you get authentication errors:
```bash
# For HTTPS repositories, ensure you have proper credentials
git config --global credential.helper store

# For SSH repositories, ensure your SSH keys are configured
ssh -T git@github.com
```

#### 2. Large Repository Timeouts
For very large repositories:
```bash
# Increase git timeout settings
git config --global http.lowSpeedTime 600
git config --global http.lowSpeedLimit 0
```

#### 3. Branch Not Found
If a branch doesn't exist in the source repository:
- The tool will skip it and continue with other branches
- Check the branch name spelling in your configuration
- Verify the branch exists: `git ls-remote origin`

### Getting Help

If you encounter issues:
1. Run with verbose output: `-v` flag
2. Check the generated migration report
3. Verify repository URLs and permissions
4. Ensure you have git version 2.9+ for best compatibility

## Advanced Configuration

### Custom Folder Structure
You can customize the folder organization:

```bash
# Example: Organize by feature instead of version
BRANCHES=("master" "feature-auth" "feature-api" "bugfix-security")
TARGET_FOLDERS=("core" "authentication" "api" "security-fixes")
```

### Selective File Migration
For more complex scenarios, you might want to modify the script to:
- Migrate only specific file types
- Apply custom file transformations
- Merge multiple branches into single folders

## Best Practices

1. **Backup First**: Always backup your target repository before migration
2. **Test with Small Sets**: Start with 1-2 branches to test the process
3. **Verify Permissions**: Ensure you have read access to source and write access to target
4. **Check Repository Size**: Large repositories may take considerable time
5. **Review Migration Report**: Always check the generated report for completeness

## Security Considerations

- The tool creates temporary directories that are automatically cleaned up
- Repository credentials are handled by git's standard authentication
- No sensitive information is logged or stored permanently
- All operations use standard git commands for maximum security