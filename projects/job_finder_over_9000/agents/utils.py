"""Shared utilities for agent streaming and output."""

from dataclasses import dataclass, field
from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ClaudeAgentOptions,
    query,
)
from rich.console import Console
from rich.rule import Rule
from rich.table import Table

console = Console()

# Tool name -> friendly label
TOOL_LABELS: dict[str, str] = {
    "WebSearch": "searching",
    "WebFetch": "fetching",
    "Read": "reading",
    "Write": "writing",
    "Edit": "editing",
    "Bash": "running",
    "Glob": "globbing",
    "Grep": "grepping",
}

# Pricing per 1M tokens: (input, output, cache_write, cache_read)
PRICING: dict[str, tuple[float, float, float, float]] = {
    "claude-opus-4-6":   (5.00,  25.00, 6.25,  0.50),
    "claude-sonnet-4-6": (3.00,  15.00, 3.75,  0.30),
    "claude-haiku-4-5":  (1.00,   5.00, 1.25,  0.10),
}


@dataclass
class UsageSummary:
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0

    def add(self, usage: dict) -> None:  # type: ignore[type-arg]
        self.input_tokens += usage.get("input_tokens", 0)
        self.output_tokens += usage.get("output_tokens", 0)
        self.cache_creation_tokens += usage.get("cache_creation_input_tokens", 0)
        self.cache_read_tokens += usage.get("cache_read_input_tokens", 0)

    def cost(self) -> float:
        prices = PRICING.get(self.model, PRICING["claude-opus-4-6"])
        input_price, output_price, cache_write_price, cache_read_price = prices
        return (
            self.input_tokens * input_price / 1_000_000
            + self.output_tokens * output_price / 1_000_000
            + self.cache_creation_tokens * cache_write_price / 1_000_000
            + self.cache_read_tokens * cache_read_price / 1_000_000
        )

    def __iadd__(self, other: "UsageSummary") -> "UsageSummary":
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_creation_tokens += other.cache_creation_tokens
        self.cache_read_tokens += other.cache_read_tokens
        return self


@dataclass
class AgentResult:
    result: str
    usage: UsageSummary


class HitLimit(Exception):
    ...


async def stream_agent(
    name: str,
    prompt: str,
    options: ClaudeAgentOptions,
) -> AgentResult:
    """
    Run an agent and stream live output to the terminal.

    Prints:
    - Tool calls as they happen (tool name + key input detail)
    - Claude's text responses as they arrive
    - A usage/cost summary on completion

    Returns AgentResult with the final result text and token usage.
    """
    console.print(Rule(f"[bold cyan]{name}[/bold cyan]", style="cyan"))

    model = options.model or "claude-opus-4-6"
    usage = UsageSummary(model=model)
    result_text = ""

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                if message.usage:
                    usage.add(message.usage)
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        console.print(f"[dim]{block.text.strip()}[/dim]")
                    elif isinstance(block, ToolUseBlock):
                        _print_tool_call(block)

            elif isinstance(message, ResultMessage):
                result_text = message.result
                console.print(Rule(style="green"))
                _print_usage(name, usage)
    except Exception as err:
        if message and hasattr(message, "result") and "You've hit your limit" in message.result:
            raise HitLimit(message.result)
        else:
            console.print(f"Error: {err}")
            raise

    return AgentResult(result=result_text, usage=usage)


def print_total_usage(stage_usages: list[tuple[str, UsageSummary]]) -> None:
    """Print a grand total cost table across all stages."""
    if not stage_usages:
        return

    table = Table(title="Token Usage & Cost", border_style="cyan", show_footer=True)
    table.add_column("Agent", style="cyan")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache R/W", justify="right")
    table.add_column("Cost (£)", justify="right", style="green", footer="Total")

    totals = UsageSummary(model=stage_usages[0][1].model)
    total_cost = 0.0

    for stage_name, u in stage_usages:
        cost = u.cost()
        total_cost += cost
        totals += u
        table.add_row(
            stage_name,
            f"{u.input_tokens:,}",
            f"{u.output_tokens:,}",
            f"{u.cache_read_tokens:,} / {u.cache_creation_tokens:,}",
            f"£{cost:.4f}",
        )

    table.columns[4].footer = f"[bold green]£{total_cost:.4f}[/bold green]"
    console.print(table)


def _print_usage(name: str, usage: UsageSummary) -> None:
    cost = usage.cost()
    console.print(
        f"[green]✓ {name} complete[/green]  "
        f"[dim]in={usage.input_tokens:,} out={usage.output_tokens:,} "
        f"cost=[bold]£{cost:.4f}[/bold][/dim]"
    )


def _print_tool_call(block: ToolUseBlock) -> None:
    tool = block.name
    label = TOOL_LABELS.get(tool, tool.lower())
    detail = _tool_detail(tool, block.input)
    console.print(f"  [yellow]→[/yellow] [bold]{label}[/bold] [dim]{detail}[/dim]")


def _tool_detail(tool: str, inp: dict) -> str:  # type: ignore[type-arg]
    if tool == "WebSearch":
        return inp.get("query", "")
    if tool == "WebFetch":
        url = inp.get("url", "")
        return url[:80] + "…" if len(url) > 80 else url
    if tool in ("Read", "Write", "Edit"):
        path = inp.get("file_path", inp.get("path", ""))
        return path.split("/")[-1] if path else ""
    if tool == "Bash":
        cmd = inp.get("command", "")
        return cmd[:80] + "…" if len(cmd) > 80 else cmd
    if tool in ("Glob", "Grep"):
        return inp.get("pattern", inp.get("query", ""))
    return ""