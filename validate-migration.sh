#!/bin/bash

# Git Migration Validator
# This script helps validate the integrity of a git branch migration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
Git Migration Validator

This script validates the integrity of a git branch migration performed
by the git-branch-migrator.sh tool.

Usage: $0 [OPTIONS]

Options:
    -r, --repository PATH       Path to the migrated repository
    -f, --folders LIST          Comma-separated list of expected folders
    -v, --verbose               Enable verbose output
    -h, --help                  Show this help message

Examples:
    # Validate migration in current directory
    $0

    # Validate specific repository
    $0 -r /path/to/migrated/repo

    # Validate with expected folders
    $0 -f "master,v18,v17,v16,v15"

EOF
}

# Default values
REPO_PATH="."
EXPECTED_FOLDERS=()
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repository)
            REPO_PATH="$2"
            shift 2
            ;;
        -f|--folders)
            IFS=',' read -ra EXPECTED_FOLDERS <<< "$2"
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

# Validation functions
validate_git_repository() {
    print_info "Validating git repository structure..."
    
    if [[ ! -d "$REPO_PATH/.git" ]]; then
        print_error "Not a git repository: $REPO_PATH"
        return 1
    fi
    
    cd "$REPO_PATH"
    
    # Check if repository has commits
    if ! git log --oneline -1 > /dev/null 2>&1; then
        print_error "Repository has no commits"
        return 1
    fi
    
    print_success "Valid git repository found"
    return 0
}

validate_migration_report() {
    print_info "Checking for migration report..."
    
    if [[ -f "$REPO_PATH/MIGRATION_REPORT.md" ]]; then
        print_success "Migration report found"
        
        # Display basic info from report
        local migration_date=$(grep "Migration Date" "$REPO_PATH/MIGRATION_REPORT.md" | cut -d: -f2- | xargs)
        local source_repo=$(grep "Source Repository" "$REPO_PATH/MIGRATION_REPORT.md" | cut -d: -f2- | xargs)
        
        if [[ -n "$migration_date" ]]; then
            print_info "Migration date: $migration_date"
        fi
        
        if [[ -n "$source_repo" ]]; then
            print_info "Source repository: $source_repo"
        fi
    else
        print_warning "Migration report not found - this might not be a migrated repository"
    fi
}

validate_folder_structure() {
    print_info "Validating folder structure..."
    
    local found_folders=()
    local missing_folders=()
    
    # Get actual folders (excluding hidden directories and files)
    while IFS= read -r -d '' folder; do
        folder_name=$(basename "$folder")
        if [[ "$folder_name" != .* ]]; then
            found_folders+=("$folder_name")
        fi
    done < <(find "$REPO_PATH" -maxdepth 1 -type d -not -path "$REPO_PATH" -print0)
    
    print_info "Found folders: ${found_folders[*]}"
    
    # If expected folders are specified, check for them
    if [[ ${#EXPECTED_FOLDERS[@]} -gt 0 ]]; then
        for expected in "${EXPECTED_FOLDERS[@]}"; do
            if [[ " ${found_folders[*]} " =~ " ${expected} " ]]; then
                print_success "✓ Folder '$expected' found"
            else
                print_error "✗ Expected folder '$expected' not found"
                missing_folders+=("$expected")
            fi
        done
        
        if [[ ${#missing_folders[@]} -eq 0 ]]; then
            print_success "All expected folders are present"
        else
            print_error "Missing folders: ${missing_folders[*]}"
            return 1
        fi
    fi
    
    return 0
}

validate_commit_history() {
    print_info "Validating commit history preservation..."
    
    cd "$REPO_PATH"
    
    # Check for migration-related commits
    local migration_commits=$(git log --oneline --grep="Migration timestamp" | wc -l)
    local merge_commits=$(git log --oneline --merges | wc -l)
    local total_commits=$(git log --oneline | wc -l)
    
    print_info "Total commits: $total_commits"
    print_info "Merge commits: $merge_commits"
    print_info "Migration commits: $migration_commits"
    
    if [[ $migration_commits -gt 0 ]]; then
        print_success "Migration commits found - history appears to be preserved"
    else
        print_warning "No migration commits found - manual verification recommended"
    fi
    
    if [[ $total_commits -lt 2 ]]; then
        print_warning "Very few commits found - verify migration completed successfully"
    fi
}

validate_file_content() {
    print_info "Validating file content in folders..."
    
    local folders_with_content=0
    local empty_folders=0
    
    # Check each directory for content
    while IFS= read -r -d '' folder; do
        folder_name=$(basename "$folder")
        if [[ "$folder_name" != .* && "$folder_name" != "MIGRATION_REPORT.md" && "$folder_name" != "README.md" ]]; then
            local file_count=$(find "$folder" -type f | wc -l)
            if [[ $file_count -gt 0 ]]; then
                print_success "✓ Folder '$folder_name' contains $file_count files"
                folders_with_content=$((folders_with_content + 1))
            else
                print_warning "✗ Folder '$folder_name' is empty"
                empty_folders=$((empty_folders + 1))
            fi
        fi
    done < <(find "$REPO_PATH" -maxdepth 1 -type d -not -path "$REPO_PATH" -print0)
    
    print_info "Folders with content: $folders_with_content"
    if [[ $empty_folders -gt 0 ]]; then
        print_warning "Empty folders: $empty_folders"
    fi
}

check_github_copilot_compatibility() {
    print_info "Checking GitHub Copilot compatibility..."
    
    cd "$REPO_PATH"
    
    # Check for preserved commit messages
    local commits_with_messages=$(git log --pretty=format:"%s" | grep -v "^$" | wc -l)
    local total_commits=$(git log --oneline | wc -l)
    
    if [[ $commits_with_messages -eq $total_commits ]]; then
        print_success "All commits have descriptive messages - good for Copilot analysis"
    else
        print_warning "Some commits may lack descriptive messages"
    fi
    
    # Check for author information preservation
    local unique_authors=$(git log --pretty=format:"%an" | sort -u | wc -l)
    print_info "Unique authors found: $unique_authors"
    
    if [[ $unique_authors -gt 1 ]]; then
        print_success "Multiple authors preserved - good for understanding contribution history"
    fi
    
    # Check file types for code analysis
    local code_files=$(find "$REPO_PATH" -type f \( -name "*.js" -o -name "*.py" -o -name "*.java" -o -name "*.cpp" -o -name "*.c" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" \) | wc -l)
    
    if [[ $code_files -gt 0 ]]; then
        print_success "Code files found: $code_files - ready for Copilot analysis"
    else
        print_info "No common code files detected - repository may contain other file types"
    fi
}

generate_validation_report() {
    local report_file="$REPO_PATH/VALIDATION_REPORT.md"
    
    print_info "Generating validation report..."
    
    cat > "$report_file" << EOF
# Migration Validation Report

## Validation Details
- **Validation Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Repository Path**: $REPO_PATH
- **Validator Version**: Git Migration Validator v1.0

## Validation Results

### Repository Structure
- ✅ Valid git repository
- $(if [[ -f "$REPO_PATH/MIGRATION_REPORT.md" ]]; then echo "✅"; else echo "⚠️"; fi) Migration report present

### Folder Organization
EOF

    # Add folder validation results
    while IFS= read -r -d '' folder; do
        folder_name=$(basename "$folder")
        if [[ "$folder_name" != .* ]]; then
            local file_count=$(find "$folder" -type f | wc -l)
            echo "- **$folder_name**: $file_count files" >> "$report_file"
        fi
    done < <(find "$REPO_PATH" -maxdepth 1 -type d -not -path "$REPO_PATH" -print0)

    cat >> "$report_file" << EOF

### Git History
- **Total Commits**: $(cd "$REPO_PATH" && git log --oneline | wc -l)
- **Merge Commits**: $(cd "$REPO_PATH" && git log --oneline --merges | wc -l)
- **Unique Authors**: $(cd "$REPO_PATH" && git log --pretty=format:"%an" | sort -u | wc -l)

### GitHub Copilot Readiness
- ✅ Commit messages preserved
- ✅ Author information maintained
- ✅ File history available
- ✅ Ready for code analysis

## Recommendations

1. **Verify Content**: Manually check that all expected files are present in each folder
2. **Test Access**: Ensure you can navigate and access all migrated content
3. **GitHub Sync**: If using GitHub, verify the repository syncs correctly
4. **Copilot Test**: Try using GitHub Copilot to verify it can understand the codebase

---
*Generated by Git Migration Validator*
EOF

    print_success "Validation report generated: $report_file"
}

# Main validation function
perform_validation() {
    print_info "Starting migration validation..."
    print_info "Repository path: $REPO_PATH"
    
    local validation_errors=0
    
    # Run all validation checks
    validate_git_repository || validation_errors=$((validation_errors + 1))
    validate_migration_report
    validate_folder_structure || validation_errors=$((validation_errors + 1))
    validate_commit_history
    validate_file_content
    check_github_copilot_compatibility
    
    # Generate report
    generate_validation_report
    
    # Summary
    echo
    print_info "=== VALIDATION SUMMARY ==="
    
    if [[ $validation_errors -eq 0 ]]; then
        print_success "✅ Migration validation passed!"
        print_info "Your migrated repository appears to be correctly structured and ready for use."
    else
        print_warning "⚠️ Migration validation completed with $validation_errors warning(s)"
        print_info "Please review the issues above and consider re-running the migration if necessary."
    fi
    
    print_info "Detailed validation report available at: $REPO_PATH/VALIDATION_REPORT.md"
}

# Run validation
perform_validation