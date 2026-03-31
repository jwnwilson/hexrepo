"""
Job Prep Agent

For the top-ranked jobs, creates tailored application materials:
- Tailored CV for each company
- Company summary
- Prep sheet with interview tips
- Application links and instructions
"""

import anyio
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

from .utils import AgentResult, stream_agent

ROOT_DIR = Path(__file__).parent.parent


async def run_job_prep_agent(
    top_n: int = 5,
    model: str = "claude-opus-4-6",
    max_turns: int = 100,
) -> AgentResult:
    """
    Generate tailored application materials for the top N ranked jobs.

    Args:
        top_n: Number of top jobs to prepare materials for (default: 5)
        model: Claude model to use. Use "claude-haiku-4-5" for cheap testing.
        max_turns: Maximum agent turns (reduce to cut cost).

    Returns:
        AgentResult with result text and token usage.
    """
    requirements_path = ROOT_DIR / "data" / "requirements.md"
    cv_path = ROOT_DIR / "data" / "cv.md"
    ranked_jobs_path = ROOT_DIR / "output" / "ranked_jobs.md"
    prep_dir = ROOT_DIR / "output" / "prep"

    prompt = f"""You are an expert career coach and CV specialist. Your task is to prepare tailored application materials.

Follow these steps:

1. Read the candidate's CV at: {cv_path}
2. Read the job requirements at: {requirements_path}
3. Read the ranked jobs list at: {ranked_jobs_path}
4. Identify the top {top_n} jobs from the ranked list

5. For each of the top {top_n} jobs, create a dedicated folder at: {prep_dir}/[company-name-slug]/
   and generate the following files:

   **a) tailored_cv.md**
   - Reorder and reword the candidate's CV to match the job description
   - Emphasise relevant technologies and experience
   - Mirror keywords from the job posting (ATS optimisation)
   - Keep it truthful — only reframe existing experience
   - Note: This is a tailored version, not a fabrication

   **b) company_summary.md**
   - Company overview: what they do, business model, customers
   - Recent news, funding rounds, product launches
   - Engineering team size and structure (if findable)
   - Tech stack used (from job posting, engineering blog, StackShare, etc.)
   - Company culture signals (Glassdoor reviews, CEO approval rating)
   - Growth trajectory and financial health
   - Key people: CTO, VP Eng, hiring manager (if listed)

   **c) prep_sheet.md**
   - **Why this company?** — 3-5 talking points specific to this company
   - **Why you?** — How the candidate's experience maps to their needs
   - **Likely interview topics**: Technical areas to prepare based on their stack
   - **Questions to ask them**: 5-7 smart questions tailored to the company
   - **Red flags to watch for**: Any concerns to probe in interviews
   - **Compensation strategy**: How to negotiate given their stage/funding

   **d) how_to_apply.md**
   - Direct application URL
   - Application method (direct, via recruiter, referral tips)
   - Required materials (CV, cover letter, portfolio, etc.)
   - Tips for this specific company's application process
   - Whether a cover letter is recommended and key points to hit
   - Timeline expectations

6. After generating all prep folders, create a master summary at: {prep_dir}/README.md
   - List all prepared companies with their rank and score
   - Quick links to each company's prep folder
   - Recommended application order and timing

Make sure all directories exist before writing files. Use Bash to create directories if needed.
Research each company thoroughly using web search before writing the materials.
"""

    return await stream_agent(
        name="Job Prep Agent",
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
    anyio.run(run_job_prep_agent)
