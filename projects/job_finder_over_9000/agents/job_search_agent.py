"""
Job Search Agent

Reads job requirements and CV, then searches the web for relevant job opportunities.
Outputs a list of potential jobs to output/job_candidates.md for review.
"""

import anyio
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

from .utils import stream_agent

ROOT_DIR = Path(__file__).parent.parent


async def run_job_search_agent(
    model: str = "claude-opus-4-6",
    max_turns: int = 50,
    max_candidates: int = 15,
) -> str:
    """
    Search for jobs online based on requirements and CV.

    Args:
        model: Claude model to use. Use "claude-haiku-4-5" for cheap testing.
        max_turns: Maximum agent turns (reduce to cut cost).
        max_candidates: Number of job candidates to find.

    Returns:
        Summary of results.
    """
    requirements_path = ROOT_DIR / "data" / "requirements.md"
    cv_path = ROOT_DIR / "data" / "cv.md"
    output_path = ROOT_DIR / "output" / "job_candidates.md"

    prompt = f"""You are a job search specialist. Your task is to find real, currently open job positions.

Follow these steps:

1. Read the job requirements file at: {requirements_path}
2. Read the CV file at: {cv_path}
3. Search the web for open job positions that match the requirements. Search multiple sources:
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
5. Aim to find {max_candidates} relevant job candidates
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

Focus on quality over quantity. Only include jobs that genuinely match the requirements.
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
