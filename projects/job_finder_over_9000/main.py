"""
Job Finder Over 9000 — Main Orchestrator

Runs the three-stage multiagent job finding pipeline:
  1. Job Search Agent   — finds job candidates online
  2. Job Review Agent   — validates and ranks candidates
  3. Job Prep Agent     — creates tailored application materials

Usage:
    python main.py                  # Run full pipeline
    python main.py --stage search   # Run only job search
    python main.py --stage review   # Run only job review
    python main.py --stage prep     # Run only job prep
    python main.py --top 3          # Prep materials for top 3 jobs (default: 5)
"""

import argparse
import anyio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agents import run_job_search_agent, run_job_review_agent, run_job_prep_agent

ROOT_DIR = Path(__file__).parent
console = Console()


def ensure_output_dirs() -> None:
    """Create output directories if they don't exist."""
    (ROOT_DIR / "output").mkdir(exist_ok=True)
    (ROOT_DIR / "output" / "prep").mkdir(exist_ok=True)


async def run_pipeline(stage: str | None = None, top_n: int = 5) -> None:
    """Run the full pipeline or a specific stage."""
    ensure_output_dirs()

    console.print(Panel.fit(
        "[bold cyan]Job Finder Over 9000[/bold cyan]\n"
        "[dim]Multiagent job search pipeline[/dim]",
        border_style="cyan"
    ))

    run_search = stage in (None, "search")
    run_review = stage in (None, "review")
    run_prep = stage in (None, "prep")

    # Stage 1: Job Search
    if run_search:
        console.print("\n[bold yellow]Stage 1/3: Job Search Agent[/bold yellow]")
        console.print("[dim]Searching the web for matching job opportunities...[/dim]")
        result = await run_job_search_agent()
        console.print(f"[green]✓[/green] Job candidates saved to [cyan]output/job_candidates.md[/cyan]")
        if result:
            console.print(f"[dim]{result[:200]}...[/dim]" if len(result) > 200 else f"[dim]{result}[/dim]")

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
        console.print("[dim]Validating jobs are open and ranking by match score...[/dim]")
        result = await run_job_review_agent()
        console.print(f"[green]✓[/green] Ranked jobs saved to [cyan]output/ranked_jobs.md[/cyan]")
        if result:
            console.print(f"[dim]{result[:200]}...[/dim]" if len(result) > 200 else f"[dim]{result}[/dim]")

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
        console.print(f"[dim]Creating tailored materials for top {top_n} jobs...[/dim]")
        result = await run_job_prep_agent(top_n=top_n)
        console.print(f"[green]✓[/green] Prep materials saved to [cyan]output/prep/[/cyan]")
        if result:
            console.print(f"[dim]{result[:200]}...[/dim]" if len(result) > 200 else f"[dim]{result}[/dim]")

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
        default=5,
        help="Number of top jobs to prepare materials for (default: 5)",
    )
    args = parser.parse_args()

    anyio.run(run_pipeline, args.stage, args.top)


if __name__ == "__main__":
    main()
