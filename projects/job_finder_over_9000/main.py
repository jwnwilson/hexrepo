"""
Job Finder Over 9000 — Main Orchestrator

Runs the three-stage multiagent job finding pipeline:
  1. Job Search Agent   — finds job candidates online
  2. Job Review Agent   — validates and ranks candidates
  3. Job Prep Agent     — creates tailored application materials

Usage:
    python main.py                  # Run full pipeline (Opus, full scope)
    python main.py --cheap          # Run with Haiku + reduced scope (for testing)
    python main.py --stage search   # Run only job search
    python main.py --stage review   # Run only job review
    python main.py --stage prep     # Run only job prep
    python main.py --top 3          # Prep materials for top 3 jobs (default: 5)

Cost modes:
    Default  — claude-opus-4-6, 15 candidates, top 5 prep
    --cheap  — claude-haiku-4-5, 5 candidates, top 1 prep, reduced turns
"""

import argparse
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
    "max_candidates": 5,
    "top_n": 1,
    "search_turns": 15,
    "review_turns": 15,
    "prep_turns": 20,
}

DEFAULT_CONFIG = {
    "model": "claude-opus-4-6",
    "max_candidates": 15,
    "top_n": 5,
    "search_turns": 50,
    "review_turns": 60,
    "prep_turns": 100,
}


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
    run_review = stage in (None, "review")
    run_prep = stage in (None, "prep")

    stage_usages = []
    
    # Stage 1: Job Search
    if run_search:
        console.print("\n[bold yellow]Stage 1/3: Job Search Agent[/bold yellow]")
        console.print(f"[dim]Searching for up to {cfg['max_candidates']} jobs ({cfg['model']})...[/dim]")
        agent_result = await run_job_search_agent(
            model=cfg["model"],
            max_turns=cfg["search_turns"],
            max_candidates=cfg["max_candidates"],
        )
        stage_usages.append(("Job Search", agent_result.usage))
        console.print("[green]✓[/green] Job candidates saved to [cyan]output/job_candidates.md[/cyan]")

    # Stage 2: Job Review
    if run_review:
        candidates_path = ROOT_DIR / "output" / "job_candidates.md"
        if not candidates_path.exists() and stage == "review":
            console.print(
                "[red]Error:[/red] output/job_candidates.md not found. "
                "Run the search stage first: python main.py --stage search"
            )
            return

        console.print("\n[bold yellow]Stage 2/3: Job Review Agent[/bold yellow]")
        console.print(f"[dim]Validating jobs are open and ranking by match score ({cfg['model']})...[/dim]")
        agent_result = await run_job_review_agent(
            model=cfg["model"],
            max_turns=cfg["review_turns"],
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

        console.print(f"\n[bold yellow]Stage 3/3: Job Prep Agent[/bold yellow]")
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
        "  • [cyan]output/job_candidates.md[/cyan]  — all found jobs\n"
        "  • [cyan]output/ranked_jobs.md[/cyan]     — scored & ranked jobs\n"
        "  • [cyan]output/prep/[/cyan]               — tailored application materials",
        border_style="green"
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description="Job Finder Over 9000 — Multiagent job search")
    parser.add_argument(
        "--stage",
        choices=["search", "review", "prep"],
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
