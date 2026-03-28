import subprocess
import os
import railtracks as rt


def load_repos():
    """Load project->path mapping from repos.txt"""
    repos = {}
    repos_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "repos.txt")
    if not os.path.exists(repos_file):
        return repos
    with open(repos_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, path = line.split("=", 1)
                repos[name.strip()] = path.strip()
    return repos


REPOS = load_repos()


@rt.function_node
def get_recent_commits(project: str, author: str, count: int = 10):
    """Get recent git commits by an author in a project repo.

    Args:
        project (str): Project name from repos.txt
        author (str): Git author name or email to filter by
        count (int): Number of commits to return (default 10)
    """
    repo_path = REPOS.get(project)
    if not repo_path:
        return f"Project '{project}' not found in repos.txt. Available: {list(REPOS.keys())}"
    result = subprocess.run(
        ["git", "log", f"--author={author}", f"-{count}", "--format=%h|%s|%ai"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("|", 2)
            if len(parts) >= 2:
                commits.append(
                    {
                        "sha": parts[0],
                        "message": parts[1],
                        "date": parts[2] if len(parts) > 2 else "",
                    }
                )
    return (
        commits if commits else f"No commits found for author '{author}' in {project}"
    )


@rt.function_node
def get_recent_changes(project: str, days: int = 7):
    """Get files changed in the last N days in a project repo.

    Args:
        project (str): Project name from repos.txt
        days (int): Number of days to look back (default 7)
    """
    repo_path = REPOS.get(project)
    if not repo_path:
        return f"Project '{project}' not found in repos.txt. Available: {list(REPOS.keys())}"
    result = subprocess.run(
        ["git", "log", f"--since={days} days ago", "--name-only", "--pretty=format:"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    files = list(set(f for f in result.stdout.strip().split("\n") if f.strip()))
    return files if files else f"No changes in the last {days} days in {project}"


@rt.function_node
def get_branches(project: str):
    """List branches in a project repo sorted by recent activity.

    Args:
        project (str): Project name from repos.txt
    """
    repo_path = REPOS.get(project)
    if not repo_path:
        return f"Project '{project}' not found in repos.txt. Available: {list(REPOS.keys())}"
    result = subprocess.run(
        ["git", "branch", "-a", "--sort=-committerdate"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    branches = [
        b.strip().lstrip("* ") for b in result.stdout.strip().split("\n") if b.strip()
    ]
    return branches[:15]


@rt.function_node
def get_file_content(project: str, file_path: str):
    """Read a specific file from a project repo (first 5000 chars).

    Args:
        project (str): Project name from repos.txt
        file_path (str): Relative path to file within the repo
    """
    repo_path = REPOS.get(project)
    if not repo_path:
        return f"Project '{project}' not found in repos.txt. Available: {list(REPOS.keys())}"
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return f"File not found: {file_path} in {project}"
    with open(full_path, "r", errors="replace") as f:
        return f.read()[:5000]


git_tools = [get_recent_commits, get_recent_changes, get_branches, get_file_content]
