# Cashu-TS GitHub Project Scraper

A Python-based tool to scan GitHub for projects using the `@cashubtc/cashu-ts` and `@cashu/cashu-ts` libraries. It identifies which version projects are using and checks for open Pull Requests to upgrade to v3.

## Features

- **Comprehensive Search:** Finds projects using both the new (`@cashubtc/cashu-ts`) and old (`@cashu/cashu-ts`) package names.
- **Monorepo Support:** Correctly identifies dependencies in subdirectories (e.g., `packages/core/package.json`).
- **Version Detection:** Categorizes projects by their Cashu-TS version (v3, v2, v1/older).
- **PR Discovery:** For v2 projects, it searches for open upgrade PRs on the upstream repository.
- **Detailed Reporting:** Generates a clean, console-based report and saves a timestamped text file.
- **Modular Design:** Broken into three logical steps to save intermediate results and avoid re-scraping.

## How It Works

The tool operates in three distinct steps, each handled by a separate script:

1. **`01_search_repos.py`**: Searches GitHub for all `package.json` files mentioning Cashu-TS and saves a list of repositories and the exact file paths.
2. **`02_get_versions.py`**: Reads the list, fetches each `package.json`, parses the dependency version, and saves the version data.
3. **`03_check_prs.py`**: Reads the version data, identifies v2 projects, searches for their upgrade PRs, and generates the final report.

## Prerequisites

- **Python 3.8+**
- **pip**
- **GitHub Personal Access Token (PAT)**: Required to avoid strict API rate limits. You can create one [here](https://github.com/settings/tokens). The `public_repo` scope is sufficient.

## Setup

1. **Install dependencies:**

   ```bash
   pip install PyGithub
   ```

2. **Set up your GitHub Token:**
   It's recommended to set your PAT as an environment variable.

   - **On macOS/Linux:**

     ```bash
     export GITHUB_TOKEN="your_personal_access_token_here"
     ```

## Usage

Run the scripts in order from the root of the repository.

1. **Search for Repositories:**
   This creates `output/repos_to_check.json`.

   ```bash
   python scripts/01_search_repos.py
   ```

2. **Get Version Data:**
   This reads the previous file and creates `output/repo_versions.json`.

   ```bash
   python scripts/02_get_versions.py
   ```

3. **Generate Final Report:**
   This reads the version data, checks for PRs, prints the report to the console, and saves a timestamped report file in the `output/` directory (e.g., `output/cashu_report_20231027_153000.txt`).

   ```bash
   python scripts/03_check_prs.py
   ```

## Output

The final report categorizes projects into six groups:

- Projects on Cashu-TS v3
- Projects on Cashu-TS v2 (With Open Upgrade PR)
- Projects on Cashu-TS v2 (No Upgrade PR Found)
- Projects on Cashu-TS v1 or Older (Deprecated)
- Projects Where No Cashu Dependency Was Found
- Projects That Could Not Be Processed (Errors)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
