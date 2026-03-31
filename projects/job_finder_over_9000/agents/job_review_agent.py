"""
Job Review Agent

Validates that found jobs are real and still open, then ranks them
against the candidate's requirements. Outputs a ranked list to output/ranked_jobs.md.
"""

import anyio
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

from .utils import AgentResult, stream_agent

ROOT_DIR = Path(__file__).parent.parent


async def run_job_review_agent(
    model: str = "claude-opus-4-6",
    max_turns: int = 60,
    candidates_path: Path | None = None,
) -> AgentResult:
    """
    Validate and rank job candidates against requirements.

    Args:
        model: Claude model to use. Use "claude-haiku-4-5" for cheap testing.
        max_turns: Maximum agent turns (reduce to cut cost).
        candidates_path: Path to candidates file (defaults to output/job_candidates.md).
                         Pass output/selected_jobs.md to review only user-selected jobs.

    Returns:
        AgentResult with result text and token usage.
    """
    requirements_path = ROOT_DIR / "data" / "requirements.md"
    cv_path = ROOT_DIR / "data" / "cv.md"
    if candidates_path is None:
        candidates_path = ROOT_DIR / "output" / "job_candidates.md"
    output_path = ROOT_DIR / "output" / "ranked_jobs.md"
    avoid_path = ROOT_DIR / "data" / "avoid_jobs.md"

    prompt = f"""You are a senior recruitment specialist and career coach. Your task is to validate and rank job candidates.

Follow these steps:

1. Read the job requirements file at: {requirements_path}
2. Read the candidate's CV at: {cv_path}
3. Read the job candidates list at: {candidates_path}

4. For each job in the candidates list:
   a. Fetch the job posting URL to verify:
      - The position is still open (not expired/filled)
      - The details match what was recorded
      - Any salary/requirements not captured initially
   b. Score the job on these criteria (1-10 each):
      - **Role match**: Does the title/level match the candidate?
      - **Tech stack match**: How well does the stack match skills?
      - **Salary match**: Does it meet the salary requirements?
      - **Culture fit**: Remote policy, company size, culture signals?
      - **Company quality**: Growth stage, reputation, funding?
   c. Calculate a weighted total score (role + tech stack weighted heavier)

5. Remove any jobs that are:
   - No longer open / expired
   - Clear mismatches on requirements
   - Excluded company types (from requirements)
   For each removed job, record it in the avoid list at: {avoid_path}
   Append to the file if it exists, create it if not. Use this format for each entry:
   - **[Job Title] — [Company Name]** | URL: [url] | Reason: [why it was removed]

6. Rank the remaining jobs by total score (highest first)

7. Write the ranked list to: {output_path}

Format the output file as markdown:

# Ranked Job List
*Generated: [date]*
*Total candidates reviewed: X | Qualified: Y*

---

## Rank #[N] — [Job Title] at [Company Name]
**Overall Score: [X]/50**

| Criteria | Score | Notes |
|----------|-------|-------|
| Role Match | X/10 | ... |
| Tech Stack | X/10 | ... |
| Salary | X/10 | ... |
| Culture Fit | X/10 | ... |
| Company Quality | X/10 | ... |

- **URL:** [direct link]
- **Location:** [location]
- **Salary:** [salary]
- **Status:** Verified Open ✅ / Possibly Filled ⚠️
- **Recommendation:** [1-2 sentences on why to apply]

---

Put the most promising jobs first. Be honest in scoring — a lower-ranked job that's a great fit is more useful than an inflated score.
"""

    return await stream_agent(
        name="Job Review Agent",
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
    anyio.run(run_job_review_agent)
