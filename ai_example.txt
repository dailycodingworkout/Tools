#!/usr/bin/env python3
"""
AI Example: Comprehensive Git Repository Analysis

This script demonstrates how an AI agent can effectively analyze the transformed
Git repository data. It showcases various analysis patterns, insights extraction,
and automated reporting capabilities.
"""

import json
from ai_query_helper import AIGitQueryHelper, quick_stats, search_everything
from datetime import datetime
from pathlib import Path

class AIRepositoryAnalyst:
    """AI Agent for automated Git repository analysis."""
    
    def __init__(self, data_file: str = "repository_data.json"):
        """Initialize the AI analyst with repository data."""
        self.helper = AIGitQueryHelper(data_file)
        self.data = self.helper.data
    
    def analyze_development_patterns(self) -> dict:
        """Analyze development patterns and team behavior."""
        patterns = {}
        
        # Commit timing analysis
        commit_hours = self.helper.get_commit_frequency_by_hour()
        peak_hour = max(commit_hours.items(), key=lambda x: x[1]) if commit_hours else (0, 0)
        
        patterns["work_schedule"] = {
            "peak_hour": peak_hour[0],
            "commits_at_peak": peak_hour[1],
            "hourly_distribution": commit_hours,
            "analysis": self._analyze_work_schedule(commit_hours)
        }
        
        # Commit frequency patterns
        date_frequency = self.helper.get_commit_frequency_by_date()
        patterns["activity_timeline"] = {
            "daily_commits": date_frequency,
            "most_active_day": max(date_frequency.items(), key=lambda x: x[1]) if date_frequency else ("", 0),
            "development_phases": self._identify_development_phases(date_frequency)
        }
        
        # Message analysis
        patterns["commit_style"] = self._analyze_commit_messages()
        
        return patterns
    
    def _analyze_work_schedule(self, hour_dist: dict) -> str:
        """Analyze work schedule from commit hours."""
        if not hour_dist:
            return "No commit timing data available"
        
        # Categorize hours
        morning = sum(hour_dist.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_dist.get(h, 0) for h in range(12, 18))
        evening = sum(hour_dist.get(h, 0) for h in range(18, 24))
        night = sum(hour_dist.get(h, 0) for h in range(0, 6))
        
        total = morning + afternoon + evening + night
        if total == 0:
            return "No temporal patterns found"
        
        # Find dominant period
        periods = [
            ("morning (6-12)", morning),
            ("afternoon (12-18)", afternoon),
            ("evening (18-24)", evening),
            ("night (0-6)", night)
        ]
        
        dominant = max(periods, key=lambda x: x[1])
        percentage = (dominant[1] / total) * 100
        
        return f"Most active during {dominant[0]} ({percentage:.1f}% of commits)"
    
    def _identify_development_phases(self, date_freq: dict) -> list:
        """Identify development phases from commit frequency."""
        if not date_freq:
            return []
        
        # Sort dates
        sorted_dates = sorted(date_freq.items())
        phases = []
        
        # Simple phase detection based on activity levels
        avg_commits = sum(date_freq.values()) / len(date_freq)
        
        current_phase = None
        phase_start = None
        
        for date, commits in sorted_dates:
            if commits > avg_commits * 1.5:  # High activity
                if current_phase != "high":
                    if current_phase:
                        phases.append({
                            "phase": current_phase,
                            "start": phase_start,
                            "end": date,
                            "intensity": "high" if current_phase == "high" else "low"
                        })
                    current_phase = "high"
                    phase_start = date
            else:  # Normal/low activity
                if current_phase == "high":
                    phases.append({
                        "phase": "high",
                        "start": phase_start,
                        "end": date,
                        "intensity": "high"
                    })
                    current_phase = "normal"
                    phase_start = date
        
        return phases
    
    def _analyze_commit_messages(self) -> dict:
        """Analyze commit message patterns."""
        messages = [commit["message"]["subject"] for commit in self.data["commits"]]
        
        # Message length analysis
        lengths = [len(msg) for msg in messages]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        # Convention analysis
        conventional_patterns = {
            "feat": 0, "fix": 0, "docs": 0, "style": 0,
            "refactor": 0, "test": 0, "chore": 0
        }
        
        for msg in messages:
            msg_lower = msg.lower()
            for pattern in conventional_patterns:
                if msg_lower.startswith(pattern + ":") or pattern in msg_lower:
                    conventional_patterns[pattern] += 1
        
        # Sentiment analysis (simple)
        positive_words = ["add", "improve", "enhance", "fix", "update", "upgrade"]
        negative_words = ["remove", "delete", "deprecate", "break", "error"]
        
        sentiment_score = 0
        for msg in messages:
            msg_lower = msg.lower()
            for word in positive_words:
                if word in msg_lower:
                    sentiment_score += 1
            for word in negative_words:
                if word in msg_lower:
                    sentiment_score -= 1
        
        return {
            "average_length": round(avg_length, 1),
            "conventional_commits": conventional_patterns,
            "sentiment_score": sentiment_score,
            "total_messages": len(messages)
        }
    
    def analyze_code_evolution(self) -> dict:
        """Analyze how the codebase evolved over time."""
        evolution = {}
        
        # File lifecycle analysis
        files_data = self.data["files"]
        
        if files_data:
            # File age analysis
            creation_dates = [f["created_date"] for f in files_data.values()]
            modification_dates = [f["last_modified"] for f in files_data.values()]
            
            evolution["file_lifecycle"] = {
                "total_files": len(files_data),
                "oldest_file": min(creation_dates) if creation_dates else None,
                "newest_file": max(creation_dates) if creation_dates else None,
                "last_activity": max(modification_dates) if modification_dates else None
            }
            
            # File stability analysis
            file_activity = [(name, data["total_commits"]) for name, data in files_data.items()]
            file_activity.sort(key=lambda x: x[1], reverse=True)
            
            evolution["file_stability"] = {
                "most_changed_files": file_activity[:5],
                "stable_files": [f for f in file_activity if f[1] == 1],
                "average_changes_per_file": sum(f[1] for f in file_activity) / len(file_activity) if file_activity else 0
            }
        else:
            evolution["file_lifecycle"] = {"message": "No file data available"}
            evolution["file_stability"] = {"message": "No file data available"}
        
        # Code volume evolution
        commits_timeline = self.helper.get_commit_timeline()
        running_insertions = 0
        running_deletions = 0
        volume_timeline = []
        
        for commit in commits_timeline:
            running_insertions += commit["stats"]["insertions"]
            running_deletions += commit["stats"]["deletions"]
            net_lines = running_insertions - running_deletions
            
            volume_timeline.append({
                "date": commit["author"]["date"],
                "commit": commit["hash"][:8],
                "net_lines": net_lines,
                "insertions": running_insertions,
                "deletions": running_deletions
            })
        
        evolution["code_volume"] = {
            "timeline": volume_timeline,
            "final_net_lines": volume_timeline[-1]["net_lines"] if volume_timeline else 0,
            "total_insertions": running_insertions,
            "total_deletions": running_deletions
        }
        
        return evolution
    
    def analyze_team_collaboration(self) -> dict:
        """Analyze team collaboration patterns."""
        collaboration = {}
        
        authors = self.data["authors"]
        
        if len(authors) > 1:
            # Collaboration matrix
            collab_matrix = self.helper.get_author_collaboration_matrix()
            
            # Find strongest collaborations
            strongest_pairs = []
            for author1, partners in collab_matrix.items():
                for author2, shared_files in partners.items():
                    if shared_files > 0:
                        author1_name = authors[author1]["name"]
                        author2_name = authors[author2]["name"]
                        strongest_pairs.append((author1_name, author2_name, shared_files))
            
            strongest_pairs.sort(key=lambda x: x[2], reverse=True)
            
            collaboration["team_dynamics"] = {
                "total_authors": len(authors),
                "collaboration_pairs": len(strongest_pairs),
                "strongest_collaborations": strongest_pairs[:5],
                "collaboration_score": sum(pair[2] for pair in strongest_pairs) / len(strongest_pairs) if strongest_pairs else 0
            }
        else:
            collaboration["team_dynamics"] = {
                "message": "Single author repository - no collaboration patterns to analyze"
            }
        
        # Author contribution analysis
        author_stats = []
        for email, data in authors.items():
            stats = {
                "name": data["name"],
                "email": email,
                "commits": data["commits"],
                "lines_added": data["total_insertions"],
                "lines_removed": data["total_deletions"],
                "files_touched": len(data["files_touched"]),
                "activity_span": self._calculate_activity_span(data["first_commit"], data["last_commit"])
            }
            author_stats.append(stats)
        
        author_stats.sort(key=lambda x: x["commits"], reverse=True)
        
        collaboration["author_contributions"] = author_stats
        
        return collaboration
    
    def _calculate_activity_span(self, first_commit: str, last_commit: str) -> dict:
        """Calculate activity span for an author."""
        try:
            first = datetime.fromisoformat(first_commit.replace('Z', '+00:00'))
            last = datetime.fromisoformat(last_commit.replace('Z', '+00:00'))
            span = last - first
            
            return {
                "days": span.days,
                "first_commit": first_commit,
                "last_commit": last_commit,
                "is_active": span.days < 30  # Active if committed within last 30 days
            }
        except:
            return {"days": 0, "first_commit": first_commit, "last_commit": last_commit, "is_active": False}
    
    def generate_insights(self) -> dict:
        """Generate actionable insights from the analysis."""
        insights = {
            "development_insights": [],
            "team_insights": [],
            "code_insights": [],
            "recommendations": []
        }
        
        # Development patterns insights
        patterns = self.analyze_development_patterns()
        work_schedule = patterns.get("work_schedule", {})
        
        if work_schedule.get("peak_hour", 0) in range(22, 6):  # Night coding
            insights["development_insights"].append(
                "Late night coding detected - consider work-life balance"
            )
        
        # Team insights
        collaboration = self.analyze_team_collaboration()
        team_data = collaboration.get("team_dynamics", {})
        
        if team_data.get("total_authors", 0) == 1:
            insights["team_insights"].append(
                "Single contributor project - consider bringing in collaborators for code review"
            )
        elif team_data.get("collaboration_score", 0) < 1:
            insights["team_insights"].append(
                "Low collaboration score - team members working on separate files"
            )
        
        # Code evolution insights
        evolution = self.analyze_code_evolution()
        volume = evolution.get("code_volume", {})
        
        if volume.get("total_deletions", 0) > volume.get("total_insertions", 0):
            insights["code_insights"].append(
                "More deletions than insertions - codebase is being simplified/refactored"
            )
        
        # Generate recommendations
        commits_count = len(self.data["commits"])
        if commits_count < 10:
            insights["recommendations"].append(
                "Consider more frequent commits for better version control"
            )
        
        files_count = len(self.data["files"])
        if files_count == 0:
            insights["recommendations"].append(
                "No file changes detected - repository may be in initial state"
            )
        
        return insights
    
    def generate_comprehensive_report(self) -> dict:
        """Generate a comprehensive AI analysis report."""
        print("🤖 AI Repository Analysis in progress...")
        
        report = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "repository_path": self.data["repository"]["original_path"],
                "data_file": "repository_data.json"
            },
            "summary": self.helper.generate_summary_report(),
            "development_patterns": self.analyze_development_patterns(),
            "code_evolution": self.analyze_code_evolution(),
            "team_collaboration": self.analyze_team_collaboration(),
            "insights": self.generate_insights(),
            "data_integrity": self.helper.validate_data_integrity()
        }
        
        return report
    
    def save_report(self, filename: str = "ai_analysis_report.json") -> str:
        """Save comprehensive report to file."""
        report = self.generate_comprehensive_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Comprehensive AI analysis saved to {filename}")
        return filename

def main():
    """Main function demonstrating AI analysis capabilities."""
    print("🚀 AI Git Repository Analysis Demo")
    print("=" * 50)
    
    try:
        # Initialize AI analyst
        analyst = AIRepositoryAnalyst()
        
        # Quick overview
        print("\n📋 Quick Repository Overview:")
        summary = analyst.helper.generate_summary_report()
        repo_info = summary["repository_overview"]
        
        print(f"   📦 Repository: {repo_info.get('original_path', 'Unknown')}")
        print(f"   📊 Commits: {repo_info.get('total_commits', 0)}")
        print(f"   👥 Authors: {repo_info.get('total_authors', 0)}")
        print(f"   📄 Files: {repo_info.get('total_files', 0)}")
        
        # Development patterns
        print("\n🕐 Development Patterns:")
        patterns = analyst.analyze_development_patterns()
        work_schedule = patterns["work_schedule"]
        print(f"   {work_schedule['analysis']}")
        
        # Team analysis
        print("\n👥 Team Collaboration:")
        collaboration = analyst.analyze_team_collaboration()
        team_dynamics = collaboration["team_dynamics"]
        
        if "message" in team_dynamics:
            print(f"   {team_dynamics['message']}")
        else:
            print(f"   👨‍💻 Authors: {team_dynamics['total_authors']}")
            print(f"   🤝 Collaboration pairs: {team_dynamics['collaboration_pairs']}")
        
        # Code evolution
        print("\n📈 Code Evolution:")
        evolution = analyst.analyze_code_evolution()
        volume = evolution["code_volume"]
        print(f"   📝 Total insertions: {volume['total_insertions']}")
        print(f"   🗑️  Total deletions: {volume['total_deletions']}")
        print(f"   📊 Net lines: {volume['final_net_lines']}")
        
        # AI Insights
        print("\n🧠 AI Insights:")
        insights = analyst.generate_insights()
        
        all_insights = (
            insights["development_insights"] +
            insights["team_insights"] +
            insights["code_insights"] +
            insights["recommendations"]
        )
        
        if all_insights:
            for i, insight in enumerate(all_insights[:5], 1):
                print(f"   {i}. {insight}")
        else:
            print("   ✅ No specific issues or recommendations identified")
        
        # Search demonstration
        print("\n🔍 Search Capabilities Demo:")
        search_results = search_everything("test")
        total_results = sum(len(results) for results in search_results.values())
        print(f"   Found {total_results} results for 'test' across all data types")
        
        # Save comprehensive report
        print("\n💾 Saving Comprehensive Report:")
        report_file = analyst.save_report()
        report_size = Path(report_file).stat().st_size
        print(f"   📁 Report size: {report_size} bytes ({report_size/1024:.1f}K)")
        
        print("\n✅ AI Analysis Complete!")
        print("\nThis demonstrates how an AI can:")
        print("   • Understand repository structure and history")
        print("   • Identify development patterns and team dynamics")
        print("   • Generate actionable insights and recommendations")
        print("   • Search and analyze code evolution efficiently")
        print("   • Provide comprehensive reporting without Git dependencies")
        
    except FileNotFoundError:
        print("❌ Repository data file not found!")
        print("   Please run git_to_ai_extractor.py first to transform the repository.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()