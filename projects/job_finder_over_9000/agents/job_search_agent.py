"""
Job Search Agent

Reads job requirements and CV, then searches the web for relevant job opportunities.
Outputs a list of potential jobs to output/job_candidates.md for review.
"""

import anyio
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

from .utils import AgentResult, stream_agent

ROOT_DIR = Path(__file__).parent.parent


async def run_job_search_agent(
    model: str = "claude-opus-4-6",
    max_turns: int = 50,
    min_candidates: int = 10,
    max_candidates: int = 15,
) -> AgentResult:
    """
    Search for jobs online based on requirements and CV.

    Args:
        model: Claude model to use. Use "claude-haiku-4-5" for cheap testing.
        max_turns: Maximum agent turns (reduce to cut cost).
        min_candidates: Minimum number of candidates to find before stopping.
        max_candidates: Target maximum number of candidates.

    Returns:
        AgentResult with result text and token usage.
    """
    requirements_path = ROOT_DIR / "data" / "requirements.md"
    cv_path = ROOT_DIR / "data" / "cv.md"
    output_path = ROOT_DIR / "output" / "job_candidates.md"

    liked_jobs_path = ROOT_DIR / "data" / "liked_jobs.md"
    liked_jobs_instruction = (
        f"2a. Read the previously liked jobs history at: {liked_jobs_path}\n"
        "    Use it to understand what kinds of roles have appealed in the past — "
        "prioritise similar companies, role types, and tech stacks in your search.\n"
        if liked_jobs_path.exists() else ""
    )

    avoid_jobs_path = ROOT_DIR / "data" / "avoid_jobs.md"
    avoid_jobs_instruction = (
        f"2b. Read the avoid list at: {avoid_jobs_path}\n"
        "    Do not include any job posting that matches a URL or (company + title) "
        "combination already in this list — these have previously been found invalid or disqualified.\n"
        if avoid_jobs_path.exists() else ""
    )

    prompt = f"""You are a job search specialist. Your task is to find real, currently open job positions.

Follow these steps:

1. Read the job requirements file at: {requirements_path}
2. Read the CV file at: {cv_path}
{liked_jobs_instruction}{avoid_jobs_instruction}3. Search the web for open job positions that match the requirements. Search multiple sources:
   - LinkedIn Jobs
   - levels.fyi
   - Glassdoor
   - Indeed
   - Otta (otta.com)
   - Greenhouse job boards
   - Company career pages for well-known tech companies
4. For each job found, capture:
   - Job title
   - Company name
   - Location / remote policy
   - Salary range (if listed)
   - Key requirements
   - Direct URL to the job posting
   - Date posted (to verify it's recent / still open)
5. Find at least {min_candidates} relevant job candidates, aiming for up to {max_candidates}
6. Write all results to: {output_path}

Format the output file as markdown with this structure for each job:

## [Job Title] — [Company Name]
- **URL:** [direct link to job posting]
- **Location:** [location / remote policy]
- **Salary:** [salary range or "not listed"]
- **Posted:** [date]
- **Key Requirements:** [bullet points of main requirements]
- **Why it matches:** [1-2 sentences on why this fits the candidate]

---

Only include jobs that match the requirements.
Make sure the output directory exists before writing.
"""

    return await stream_agent(
        name="Job Search Agent",
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(ROOT_DIR),
            allowed_tools=["Read", "Write", "Bash", "WebSearch", "WebFetch"],
            permission_mode="acceptEdits",
            max_turns=max_turns,
            model=model,
        ),
    )


if __name__ == "__main__":
    anyio.run(run_job_search_agent)
