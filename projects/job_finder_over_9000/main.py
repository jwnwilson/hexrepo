"""
Job Finder Over 9000 — Main Orchestrator

Runs the three-stage multiagent job finding pipeline:
  1. Job Search Agent   — finds job candidates online
  2. Selection Step     — you pick which candidates to keep
  3. Job Review Agent   — validates and ranks selected candidates
  4. Job Prep Agent     — creates tailored application materials

Usage:
    python main.py                  # Run full pipeline (auto-resumes from last checkpoint)
    python main.py --fresh          # Re-run full pipeline from scratch
    python main.py --cheap          # Run with Haiku + reduced scope (for testing)
    python main.py --stage search   # Run only job search
    python main.py --stage select   # Run only selection step
    python main.py --stage review   # Run only job review
    python main.py --stage prep     # Run only job prep (skips companies already prepped)
    python main.py --status         # Show pipeline status and exit

Cost modes:
    Default  — claude-opus-4-6, 15 candidates
    --cheap  — claude-haiku-4-5, 5 candidates, reduced turns
"""

import argparse
import re
from datetime import date, datetime
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

# Ordered pipeline stages with their output file/dir markers
STAGES = [
    {"key": "search",  "label": "Search",    "output": ROOT_DIR / "output" / "job_candidates.md"},
    {"key": "select",  "label": "Selection", "output": ROOT_DIR / "output" / "selected_jobs.md"},
    {"key": "review",  "label": "Review",    "output": ROOT_DIR / "output" / "ranked_jobs.md"},
    {"key": "prep",    "label": "Prep",      "output": ROOT_DIR / "output" / "prep"},
]


def _stage_complete(stage: dict) -> bool:
    """Return True if a stage's output already exists."""
    path: Path = stage["output"]
    if path.suffix == "":  # directory
        return path.is_dir() and any(path.glob("*.md"))
    return path.exists()


def _file_mtime(path: Path) -> str:
    """Return a short human-readable modification time for a file/dir."""
    target = path
    if path.is_dir():
        files = sorted(path.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            return ""
        target = files[0]
    try:
        ts = datetime.fromtimestamp(target.stat().st_mtime)
        return ts.strftime("%d %b %H:%M")
    except OSError:
        return ""


def print_pipeline_status() -> None:
    """Print a summary of which pipeline stages are complete."""
    lines = []
    for s in STAGES:
        done = _stage_complete(s)
        if done:
            ts = _file_mtime(s["output"])
            lines.append(f"  [green]✓[/green] {s['label']:<12} [dim]{ts}[/dim]")
        else:
            lines.append(f"  [dim]○[/dim] {s['label']:<12} [dim]not started[/dim]")
    console.print(Panel(
        "\n".join(lines),
        title="[bold]Pipeline Status[/bold]",
        border_style="cyan",
        padding=(0, 1),
    ))


def _parse_job_blocks(candidates_path: Path) -> list[tuple[str, str]]:
    """
    Parse job_candidates.md into a list of (header, full_block) tuples.
    Each block is everything from '## Title' up to (not including) the next '## '.
    Returns list of (display_label, markdown_block).
    """
    text = candidates_path.read_text()
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


async def run_pipeline(
    stage: str | None = None,
    cheap: bool = False,
    fresh: bool = False,
) -> None:
    """Run the full pipeline or a specific stage."""
    ensure_output_dirs()

    cfg = CHEAP_CONFIG if cheap else DEFAULT_CONFIG

    mode_label = "[yellow]CHEAP MODE[/yellow] (haiku)" if cheap else "[green]FULL MODE[/green] (opus)"
    console.print(Panel.fit(
        f"[bold cyan]Job Finder Over 9000[/bold cyan]  {mode_label}\n"
        "[dim]Multiagent job search pipeline[/dim]",
        border_style="cyan"
    ))

    # Show current pipeline status before running
    print_pipeline_status()

    # When running the full pipeline, auto-skip completed stages unless --fresh
    # When a specific --stage is given, always run it (user explicitly requested)
    full_pipeline = stage is None

    def should_run(key: str) -> bool:
        if stage is not None:
            return stage == key
        if fresh:
            return True
        stage_def = next(s for s in STAGES if s["key"] == key)
        return not _stage_complete(stage_def)

    if full_pipeline and not fresh:
        pending = [s["label"] for s in STAGES if not _stage_complete(s)]
        if not pending:
            console.print("\n[green]All stages complete.[/green] Use [cyan]--fresh[/cyan] to re-run.\n")
            return
        console.print(
            f"\n[dim]Resuming from:[/dim] [bold]{pending[0]}[/bold]"
            f"  [dim](use --fresh to re-run from scratch)[/dim]\n"
        )

    stage_usages = []

    # Stage 1: Job Search
    if should_run("search"):
        console.print("[bold yellow]Stage 1: Job Search Agent[/bold yellow]")
        console.print(f"[dim]Searching for up to {cfg['max_candidates']} jobs ({cfg['model']})...[/dim]")
        agent_result = await run_job_search_agent(
            model=cfg["model"],
            max_turns=cfg["search_turns"],
            min_candidates=cfg["min_candidates"],
            max_candidates=cfg["max_candidates"],
        )
        stage_usages.append(("Job Search", agent_result.usage))
        console.print("[green]✓[/green] Job candidates saved to [cyan]output/job_candidates.md[/cyan]\n")
    elif full_pipeline:
        console.print("[dim]Stage 1: Search — skipping (output/job_candidates.md exists)[/dim]")

    # Selection Step
    candidates_path = ROOT_DIR / "output" / "job_candidates.md"
    selected_path = ROOT_DIR / "output" / "selected_jobs.md"

    if should_run("select"):
        if not candidates_path.exists():
            console.print(
                "[red]Error:[/red] output/job_candidates.md not found. "
                "Run the search stage first: python main.py --stage search"
            )
            return
        console.print("[bold yellow]Selection: Choose your candidates[/bold yellow]")
        result = select_jobs(candidates_path)
        if result is None:
            return
        selected_path = result
        console.print()
    elif full_pipeline:
        console.print("[dim]Selection — skipping (output/selected_jobs.md exists)[/dim]")

    # Stage 2: Job Review
    if should_run("review"):
        review_input = selected_path if selected_path.exists() else candidates_path
        if not review_input.exists():
            console.print(
                "[red]Error:[/red] No candidates file found. "
                "Run search and selection first."
            )
            return

        console.print("[bold yellow]Stage 2: Job Review Agent[/bold yellow]")
        input_label = "selected_jobs.md" if review_input == selected_path else "job_candidates.md"
        console.print(f"[dim]Validating and ranking jobs from {input_label} ({cfg['model']})...[/dim]")
        agent_result = await run_job_review_agent(
            model=cfg["model"],
            max_turns=cfg["review_turns"],
            candidates_path=review_input,
        )
        stage_usages.append(("Job Review", agent_result.usage))
        console.print("[green]✓[/green] Ranked jobs saved to [cyan]output/ranked_jobs.md[/cyan]\n")
    elif full_pipeline:
        console.print("[dim]Stage 2: Review — skipping (output/ranked_jobs.md exists)[/dim]")

    # Stage 3: Job Prep
    if should_run("prep"):
        ranked_path = ROOT_DIR / "output" / "ranked_jobs.md"
        if not ranked_path.exists():
            console.print(
                "[red]Error:[/red] output/ranked_jobs.md not found. "
                "Run the review stage first: python main.py --stage review"
            )
            return

        console.print("[bold yellow]Stage 3: Job Prep Agent[/bold yellow]")
        console.print(f"[dim]Creating tailored materials for top {effective_top_n} jobs ({cfg['model']})...[/dim]")
        agent_result = await run_job_prep_agent(
            top_n=effective_top_n,
            model=cfg["model"],
            max_turns=cfg["prep_turns"],
        )
        stage_usages.append(("Job Prep", agent_result.usage))
        console.print("[green]✓[/green] Prep materials saved to [cyan]output/prep/[/cyan]\n")
    elif full_pipeline:
        console.print("[dim]Stage 3: Prep — skipping (output/prep/ has files)[/dim]")

    console.print()
    if len(stage_usages) > 1:
        print_total_usage(stage_usages)

    # Final status panel
    print_pipeline_status()


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
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Re-run all stages from scratch, ignoring existing output files",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show pipeline status and exit",
    )
    args = parser.parse_args()

    if args.status:
        ensure_output_dirs()
        print_pipeline_status()
        return

    try:
        anyio.run(run_pipeline, args.stage, args.top, args.cheap, args.fresh)
    except HitLimit as err:
        console.print(err)


if __name__ == "__main__":
    main()
