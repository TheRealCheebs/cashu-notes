import os
import sys
import getpass
import json
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


def main():
    print("Connecting to GitHub...")
    g = get_github_client()

    print("Searching for projects using any version of Cashu-TS...")

    query_v2 = '"@cashubtc/cashu-ts" in:file filename:package.json'
    query_v1 = '"@cashu/cashu-ts" in:file filename:package.json'

    found_files = {}

    def run_search(query):
        print(f"\nRunning query: {query}")
        try:
            code_search_results = g.search_code(query, sort="indexed", order="desc")
            if code_search_results.totalCount == 0:
                print("  - No results for this query.")
                return
            print(f"  - Found {code_search_results.totalCount} file results.")
            for file in code_search_results:
                repo_name = file.repository.full_name
                file_path = file.path
                if repo_name not in found_files:
                    found_files[repo_name] = file_path
        except GithubException as e:
            print(f"  - An error occurred during search: {e.data.get('message', 'Unknown error')}")

    run_search(query_v2)
    run_search(query_v1)

    if not found_files:
        print("\nNo projects found with either query.")
        return

    print(f"\n--- Search Complete ---")
    print(f"Found a total of {len(found_files)} unique repositories.")

    output_path = os.path.join("..", "output", "repos_to_check.json")
    with open(output_path, "w") as f:
        output_data = [{"repo_name": name, "file_path": path} for name, path in found_files.items()]
        json.dump(output_data, f, indent=2)

    print(f"Successfully saved repository and path data to '{output_path}'")


if __name__ == "__main__":
    main()
