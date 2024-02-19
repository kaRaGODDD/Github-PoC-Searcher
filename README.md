# Course Project: Automated Tool for Finding PoC Vulnerabilities

Welcome to the Course Project: Automated Tool for Finding Proof of Concept (PoC) Vulnerabilities. This project is designed to develop an automated tool that identifies PoC vulnerabilities within popular public repositories. The tool is implemented in Python and requires Python version 3.11 for execution.

## Project Repositories

Explore the results of the project in the following repositories:

- [CVE Database](https://github.com/kaRaGODDD/cve_database): This repository houses CVE vulnerabilities collected from the National Vulnerability Database (NVD).
- [CVE with their PoC's](https://github.com/kaRaGODDD/Cve-with-their-PoC-s): Discover PoCs for the CVE vulnerabilities identified on GitHub.

## Getting Started

To use the tool, set up a `.env` file with the following parameters:


- **PYTHONPATH** = "Path to directory with project"
- **GITHUB_GRAPHQL_URL** = "https://api.github.com/graphql"
- **GITHUB_API_URL** = "https://api.github.com/search/repositories?q={}"
- **GITHUB_SPECIAL_URL_FOR_UPDATE** = "https://api.github.com/search/repositories?q=cve%20created:{}..{}"
- **GITHUB_TOKEN** = "Your GitHub API token"
- **NVD_API_URL** = "https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={}&pubEndDate={}"
- **NVD_API_KEY** = "Your NVD API key"
- **NAME_OF_THE_DATA_DIRECTORY** = "Name of your data directory with CVE database"
- **PATH_TO_THE_DATA_DIRECTORY** = "Path to the CVE database directory"
- **PATH_TO_THE_BASE_DIRECTORY** = "Path where the repository with CVE will be created"
- **NAME_OF_THE_POC_DIRECTORY** = "Name of the PoC directory"
- **PATH_TO_THE_POC_DIRECTORY** = "Path to the PoC directory"
- **LAST_SCRAPPING_DATE_OF_NVD** = "Last scraping date of NVD"
- **NAME_OF_THE_JSON_AWSWERS_DIRECTORY** = "Name where JSON answers will be situated"
- **PATH_TO_THE_JSON_ANSWERS_DIRECTORY** = "Path to that directory"
- **PATH_TO_CVE_YEAR_DIRECTORY** = "For traversing the CVE data directory by fix year"
- **LAST_DATE_SCRAPPING_POC_UPDATE** = "Last update of PoC directory"


### __USAGE__

1. Clone that repository.
2. Set up the .env file with the specified parameters.
3. Run the tool using Python 3.11. **python main.py**


### __Contributions__

Feel free to contribute or report issues on the GitHub repository. Your interest and support are highly appreciated!