"""Shared utilities for agent streaming and output."""

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


async def stream_agent(
    name: str,
    prompt: str,
    options: ClaudeAgentOptions,
) -> str:
    """
    Run an agent and stream live output to the terminal.

    Prints:
    - Tool calls as they happen (tool name + key input detail)
    - Claude's text responses as they arrive
    - A final result summary

    Returns the ResultMessage.result string.
    """
    console.print(Rule(f"[bold cyan]{name}[/bold cyan]", style="cyan"))

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    console.print(f"[dim]{block.text.strip()}[/dim]")
                elif isinstance(block, ToolUseBlock):
                    _print_tool_call(block)

        elif isinstance(message, ResultMessage):
            result_text = message.result
            console.print(Rule(style="green"))
            console.print(f"[green]✓ {name} complete[/green]")

    return result_text


def _print_tool_call(block: ToolUseBlock) -> None:
    """Print a single tool call with its key input as a short label."""
    tool = block.name
    label = TOOL_LABELS.get(tool, tool.lower())
    detail = _tool_detail(tool, block.input)
    console.print(f"  [yellow]→[/yellow] [bold]{label}[/bold] [dim]{detail}[/dim]")


def _tool_detail(tool: str, inp: dict) -> str:  # type: ignore[type-arg]
    """Extract the most useful single line of detail from tool input."""
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
