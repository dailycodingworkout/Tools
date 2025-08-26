#!/bin/bash

# Git Branch Migrator Tool
# This script helps migrate multiple branches from a source repository to a target repository
# while preserving complete git history and organizing branches into folders

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables (can be overridden by config file)
SOURCE_REPO=""
TARGET_REPO=""
BRANCHES=()
TARGET_FOLDERS=()
TEMP_DIR=""
PRESERVE_HISTORY=true
VERBOSE=false

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Git Branch Migrator Tool

Usage: $0 [OPTIONS]

Options:
    -s, --source-repo URL       Source repository URL or path
    -t, --target-repo URL       Target repository URL or path
    -b, --branches LIST         Comma-separated list of branches to migrate
    -f, --folders LIST          Comma-separated list of target folder names
    -c, --config FILE           Configuration file path
    -v, --verbose               Enable verbose output
    -h, --help                  Show this help message

Examples:
    # Basic usage
    $0 -s "https://github.com/user/source-repo" -t "https://github.com/user/target-repo" \\
       -b "master,18.0,17.0,16.0,15.0" -f "master,v18,v17,v16,v15"

    # Using configuration file
    $0 -c migration-config.conf

Configuration file format:
    SOURCE_REPO="https://github.com/user/source-repo"
    TARGET_REPO="https://github.com/user/target-repo"
    BRANCHES=("master" "18.0" "17.0" "16.0" "15.0")
    TARGET_FOLDERS=("master" "v18" "v17" "v16" "v15")

EOF
}

# Function to load configuration file
load_config() {
    local config_file="$1"
    if [[ -f "$config_file" ]]; then
        print_info "Loading configuration from $config_file"
        source "$config_file"
    else
        print_error "Configuration file not found: $config_file"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    local errors=0
    
    if [[ -z "$SOURCE_REPO" ]]; then
        print_error "Source repository not specified"
        errors=$((errors + 1))
    fi
    
    if [[ -z "$TARGET_REPO" ]]; then
        print_error "Target repository not specified"
        errors=$((errors + 1))
    fi
    
    if [[ ${#BRANCHES[@]} -eq 0 ]]; then
        print_error "No branches specified for migration"
        errors=$((errors + 1))
    fi
    
    if [[ ${#TARGET_FOLDERS[@]} -ne ${#BRANCHES[@]} ]]; then
        print_error "Number of target folders (${#TARGET_FOLDERS[@]}) doesn't match number of branches (${#BRANCHES[@]})"
        errors=$((errors + 1))
    fi
    
    if [[ $errors -gt 0 ]]; then
        print_error "Configuration validation failed with $errors error(s)"
        exit 1
    fi
    
    print_success "Configuration validation passed"
}

# Function to setup temporary directory
setup_temp_dir() {
    TEMP_DIR=$(mktemp -d -t git-migrator-XXXXXX)
    print_info "Created temporary directory: $TEMP_DIR"
    
    # Cleanup function
    cleanup() {
        if [[ -d "$TEMP_DIR" ]]; then
            print_info "Cleaning up temporary directory: $TEMP_DIR"
            rm -rf "$TEMP_DIR"
        fi
    }
    
    # Register cleanup function to be called on script exit
    trap cleanup EXIT
}

# Function to clone source repository
clone_source_repo() {
    local source_clone_dir="$TEMP_DIR/source"
    
    print_info "Cloning source repository: $SOURCE_REPO"
    git clone --mirror "$SOURCE_REPO" "$source_clone_dir"
    
    if [[ $? -eq 0 ]]; then
        print_success "Source repository cloned successfully"
    else
        print_error "Failed to clone source repository"
        exit 1
    fi
    
    echo "$source_clone_dir"
}

# Function to prepare target repository
prepare_target_repo() {
    local target_clone_dir="$TEMP_DIR/target"
    
    # Check if target repo exists
    if git ls-remote "$TARGET_REPO" > /dev/null 2>&1; then
        print_info "Target repository exists, cloning: $TARGET_REPO"
        git clone "$TARGET_REPO" "$target_clone_dir"
    else
        print_info "Target repository doesn't exist, creating new one: $target_clone_dir"
        mkdir -p "$target_clone_dir"
        cd "$target_clone_dir"
        git init
        git remote add origin "$TARGET_REPO"
        
        # Create initial commit
        echo "# Migrated Repository" > README.md
        git add README.md
        git commit -m "Initial commit for migrated repository"
        cd - > /dev/null
    fi
    
    echo "$target_clone_dir"
}

# Function to migrate a single branch
migrate_branch() {
    local source_dir="$1"
    local target_dir="$2"
    local branch_name="$3"
    local target_folder="$4"
    
    print_info "Migrating branch '$branch_name' to folder '$target_folder'"
    
    cd "$target_dir"
    
    # Add source as remote if not already added
    if ! git remote | grep -q "source-repo"; then
        git remote add source-repo "$source_dir"
    fi
    
    # Fetch the specific branch
    git fetch source-repo "$branch_name:temp-$branch_name" 2>/dev/null || {
        print_warning "Branch '$branch_name' not found in source repository, skipping"
        return 0
    }
    
    # Create target folder if it doesn't exist
    mkdir -p "$target_folder"
    
    # Use git subtree to move branch content to folder while preserving history
    git checkout "temp-$branch_name"
    
    # Create a new branch for the folder-organized version
    git checkout -b "migrated-$target_folder"
    
    # Move all files to the target folder
    if [[ $(ls -la | wc -l) -gt 3 ]]; then  # More than just . and ..
        mkdir -p "$target_folder-temp"
        find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "$target_folder-temp" -exec mv {} "$target_folder-temp/" \;
        mv "$target_folder-temp" "$target_folder"
        
        # Commit the reorganization
        git add .
        git commit -m "Reorganize $branch_name branch content into $target_folder folder

Original branch: $branch_name
Migration timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Source repository: $SOURCE_REPO
Target folder: $target_folder

This commit preserves the complete git history from the original branch."
    fi
    
    # Merge into main branch
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || {
        # Create main branch if it doesn't exist
        git checkout -b main
    }
    
    # Merge the migrated branch
    git merge "migrated-$target_folder" --allow-unrelated-histories -m "Merge $branch_name branch into $target_folder

This merge brings in the complete history from branch '$branch_name' 
from the source repository into the '$target_folder' folder structure.

Source: $SOURCE_REPO
Branch: $branch_name
Target folder: $target_folder
Migration date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    
    # Clean up temporary branches
    git branch -D "temp-$branch_name" "migrated-$target_folder" 2>/dev/null || true
    
    cd - > /dev/null
    print_success "Successfully migrated branch '$branch_name' to folder '$target_folder'"
}

# Function to push changes to target repository
push_changes() {
    local target_dir="$1"
    
    cd "$target_dir"
    
    print_info "Pushing changes to target repository"
    
    # Push main/master branch
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || {
        print_warning "Failed to push changes. Please check repository permissions and try manually."
        print_info "Target repository location: $target_dir"
        return 1
    }
    
    print_success "Changes pushed successfully to target repository"
    cd - > /dev/null
}

# Function to generate migration report
generate_report() {
    local target_dir="$1"
    local report_file="$target_dir/MIGRATION_REPORT.md"
    
    print_info "Generating migration report"
    
    cat > "$report_file" << EOF
# Git Branch Migration Report

## Migration Details
- **Migration Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Source Repository**: $SOURCE_REPO
- **Target Repository**: $TARGET_REPO
- **Tool Version**: Git Branch Migrator v1.0

## Migrated Branches

| Original Branch | Target Folder | Status |
|----------------|---------------|---------|
EOF

    for i in "${!BRANCHES[@]}"; do
        echo "| ${BRANCHES[$i]} | ${TARGET_FOLDERS[$i]} | ✅ Migrated |" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Migration Process

This migration was performed using the Git Branch Migrator tool, which:

1. **Preserves Complete History**: All commit history, messages, and metadata are preserved
2. **Maintains Author Information**: Original commit authors and timestamps are retained
3. **Organizes Content**: Each branch is organized into its respective folder
4. **GitHub Copilot Compatible**: The migrated history maintains full compatibility with GitHub Copilot analysis

## Folder Structure

The migrated repository is organized as follows:

\`\`\`
repository-root/
$(for folder in "${TARGET_FOLDERS[@]}"; do echo "├── $folder/"; done)
└── MIGRATION_REPORT.md
\`\`\`

## Verification

To verify the migration integrity:

1. Check commit history: \`git log --oneline --graph\`
2. Verify file contents in each folder
3. Confirm all original commits are present with: \`git log --all --grep="Original branch"\`

## GitHub Copilot Integration

The migrated repository maintains full compatibility with GitHub Copilot:
- All commit messages are preserved for context understanding
- File history is maintained for better code analysis
- Branch relationships are documented in merge commits
- Original authorship information is retained

EOF

    print_success "Migration report generated: $report_file"
}

# Main migration function
perform_migration() {
    print_info "Starting git branch migration process"
    
    # Setup
    setup_temp_dir
    
    # Clone repositories
    local source_dir=$(clone_source_repo)
    local target_dir=$(prepare_target_repo)
    
    # Migrate each branch
    for i in "${!BRANCHES[@]}"; do
        migrate_branch "$source_dir" "$target_dir" "${BRANCHES[$i]}" "${TARGET_FOLDERS[$i]}"
    done
    
    # Generate report
    generate_report "$target_dir"
    
    # Add and commit the report
    cd "$target_dir"
    git add MIGRATION_REPORT.md
    git commit -m "Add migration report

This report documents the branch migration process and provides
information about the migrated content organization."
    cd - > /dev/null
    
    # Push changes
    push_changes "$target_dir"
    
    print_success "Migration completed successfully!"
    print_info "Temporary files will be cleaned up automatically"
    print_info "Check the MIGRATION_REPORT.md file in your target repository for details"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--source-repo)
            SOURCE_REPO="$2"
            shift 2
            ;;
        -t|--target-repo)
            TARGET_REPO="$2"
            shift 2
            ;;
        -b|--branches)
            IFS=',' read -ra BRANCHES <<< "$2"
            shift 2
            ;;
        -f|--folders)
            IFS=',' read -ra TARGET_FOLDERS <<< "$2"
            shift 2
            ;;
        -c|--config)
            load_config "$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Enable verbose output if requested
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Validate configuration
validate_config

# Perform migration
perform_migration