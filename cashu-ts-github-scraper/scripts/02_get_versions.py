import json
import os
import sys
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


def parse_version(version_string):
    if not version_string:
        return None
    if version_string.startswith(("^", "~", ">", "<", "=")):
        version_string = version_string[1:]
    try:
        return int(version_string.split(".")[0])
    except (ValueError, IndexError):
        return None


def main():
    input_path = os.path.join("..", "output", "repos_to_check.json")
    if not os.path.exists(input_path):
        print(f"Error: '{input_path}' not found. Please run 01_search_repos.py first.")
        sys.exit(1)

    print("Connecting to GitHub...")
    g = get_github_client()

    repo_data = {}

    with open(input_path, "r") as f:
        repos_to_check = json.load(f)

    print(f"Processing {len(repos_to_check)} repositories...")

    possible_names = ["@cashubtc/cashu-ts", "@cashu/cashu-ts", "cashu-ts"]

    for item in repos_to_check:
        repo_name = item["repo_name"]
        file_path = item["file_path"]

        print(f"  - Processing {repo_name} (at {file_path})...")
        try:
            repo = g.get_repo(repo_name)

            # --- NEW: Collect creation and update dates ---
            created_date = repo.created_at.strftime("%Y-%m-%d")
            updated_date = repo.updated_at.strftime("%Y-%m-%d")

            file_content = repo.get_contents(file_path, ref=repo.default_branch)
            package_json = json.loads(file_content.decoded_content.decode("utf-8"))

            deps = package_json.get("dependencies", {})
            dev_deps = package_json.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            found_package_name = None
            found_version_string = None

            for name in possible_names:
                if name in all_deps:
                    found_package_name = name
                    found_version_string = all_deps[name]
                    break

            if found_package_name:
                major_version = parse_version(found_version_string)
                repo_data[repo_name] = {
                    "status": "found" if major_version else "found_old",
                    "package_name": found_package_name,
                    "version_string": found_version_string,
                    "major_version": major_version,
                    # --- NEW: Add dates to the saved data ---
                    "created_at": created_date,
                    "updated_at": updated_date,
                }
                print(
                    f"    - Found {found_package_name}: {found_version_string} (Last updated: {updated_date})"
                )
            else:
                print(f"    - No Cashu dependency found (unexpected!).")
                repo_data[repo_name] = {
                    "status": "not_found",
                    "created_at": created_date,
                    "updated_at": updated_date,
                }

        except GithubException as e:
            print(f"    - ERROR: {e.status} {e.data.get('message', 'Unknown GitHub API Error')}")
            repo_data[repo_name] = {"status": "error", "message": str(e)}
        except json.JSONDecodeError:
            print(f"    - ERROR: Could not parse package.json.")
            repo_data[repo_name] = {"status": "error", "message": "JSONDecodeError"}
        except Exception as e:
            print(f"    - ERROR: An unexpected error occurred: {e}")
            repo_data[repo_name] = {"status": "error", "message": str(e)}

    output_path = os.path.join("..", "output", "repo_versions.json")
    with open(output_path, "w") as f:
        json.dump(repo_data, f, indent=2)

    print(f"\nSuccessfully saved detailed data to '{output_path}'")


if __name__ == "__main__":
    main()
