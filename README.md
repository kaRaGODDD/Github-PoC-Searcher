# Required parameters

- PYTHONPATH - "Path to directory with project"
- GITHUB_GRAPHQL_URL="https://api.github.com/graphql"
- GITHUB_API_URL="https://api.github.com/search/repositories?q={}"
- GITHUB_SPECIAL_URL_FOR_UPDATE="https://api.github.com/search/repositories?q=cve%20created:{}..{}"
- GITHUB_TOKEN = "Your github API token"
- NVD_API_URL='https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={}&pubEndDate={}'
- NVD_API_KEY="your NVD API key"
- NAME_OF_THE_DATA_DIRECTORY="name of the your data directory with cve database"
- PATH_TO_THE_DATA_DIRECTORY="path to the cve database directory"
- PATH_TO_THE_BASE_DIRECTORY="path where the repository with cve will be created"
- NAME_OF_THE_POC_DIRECTORY="name of the poc directory"
- PATH_TO_THE_POC_DIRECTORY="path where path to the poc directory"
- LAST_SCRAPPING_DATE_OF_NVD="last scraping date of nvd"
- NAME_OF_THE_JSON_AWSWERS_DIRECTORY="just name where json answers will be situated"
- PATH_TO_THE_JSON_ANSWERS_DIRECTORY="path to that directory"
- PATH_TO_CVE_YEAR_DIRECTORY="for traverse the cve data directory by fix year"
- LAST_DATE_SCRAPPING_POC_UPDATE = "last update of poc directory"