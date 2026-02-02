import json
import os
import sys
import time
from datetime import datetime
import getpass
from github import Github, GithubException, Auth

# Ensure the output directory exists
os.makedirs("../output", exist_ok=True)


def get_github_client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable not found.")
        token = getpass.getpass("Enter your GitHub Personal Access Token: ")
    try:
        auth = Auth.Token(token)
        return Github(auth=auth, per_page=100)
    except Exception as e:
        print(f"Error authenticating with GitHub: {e}")
        sys.exit(1)


def check_for_upgrade_pr(repo_to_search, g):
    query = f'repo:{repo_to_search} type:pr state:open "upgrade cashu-ts" OR "bump cashu-ts" OR "cashu-ts v3"'
    try:
        prs = g.search_issues(query, sort="created", order="desc")
        if prs.totalCount > 0:
            return prs[0].html_url
    except GithubException as e:
        if e.status == 403:
            pass
        else:
            print(
                f"    - Warning: Could not search for PRs in {repo_to_search}: {e.data.get('message', 'Unknown error')}"
            )
    return None


def print_and_write_report(report_data, file_handle=None):
    print_func = print
    if file_handle:

        def file_print(*args, **kwargs):
            print(*args, file=file_handle, **kwargs)

        print_func = file_print

    print_func("\n" + "=" * 70)
    print_func("                    CASHU-TS PROJECT REPORT")
    print_func(f"              Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_func("=" * 70)

    def print_section(title, items, format_func):
        print_func(f"\n--- {title} ({len(items)}) ---")
        if not items:
            print_func("  (None)")
            return
        for item in sorted(items, key=lambda i: i["stars"], reverse=True):
            print_func(format_func(item))

    # --- FORMAT STRINGS: Focused on 'updated_at' ---
    sections = [
        (
            "Projects on Cashu-TS v3",
            report_data["v3"],
            lambda r: f"  ⭐ {r['stars']:<5} | {r['updated']:<10} | {r['name']:<45} | {r['url']}",
        ),
        (
            "Projects on Cashu-TS v2 (With Open Upgrade PR)",
            report_data["v2_with_pr"],
            lambda r: f"  ⭐ {r['stars']:<5} | {r['updated']:<10} | {r['name']:<45} | PR: {r['pr_url']}",
        ),
        (
            "Projects on Cashu-TS v2 (No Upgrade PR Found)",
            report_data["v2_no_pr"],
            lambda r: f"  ⭐ {r['stars']:<5} | {r['updated']:<10} | {r['name']:<45} | {r['url']}",
        ),
        (
            "Projects on Cashu-TS v1 or Older (Deprecated)",
            report_data["v1_older"],
            lambda r: f"  ⭐ {r['stars']:<5} | {r['updated']:<10} | {r['name']:<45} | Using: {r['package_name']:<20} | {r['url']}",
        ),
        (
            "Projects Where No Cashu Dependency Was Found",
            report_data["not_found"],
            lambda r: f"  ⭐ {r['stars']:<5} | {r['updated']:<10} | {r['name']:<45} | {r['url']}",
        ),
        (
            "Projects That Could Not Be Processed (Errors)",
            report_data["errors"],
            lambda r: f"  ⭐ {r['stars']:<5} | {'N/A':<10} | {r['name']:<45} | Error: {r['message']}",
        ),
    ]

    for title, items, fmt in sections:
        print_section(title, items, fmt)

    print_func("\n" + "=" * 70)


def main():
    input_path = os.path.join("..", "output", "repo_versions.json")
    if not os.path.exists(input_path):
        print(f"Error: '{input_path}' not found. Please run 02_get_versions.py first.")
        sys.exit(1)

    print("Connecting to GitHub...")
    g = get_github_client()

    with open(input_path, "r") as f:
        repo_versions = json.load(f)

    report_data = {
        "v3": [],
        "v2_with_pr": [],
        "v2_no_pr": [],
        "v1_older": [],
        "not_found": [],
        "errors": [],
    }

    print("Processing repository data and checking for PRs...")
    v2_repos_to_check = []
    for repo_name, data in repo_versions.items():
        try:
            repo = g.get_repo(repo_name)

            repo_info = {
                "name": repo_name,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "updated": data.get("updated_at", "N/A"),
            }

            status = data.get("status")
            major_version = data.get("major_version")

            if status == "found" and major_version == 3:
                report_data["v3"].append(repo_info)
            elif status == "found" and major_version == 2:
                v2_repos_to_check.append({"repo_info": repo_info, "repo_obj": repo})
            elif status == "found_old" or (status == "found" and major_version is None):
                pkg_name = data.get("package_name", "N/A")
                report_data["v1_older"].append({**repo_info, "package_name": pkg_name})
            elif status == "not_found":
                report_data["not_found"].append(repo_info)
            elif status == "error":
                report_data["errors"].append(
                    {**repo_info, "message": data.get("message", "Unknown error")}
                )
        except Exception as e:
            print(f"  - An error occurred for {repo_name}: {e}")
            report_data["errors"].append(
                {"name": repo_name, "url": "#", "stars": 0, "updated": "N/A", "message": str(e)}
            )

    print(f"\nFound {len(v2_repos_to_check)} projects on v2. Checking for upgrade PRs...")
    for i, item in enumerate(v2_repos_to_check):
        repo_info = item["repo_info"]
        repo_obj = item["repo_obj"]

        print(f"  - ({i + 1}/{len(v2_repos_to_check)}) Checking PRs for {repo_info['name']}...")
        pr_url = check_for_upgrade_pr(repo_info["name"], g)

        if pr_url:
            report_data["v2_with_pr"].append({**repo_info, "pr_url": pr_url})
            print(f"    - Found PR.")
        else:
            report_data["v2_no_pr"].append(repo_info)
            print(f"    - No open upgrade PR found.")
        time.sleep(2)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join("..", "output", f"cashu_report_{timestamp}.txt")

    print(f"\n--- Saving report to {report_filename} ---")
    with open(report_filename, "w") as report_file:
        print_and_write_report(report_data, file_handle=report_file)

    print_and_write_report(report_data)


if __name__ == "__main__":
    main()
