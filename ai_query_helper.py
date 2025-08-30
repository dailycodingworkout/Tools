#!/usr/bin/env python3
"""
AI Query Helper for Git Repository Data

This module provides helper functions for AI agents to easily query and analyze
the transformed Git repository data. It includes optimized lookups, analysis
functions, and data mining capabilities.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from collections import defaultdict, Counter

class AIGitQueryHelper:
    """Helper class for AI to query Git repository data efficiently."""
    
    def __init__(self, data_file: str = "repository_data.json"):
        """Initialize with repository data file."""
        self.data_file = Path(data_file)
        self.data = self._load_data()
        self.indexes = self.data.get("indexes", {})
    
    def _load_data(self) -> Dict[str, Any]:
        """Load repository data from JSON file."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Repository data file not found: {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # === BASIC LOOKUPS ===
    
    def get_commit_by_hash(self, hash_prefix: str) -> Optional[Dict[str, Any]]:
        """Get commit by hash (supports partial hashes)."""
        # Try exact match first
        if hash_prefix in self.indexes["by_hash"]:
            return self.indexes["by_hash"][hash_prefix]
        
        # Try partial match
        for full_hash, commit in self.indexes["by_hash"].items():
            if full_hash.startswith(hash_prefix):
                return commit
        
        return None
    
    def get_commits_by_author(self, author_email: str) -> List[Dict[str, Any]]:
        """Get all commits by an author."""
        commit_hashes = self.indexes["by_author"].get(author_email, [])
        return [self.indexes["by_hash"][h] for h in commit_hashes]
    
    def get_commits_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get commits by date (YYYY-MM-DD format)."""
        commit_hashes = self.indexes["by_date"].get(date, [])
        return [self.indexes["by_hash"][h] for h in commit_hashes]
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get file information and history."""
        return self.indexes["by_file"].get(filename)
    
    # === SEARCH FUNCTIONS ===
    
    def search_commits(self, query: str, field: str = "message") -> List[Dict[str, Any]]:
        """Search commits by message, author, or other fields."""
        results = []
        query_lower = query.lower()
        
        for commit in self.data["commits"]:
            if field == "message":
                if query_lower in commit["message"]["subject"].lower() or \
                   query_lower in commit["message"]["body"].lower():
                    results.append(commit)
            elif field == "author":
                if query_lower in commit["author"]["name"].lower() or \
                   query_lower in commit["author"]["email"].lower():
                    results.append(commit)
            elif field == "files":
                for change in commit["changes"]:
                    if query_lower in change["file"].lower():
                        results.append(commit)
                        break
        
        return results
    
    def search_files(self, pattern: str) -> List[Dict[str, Any]]:
        """Search files by name pattern (supports regex)."""
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for filename, file_data in self.data["files"].items():
            if regex.search(filename):
                results.append(file_data)
        
        return results
    
    # === ANALYSIS FUNCTIONS ===
    
    def get_author_stats(self, author_email: str = None) -> Dict[str, Any]:
        """Get comprehensive author statistics."""
        if author_email:
            return self.data["authors"].get(author_email, {})
        else:
            return self.data["authors"]
    
    def get_commit_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological commit timeline."""
        commits = sorted(
            self.data["commits"],
            key=lambda x: x["author"]["date"]
        )
        return commits
    
    def get_file_evolution(self, filename: str) -> List[Dict[str, Any]]:
        """Get complete evolution history of a file."""
        file_info = self.get_file_info(filename)
        if not file_info:
            return []
        
        history = []
        for hist_entry in file_info["history"]:
            commit = self.get_commit_by_hash(hist_entry["commit"])
            if commit:
                # Find the specific file change in this commit
                file_change = None
                for change in commit["changes"]:
                    if change["file"] == filename:
                        file_change = change
                        break
                
                history.append({
                    "commit": commit,
                    "change": file_change,
                    "history_entry": hist_entry
                })
        
        return sorted(history, key=lambda x: x["commit"]["author"]["date"])
    
    def get_most_active_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get files with most commits."""
        files_with_commits = [
            (filename, data["total_commits"], data)
            for filename, data in self.data["files"].items()
        ]
        
        sorted_files = sorted(files_with_commits, key=lambda x: x[1], reverse=True)
        return [{"file": f[0], "commits": f[1], "data": f[2]} for f in sorted_files[:limit]]
    
    def get_most_active_authors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most active authors by commit count."""
        authors_with_commits = [
            (email, data["commits"], data)
            for email, data in self.data["authors"].items()
        ]
        
        sorted_authors = sorted(authors_with_commits, key=lambda x: x[1], reverse=True)
        return [{"email": a[0], "commits": a[1], "data": a[2]} for a in sorted_authors[:limit]]
    
    def get_commit_frequency_by_date(self) -> Dict[str, int]:
        """Get commit frequency by date."""
        frequency = defaultdict(int)
        
        for commit in self.data["commits"]:
            date = commit["author"]["date"][:10]  # YYYY-MM-DD
            frequency[date] += 1
        
        return dict(frequency)
    
    def get_commit_frequency_by_hour(self) -> Dict[int, int]:
        """Get commit frequency by hour of day."""
        frequency = defaultdict(int)
        
        for commit in self.data["commits"]:
            # Extract hour from date string
            try:
                dt = datetime.fromisoformat(commit["author"]["date"].replace('Z', '+00:00'))
                frequency[dt.hour] += 1
            except:
                pass
        
        return dict(frequency)
    
    def get_language_stats(self) -> Dict[str, int]:
        """Get file count by language (based on extensions)."""
        language_count = defaultdict(int)
        
        for filename in self.data["files"].keys():
            ext = Path(filename).suffix.lower()
            if ext:
                language_count[ext] += 1
            else:
                language_count["no_extension"] += 1
        
        return dict(language_count)
    
    # === COLLABORATION ANALYSIS ===
    
    def get_file_collaborators(self, filename: str) -> List[Dict[str, Any]]:
        """Get all authors who worked on a specific file."""
        file_info = self.get_file_info(filename)
        if not file_info:
            return []
        
        collaborators = []
        for author_email in file_info["authors"]:
            author_data = self.data["authors"][author_email]
            
            # Count commits to this file
            file_commits = 0
            for hist_entry in file_info["history"]:
                if hist_entry["author"] == author_email:
                    file_commits += 1
            
            collaborators.append({
                "author": author_data,
                "commits_to_file": file_commits
            })
        
        return sorted(collaborators, key=lambda x: x["commits_to_file"], reverse=True)
    
    def get_author_collaboration_matrix(self) -> Dict[str, Dict[str, int]]:
        """Get matrix of authors who worked on same files."""
        collaboration = defaultdict(lambda: defaultdict(int))
        
        for filename, file_data in self.data["files"].items():
            authors = file_data["authors"]
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    collaboration[author1][author2] += 1
                    collaboration[author2][author1] += 1
        
        return {k: dict(v) for k, v in collaboration.items()}
    
    # === CHANGE ANALYSIS ===
    
    def get_largest_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get commits with most changes."""
        commits_with_size = []
        
        for commit in self.data["commits"]:
            total_changes = commit["stats"]["insertions"] + commit["stats"]["deletions"]
            commits_with_size.append((commit, total_changes))
        
        sorted_commits = sorted(commits_with_size, key=lambda x: x[1], reverse=True)
        return [{"commit": c[0], "total_changes": c[1]} for c in sorted_commits[:limit]]
    
    def get_commit_impact_score(self, commit_hash: str) -> float:
        """Calculate impact score for a commit based on files and changes."""
        commit = self.get_commit_by_hash(commit_hash)
        if not commit:
            return 0.0
        
        # Factors: files changed, lines changed, file importance
        files_changed = len(commit["changes"])
        lines_changed = commit["stats"]["insertions"] + commit["stats"]["deletions"]
        
        # Weight by file importance (files touched by more authors are more important)
        file_importance = 0
        for change in commit["changes"]:
            file_info = self.get_file_info(change["file"])
            if file_info:
                file_importance += len(file_info["authors"])
        
        # Simple scoring formula
        score = (files_changed * 0.3) + (lines_changed * 0.005) + (file_importance * 0.2)
        return round(score, 2)
    
    # === REPORTING FUNCTIONS ===
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive repository summary."""
        repo_info = self.data["repository"]
        
        # Calculate additional metrics
        total_insertions = sum(a["total_insertions"] for a in self.data["authors"].values())
        total_deletions = sum(a["total_deletions"] for a in self.data["authors"].values())
        
        # Find most active period
        frequency = self.get_commit_frequency_by_date()
        most_active_date = max(frequency.items(), key=lambda x: x[1]) if frequency else ("N/A", 0)
        
        # Find most impactful commit
        largest_commits = self.get_largest_commits(1)
        most_impactful = largest_commits[0] if largest_commits else None
        
        return {
            "repository_overview": repo_info,
            "code_metrics": {
                "total_insertions": total_insertions,
                "total_deletions": total_deletions,
                "net_lines": total_insertions - total_deletions
            },
            "activity_metrics": {
                "most_active_date": most_active_date[0],
                "commits_on_most_active_date": most_active_date[1],
                "average_commits_per_day": len(self.data["commits"]) / max(len(frequency), 1)
            },
            "collaboration_metrics": {
                "authors": self.get_most_active_authors(5),
                "files_with_most_contributors": self.get_most_active_files(5)
            },
            "technical_metrics": {
                "language_distribution": self.get_language_stats(),
                "largest_commit": most_impactful
            }
        }
    
    def find_patterns(self) -> Dict[str, Any]:
        """Find interesting patterns in the repository."""
        patterns = {}
        
        # Commit message patterns
        message_words = []
        for commit in self.data["commits"]:
            words = commit["message"]["subject"].lower().split()
            message_words.extend(words)
        
        patterns["common_commit_words"] = dict(Counter(message_words).most_common(10))
        
        # Time patterns
        patterns["commit_hours"] = self.get_commit_frequency_by_hour()
        
        # File patterns
        patterns["file_extensions"] = self.get_language_stats()
        
        # Author patterns
        author_commits = {email: data["commits"] for email, data in self.data["authors"].items()}
        patterns["author_activity"] = author_commits
        
        return patterns
    
    # === UTILITY FUNCTIONS ===
    
    def export_timeline_csv(self, filename: str = "commit_timeline.csv") -> str:
        """Export commit timeline to CSV."""
        import csv
        
        timeline = self.get_commit_timeline()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'hash', 'author', 'subject', 'insertions', 'deletions', 'files_changed']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for commit in timeline:
                writer.writerow({
                    'date': commit['author']['date'],
                    'hash': commit['hash'][:8],
                    'author': commit['author']['name'],
                    'subject': commit['message']['subject'],
                    'insertions': commit['stats']['insertions'],
                    'deletions': commit['stats']['deletions'],
                    'files_changed': commit['stats']['files_changed']
                })
        
        return filename
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of the repository data."""
        issues = []
        stats = {
            "total_commits": len(self.data["commits"]),
            "total_authors": len(self.data["authors"]),
            "total_files": len(self.data["files"]),
            "index_integrity": True
        }
        
        # Check if all commits in index exist
        for hash_val in self.indexes["by_hash"]:
            found = any(c["hash"] == hash_val for c in self.data["commits"])
            if not found:
                issues.append(f"Hash {hash_val} in index but not in commits")
                stats["index_integrity"] = False
        
        # Check if all authors referenced in commits exist
        for commit in self.data["commits"]:
            author_email = commit["author"]["email"]
            if author_email not in self.data["authors"]:
                issues.append(f"Author {author_email} referenced but not in authors list")
        
        return {
            "stats": stats,
            "issues": issues,
            "valid": len(issues) == 0
        }

# === CONVENIENCE FUNCTIONS ===

def load_repository(data_file: str = "repository_data.json") -> AIGitQueryHelper:
    """Load repository data and return helper instance."""
    return AIGitQueryHelper(data_file)

def quick_stats(data_file: str = "repository_data.json") -> Dict[str, Any]:
    """Get quick repository statistics."""
    helper = AIGitQueryHelper(data_file)
    return helper.generate_summary_report()

def search_everything(query: str, data_file: str = "repository_data.json") -> Dict[str, List]:
    """Search across all repository data."""
    helper = AIGitQueryHelper(data_file)
    
    return {
        "commits_by_message": helper.search_commits(query, "message"),
        "commits_by_author": helper.search_commits(query, "author"),
        "commits_by_files": helper.search_commits(query, "files"),
        "files": helper.search_files(query)
    }

# Example usage for AI agents
def ai_example_queries(data_file: str = "repository_data.json"):
    """Example queries that AI agents can use."""
    helper = AIGitQueryHelper(data_file)
    
    print("=== AI Git Repository Query Examples ===\n")
    
    # Basic lookups
    print("1. Get repository summary:")
    summary = helper.generate_summary_report()
    print(f"   Commits: {summary['repository_overview']['total_commits']}")
    print(f"   Authors: {summary['repository_overview']['total_authors']}")
    print(f"   Files: {summary['repository_overview']['total_files']}")
    
    # Search examples
    print("\n2. Search commits containing 'fix':")
    fix_commits = helper.search_commits("fix")
    for commit in fix_commits[:3]:  # Show first 3
        print(f"   {commit['hash'][:8]}: {commit['message']['subject']}")
    
    # Analysis examples
    print("\n3. Most active authors:")
    active_authors = helper.get_most_active_authors(3)
    for author in active_authors:
        print(f"   {author['data']['name']}: {author['commits']} commits")
    
    # Pattern finding
    print("\n4. Common commit message words:")
    patterns = helper.find_patterns()
    for word, count in list(patterns['common_commit_words'].items())[:5]:
        print(f"   '{word}': {count} times")
    
    print("\n5. Data integrity check:")
    integrity = helper.validate_data_integrity()
    print(f"   Valid: {integrity['valid']}")
    print(f"   Issues: {len(integrity['issues'])}")

if __name__ == "__main__":
    # Run example queries
    ai_example_queries()