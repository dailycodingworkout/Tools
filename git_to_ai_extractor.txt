#!/usr/bin/env python3
"""
Git to AI Repository Extractor

This script extracts Git repository information and transforms it into an AI-readable format.
It creates a comprehensive JSON structure that preserves all commit history, file changes,
and author information while being optimized for AI analysis.
"""

import json
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

class GitToAIExtractor:
    """Extracts Git repository data and transforms it to AI-readable format."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize extractor with repository path."""
        self.repo_path = Path(repo_path).resolve()
        self.git_dir = self.repo_path / ".git"
        
        if not self.git_dir.exists():
            raise ValueError(f"No Git repository found at {repo_path}")
    
    def run_git_command(self, cmd: List[str]) -> str:
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            return ""
    
    def get_commits(self) -> List[Dict[str, Any]]:
        """Extract all commits with full metadata."""
        commits = []
        
        # Get commit hashes
        commit_hashes = self.run_git_command([
            "log", "--pretty=format:%H", "--all"
        ]).split('\n')
        
        for commit_hash in commit_hashes:
            if not commit_hash:
                continue
                
            # Get commit details
            commit_info = self.run_git_command([
                "show", "--pretty=format:%H|%an|%ae|%ad|%cn|%ce|%cd|%s|%B",
                "--no-patch", commit_hash
            ])
            
            if not commit_info:
                continue
                
            parts = commit_info.split('|', 7)
            if len(parts) < 8:
                continue
                
            hash_val, author_name, author_email, author_date, \
            committer_name, committer_email, committer_date, \
            subject = parts[:8]
            
            # Get full message
            full_message = self.run_git_command([
                "log", "-1", "--pretty=format:%B", commit_hash
            ])
            
            # Get file changes
            changed_files = self.get_commit_changes(commit_hash)
            
            # Get parent commits
            parents = self.run_git_command([
                "log", "-1", "--pretty=format:%P", commit_hash
            ]).split()
            
            commit_data = {
                "hash": hash_val,
                "author": {
                    "name": author_name,
                    "email": author_email,
                    "date": author_date
                },
                "committer": {
                    "name": committer_name,
                    "email": committer_email,
                    "date": committer_date
                },
                "message": {
                    "subject": subject,
                    "body": full_message
                },
                "parents": parents,
                "changes": changed_files,
                "stats": self.get_commit_stats(commit_hash)
            }
            
            commits.append(commit_data)
        
        return commits
    
    def get_commit_changes(self, commit_hash: str) -> List[Dict[str, Any]]:
        """Get file changes for a specific commit."""
        changes = []
        
        # Get file changes with stats
        try:
            files_changed = self.run_git_command([
                "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash
            ])
            
            for line in files_changed.split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t', 1)
                if len(parts) < 2:
                    continue
                    
                status = parts[0]
                filename = parts[1]
                
                # Get file content diff
                file_diff = self.run_git_command([
                    "show", f"{commit_hash}:{filename}"
                ]) if status != 'D' else ""
                
                change_data = {
                    "file": filename,
                    "status": status,
                    "diff": self.get_file_diff(commit_hash, filename),
                    "content_after": file_diff if status != 'D' else None
                }
                
                changes.append(change_data)
                
        except Exception as e:
            print(f"Error getting changes for commit {commit_hash}: {e}")
        
        return changes
    
    def get_file_diff(self, commit_hash: str, filename: str) -> str:
        """Get the diff for a specific file in a commit."""
        try:
            return self.run_git_command([
                "show", commit_hash, "--", filename
            ])
        except:
            return ""
    
    def get_commit_stats(self, commit_hash: str) -> Dict[str, int]:
        """Get statistics for a commit."""
        try:
            stats_output = self.run_git_command([
                "show", "--stat", "--format=", commit_hash
            ])
            
            # Parse stats (files changed, insertions, deletions)
            stats = {"files_changed": 0, "insertions": 0, "deletions": 0}
            
            for line in stats_output.split('\n'):
                if "changed" in line and ("insertion" in line or "deletion" in line):
                    if "file" in line and "changed" in line:
                        stats["files_changed"] = int(line.split()[0])
                    if "insertion" in line:
                        parts = line.split(", ")
                        for part in parts:
                            if "insertion" in part:
                                stats["insertions"] = int(part.split()[0])
                    if "deletion" in line:
                        parts = line.split(", ")
                        for part in parts:
                            if "deletion" in part:
                                stats["deletions"] = int(part.split()[0])
            
            return stats
        except:
            return {"files_changed": 0, "insertions": 0, "deletions": 0}
    
    def get_branches(self) -> List[Dict[str, str]]:
        """Get all branches."""
        branches = []
        
        try:
            branch_output = self.run_git_command(["branch", "-a"])
            for line in branch_output.split('\n'):
                if line.strip():
                    current = line.startswith('*')
                    name = line.replace('*', '').strip()
                    if name.startswith('remotes/'):
                        name = name[8:]  # Remove 'remotes/' prefix
                    
                    branches.append({
                        "name": name,
                        "current": current,
                        "type": "remote" if "remotes/" in line else "local"
                    })
        except:
            pass
        
        return branches
    
    def get_tags(self) -> List[Dict[str, str]]:
        """Get all tags."""
        tags = []
        
        try:
            tag_output = self.run_git_command(["tag", "-l"])
            for tag_name in tag_output.split('\n'):
                if tag_name.strip():
                    # Get tag commit
                    tag_commit = self.run_git_command(["rev-list", "-1", tag_name])
                    tags.append({
                        "name": tag_name.strip(),
                        "commit": tag_commit
                    })
        except:
            pass
        
        return tags
    
    def get_authors(self, commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract author information and statistics."""
        authors = {}
        
        for commit in commits:
            author_email = commit["author"]["email"]
            author_name = commit["author"]["name"]
            
            if author_email not in authors:
                authors[author_email] = {
                    "name": author_name,
                    "email": author_email,
                    "commits": 0,
                    "first_commit": commit["author"]["date"],
                    "last_commit": commit["author"]["date"],
                    "total_insertions": 0,
                    "total_deletions": 0,
                    "files_touched": set()
                }
            
            author_data = authors[author_email]
            author_data["commits"] += 1
            author_data["total_insertions"] += commit["stats"]["insertions"]
            author_data["total_deletions"] += commit["stats"]["deletions"]
            
            # Track files touched
            for change in commit["changes"]:
                author_data["files_touched"].add(change["file"])
            
            # Update dates
            if commit["author"]["date"] < author_data["first_commit"]:
                author_data["first_commit"] = commit["author"]["date"]
            if commit["author"]["date"] > author_data["last_commit"]:
                author_data["last_commit"] = commit["author"]["date"]
        
        # Convert sets to lists for JSON serialization
        for author_data in authors.values():
            author_data["files_touched"] = list(author_data["files_touched"])
        
        return authors
    
    def get_file_history(self, commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Create file evolution history."""
        files = {}
        
        for commit in commits:
            for change in commit["changes"]:
                filename = change["file"]
                
                if filename not in files:
                    files[filename] = {
                        "path": filename,
                        "created_in": commit["hash"],
                        "created_by": commit["author"]["email"],
                        "created_date": commit["author"]["date"],
                        "last_modified": commit["author"]["date"],
                        "last_modified_by": commit["author"]["email"],
                        "last_modified_in": commit["hash"],
                        "total_commits": 0,
                        "authors": set(),
                        "history": []
                    }
                
                file_data = files[filename]
                file_data["total_commits"] += 1
                file_data["authors"].add(commit["author"]["email"])
                file_data["last_modified"] = commit["author"]["date"]
                file_data["last_modified_by"] = commit["author"]["email"]
                file_data["last_modified_in"] = commit["hash"]
                
                file_data["history"].append({
                    "commit": commit["hash"],
                    "date": commit["author"]["date"],
                    "author": commit["author"]["email"],
                    "status": change["status"],
                    "message": commit["message"]["subject"]
                })
        
        # Convert sets to lists for JSON serialization
        for file_data in files.values():
            file_data["authors"] = list(file_data["authors"])
        
        return files
    
    def create_indexes(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Create search indexes for fast lookups."""
        indexes = {
            "by_hash": {},
            "by_author": {},
            "by_file": {},
            "by_date": {}
        }
        
        # Index commits by hash
        for commit in data["commits"]:
            indexes["by_hash"][commit["hash"]] = commit
            
            # Index by author
            author_email = commit["author"]["email"]
            if author_email not in indexes["by_author"]:
                indexes["by_author"][author_email] = []
            indexes["by_author"][author_email].append(commit["hash"])
            
            # Index by date
            date_key = commit["author"]["date"][:10]  # YYYY-MM-DD
            if date_key not in indexes["by_date"]:
                indexes["by_date"][date_key] = []
            indexes["by_date"][date_key].append(commit["hash"])
        
        # Index by file
        for filename, file_data in data["files"].items():
            indexes["by_file"][filename] = file_data
        
        return indexes
    
    def extract_repository_data(self) -> Dict[str, Any]:
        """Extract complete repository data."""
        print("Extracting Git repository data...")
        
        # Get all commits
        commits = self.get_commits()
        print(f"Found {len(commits)} commits")
        
        # Get branches and tags
        branches = self.get_branches()
        tags = self.get_tags()
        
        # Extract authors and file history
        authors = self.get_authors(commits)
        files = self.get_file_history(commits)
        
        # Create the main data structure
        data = {
            "repository": {
                "extracted_at": datetime.now().isoformat(),
                "original_path": str(self.repo_path),
                "total_commits": len(commits),
                "total_authors": len(authors),
                "total_files": len(files),
                "branches": len(branches),
                "tags": len(tags)
            },
            "commits": commits,
            "authors": authors,
            "files": files,
            "branches": branches,
            "tags": tags
        }
        
        # Create search indexes
        data["indexes"] = self.create_indexes(data)
        
        return data
    
    def save_to_file(self, data: Dict[str, Any], filename: str = "repository_data.json"):
        """Save extracted data to JSON file."""
        output_path = self.repo_path / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Repository data saved to {output_path}")
        return output_path
    
    def get_git_directory_size(self) -> int:
        """Get the size of the .git directory."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.git_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size
    
    def transform_repository(self, remove_git: bool = False):
        """Complete repository transformation."""
        print("Starting Git to AI transformation...")
        
        # Get original .git size
        git_size = self.get_git_directory_size()
        print(f"Original .git directory size: {git_size} bytes ({git_size/1024:.1f}K)")
        
        # Extract repository data
        data = self.extract_repository_data()
        
        # Save to JSON
        json_path = self.save_to_file(data)
        
        # Get new file size
        json_size = os.path.getsize(json_path)
        print(f"AI-readable format size: {json_size} bytes ({json_size/1024:.1f}K)")
        
        # Calculate space savings
        if git_size > 0:
            savings = ((git_size - json_size) / git_size) * 100
            print(f"Space savings: {savings:.1f}%")
        
        if remove_git:
            import shutil
            shutil.rmtree(self.git_dir)
            print("Removed .git directory")
        
        return data, json_path

def main():
    """Main function for command-line usage."""
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "."
    
    remove_git = "--remove-git" in sys.argv
    
    try:
        extractor = GitToAIExtractor(repo_path)
        data, json_path = extractor.transform_repository(remove_git=remove_git)
        
        print("\n✅ Transformation complete!")
        print(f"📁 Repository data: {json_path}")
        print(f"📊 Total commits: {data['repository']['total_commits']}")
        print(f"👥 Total authors: {data['repository']['total_authors']}")
        print(f"📄 Total files: {data['repository']['total_files']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()