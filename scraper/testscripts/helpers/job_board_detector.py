import re

# You can expand this with more platforms and smarter logic later
JOB_BOARD_PATTERNS = {
    "greenhouse": r"(greenhouse\.io|boards\.greenhouse\.io)",
    "lever": r"lever\.co",
    "workday": r"myworkdayjobs\.com",
    "successfactors": r"successfactors\.com",
    "smartrecruiters": r"smartrecruiters\.com",
    "bamboohr": r"bamboohr\.com",
    "jobvite": r"jobvite\.com",
    "icims": r"icims\.com",
    "ashby": r"ashbyhq\.com",
}

def detect_job_board(url: str, page_content: str) -> str:
    """
    Detect the job board platform based on URL or content.
    Returns the name of the platform or 'general'.
    """
    for name, pattern in JOB_BOARD_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE) or re.search(pattern, page_content, re.IGNORECASE):
            return name
    return "general"
