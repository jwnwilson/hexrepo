"""
Job Finder Over 9000 — Main Orchestrator

Runs the three-stage multiagent job finding pipeline:
  1. Job Search Agent   — finds job candidates online
  2. Selection Step     — you pick which candidates to keep
  3. Job Review Agent   — validates and ranks selected candidates
  4. Job Prep Agent     — creates tailored application materials

Usage:
    python main.py                  # Run full pipeline (Opus, full scope)
    python main.py --cheap          # Run with Haiku + reduced scope (for testing)
    python main.py --stage search   # Run only job search
    python main.py --stage select   # Run only selection step
    python main.py --stage review   # Run only job review
    python main.py --stage prep     # Run only job prep
    python main.py --top 3          # Prep materials for top 3 jobs (default: 5)

Cost modes:
    Default  — claude-opus-4-6, 15 candidates, top 5 prep
    --cheap  — claude-haiku-4-5, 5 candidates, top 1 prep, reduced turns
"""

import argparse
import re
from datetime import date
import anyio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from agents import run_job_search_agent, run_job_review_agent, run_job_prep_agent, print_total_usage
from agents.utils import HitLimit

ROOT_DIR = Path(__file__).parent
console = Console()


def ensure_output_dirs() -> None:
    """Create output directories if they don't exist."""
    (ROOT_DIR / "output").mkdir(exist_ok=True)
    (ROOT_DIR / "output" / "prep").mkdir(exist_ok=True)


CHEAP_CONFIG = {
    "model": "claude-haiku-4-5",
    "min_candidates": 3,
    "max_candidates": 5,
    "top_n": 1,
    "search_turns": 15,
    "review_turns": 15,
    "prep_turns": 20,
}

DEFAULT_CONFIG = {
    "model": "claude-opus-4-6",
    "min_candidates": 10,
    "max_candidates": 15,
    "top_n": 5,
    "search_turns": 50,
    "review_turns": 60,
    "prep_turns": 100,
}


def _parse_job_blocks(candidates_path: Path) -> list[tuple[str, str]]:
    """
    Parse job_candidates.md into a list of (header, full_block) tuples.
    Each block is everything from '## Title' up to (not including) the next '## '.
    Returns list of (display_label, markdown_block).
    """
    text = candidates_path.read_text()
    # Split on level-2 headers that mark each job
    raw_blocks = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    jobs = []
    for block in raw_blocks:
        block = block.strip()
        if not block.startswith("## "):
            continue
        header_match = re.match(r"^## (.+)$", block, re.MULTILINE)
        if header_match:
            jobs.append((header_match.group(1).strip(), block))
    return jobs


def select_jobs(candidates_path: Path) -> Path | None:
    """
    Interactively present job candidates for selection.

    Displays a numbered list of jobs, prompts the user to choose,
    saves selected jobs to output/selected_jobs.md, and appends
    a compact history entry to data/liked_jobs.md.

    Returns the path to selected_jobs.md, or None if nothing was selected.
    """
    if not candidates_path.exists():
        console.print("[red]Error:[/red] output/job_candidates.md not found.")
        return None

    jobs = _parse_job_blocks(candidates_path)
    if not jobs:
        console.print("[yellow]No job candidates found to select from.[/yellow]")
        return None

    console.print("\n[bold cyan]Job Selection[/bold cyan]")
    console.print("[dim]Review the candidates found and pick the ones you want to proceed with.[/dim]\n")

    for i, (label, _) in enumerate(jobs, 1):
        console.print(f"  [bold cyan]{i:>2}.[/bold cyan] {label}")

    console.print()
    raw = console.input(
        "[bold]Enter job numbers to keep[/bold] "
        "(comma-separated, e.g. [cyan]1,3,5[/cyan]) "
        "or [cyan]all[/cyan] / [cyan]none[/cyan]: "
    ).strip()

    if raw.lower() == "none":
        console.print("[yellow]No jobs selected. Skipping review and prep stages.[/yellow]")
        return None

    if raw.lower() == "all":
        selected_indices = list(range(len(jobs)))
    else:
        selected_indices = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(jobs):
                    selected_indices.append(idx)
        if not selected_indices:
            console.print("[yellow]No valid numbers entered. Skipping review and prep stages.[/yellow]")
            return None

    selected_jobs = [jobs[i] for i in selected_indices]

    # Write selected jobs to output/selected_jobs.md (used by review agent)
    selected_path = ROOT_DIR / "output" / "selected_jobs.md"
    selected_content = "\n\n---\n\n".join(block for _, block in selected_jobs)
    selected_path.write_text(selected_content)
    console.print(
        f"[green]✓[/green] {len(selected_jobs)} job(s) selected — "
        "saved to [cyan]output/selected_jobs.md[/cyan]"
    )

    # Append compact entries to data/liked_jobs.md for future search context
    liked_path = ROOT_DIR / "data" / "liked_jobs.md"
    today = date.today().isoformat()
    history_entries = []
    for label, block in selected_jobs:
        url_match = re.search(r"\*\*URL:\*\*\s*(.+)", block)
        why_match = re.search(r"\*\*Why it matches:\*\*\s*(.+)", block)
        url = url_match.group(1).strip() if url_match else "N/A"
        why = why_match.group(1).strip() if why_match else ""
        history_entries.append(f"- **{label}** (selected {today})\n  - URL: {url}\n  - Why: {why}")

    with liked_path.open("a") as f:
        if not liked_path.stat().st_size:
            f.write("# Previously Liked Jobs\n\nJobs you have selected in past searches.\n\n")
        f.write("\n".join(history_entries) + "\n")

    console.print("[green]✓[/green] History appended to [cyan]data/liked_jobs.md[/cyan]")
    return selected_path


async def run_pipeline(stage: str | None = None, top_n: int | None = None, cheap: bool = False) -> None:
    """Run the full pipeline or a specific stage."""
    ensure_output_dirs()

    cfg = CHEAP_CONFIG if cheap else DEFAULT_CONFIG
    effective_top_n = top_n if top_n is not None else cfg["top_n"]

    mode_label = "[yellow]CHEAP MODE[/yellow] (haiku)" if cheap else "[green]FULL MODE[/green] (opus)"
    console.print(Panel.fit(
        f"[bold cyan]Job Finder Over 9000[/bold cyan]  {mode_label}\n"
        "[dim]Multiagent job search pipeline[/dim]",
        border_style="cyan"
    ))

    run_search = stage in (None, "search")
    run_select = stage in (None, "select")
    run_review = stage in (None, "review")
    run_prep = stage in (None, "prep")

    stage_usages = []

    # Stage 1: Job Search
    if run_search:
        console.print("\n[bold yellow]Stage 1: Job Search Agent[/bold yellow]")
        console.print(f"[dim]Searching for up to {cfg['max_candidates']} jobs ({cfg['model']})...[/dim]")
        agent_result = await run_job_search_agent(
            model=cfg["model"],
            max_turns=cfg["search_turns"],
            min_candidates=cfg["min_candidates"],
            max_candidates=cfg["max_candidates"],
        )
        stage_usages.append(("Job Search", agent_result.usage))
        console.print("[green]✓[/green] Job candidates saved to [cyan]output/job_candidates.md[/cyan]")

    # Selection Step: user picks which candidates to keep
    candidates_path = ROOT_DIR / "output" / "job_candidates.md"
    selected_path = ROOT_DIR / "output" / "selected_jobs.md"

    if run_select:
        if not candidates_path.exists() and stage == "select":
            console.print(
                "[red]Error:[/red] output/job_candidates.md not found. "
                "Run the search stage first: python main.py --stage search"
            )
            return
        console.print("\n[bold yellow]Selection: Choose your candidates[/bold yellow]")
        result = select_jobs(candidates_path)
        if result is None and stage in (None, "select"):
            # User selected none — stop the pipeline
            return
        if result is not None:
            selected_path = result

    # Stage 2: Job Review
    if run_review:
        # Prefer selected jobs if available, fall back to all candidates
        review_input = selected_path if selected_path.exists() else candidates_path
        if not review_input.exists() and stage == "review":
            console.print(
                "[red]Error:[/red] No candidates file found. "
                "Run search + selection first: python main.py --stage search"
            )
            return

        console.print("\n[bold yellow]Stage 2: Job Review Agent[/bold yellow]")
        input_label = "selected_jobs.md" if review_input == selected_path else "job_candidates.md"
        console.print(f"[dim]Validating and ranking jobs from {input_label} ({cfg['model']})...[/dim]")
        agent_result = await run_job_review_agent(
            model=cfg["model"],
            max_turns=cfg["review_turns"],
            candidates_path=review_input,
        )
        stage_usages.append(("Job Review", agent_result.usage))
        console.print("[green]✓[/green] Ranked jobs saved to [cyan]output/ranked_jobs.md[/cyan]")

    # Stage 3: Job Prep
    if run_prep:
        ranked_path = ROOT_DIR / "output" / "ranked_jobs.md"
        if not ranked_path.exists() and stage == "prep":
            console.print(
                "[red]Error:[/red] output/ranked_jobs.md not found. "
                "Run the review stage first: python main.py --stage review"
            )
            return

        console.print(f"\n[bold yellow]Stage 3: Job Prep Agent[/bold yellow]")
        console.print(f"[dim]Creating tailored materials for top {effective_top_n} jobs ({cfg['model']})...[/dim]")
        agent_result = await run_job_prep_agent(
            top_n=effective_top_n,
            model=cfg["model"],
            max_turns=cfg["prep_turns"],
        )
        stage_usages.append(("Job Prep", agent_result.usage))
        console.print("[green]✓[/green] Prep materials saved to [cyan]output/prep/[/cyan]")

    console.print()
    if len(stage_usages) > 1:
        print_total_usage(stage_usages)
    console.print(Panel.fit(
        "[bold green]Pipeline complete![/bold green]\n\n"
        "Check the [cyan]output/[/cyan] directory for results:\n"
        "  • [cyan]output/job_candidates.md[/cyan]   — all found jobs\n"
        "  • [cyan]output/selected_jobs.md[/cyan]    — your selected jobs\n"
        "  • [cyan]output/ranked_jobs.md[/cyan]      — scored & ranked jobs\n"
        "  • [cyan]output/prep/[/cyan]                — tailored application materials",
        border_style="green"
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description="Job Finder Over 9000 — Multiagent job search")
    parser.add_argument(
        "--stage",
        choices=["search", "select", "review", "prep"],
        help="Run only a specific stage (default: run all stages)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Number of top jobs to prepare materials for (default: 5, or 1 in --cheap mode)",
    )
    parser.add_argument(
        "--cheap",
        action="store_true",
        help="Use claude-haiku-4-5 with reduced scope for cheap testing",
    )
    args = parser.parse_args()

    try:
        anyio.run(run_pipeline, args.stage, args.top, args.cheap)
    except HitLimit as err:
        console.print(err)


if __name__ == "__main__":
    main()
