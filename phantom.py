#!/usr/bin/env python3
"""
Phantom Vision — AI-powered image analysis CLI
Powered by Claude vision models
"""

import os
import sys
import json
import base64
import time
from pathlib import Path

import click
import anthropic
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

console = Console()

# ─── Helpers ────────────────────────────────────────────────────────────────

def load_image_as_b64(image_path: str) -> tuple[str, str]:
    """Load an image from disk and return (base64_data, media_type)."""
    path = Path(image_path)
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {image_path}")
        sys.exit(1)

    suffix = path.suffix.lower()
    media_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_map.get(suffix, "image/jpeg")

    # Auto-resize if image is very large (keeps tokens low)
    img = Image.open(path)
    max_dim = 1568
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        console.print(f"[dim]ℹ Resized to {img.size} to reduce token usage[/dim]")

    import io
    buffer = io.BytesIO()
    fmt = "JPEG" if media_type == "image/jpeg" else suffix.lstrip(".").upper()
    img.save(buffer, format=fmt)
    b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")
    return b64, media_type


def build_vision_message(b64: str, media_type: str, prompt: str) -> list:
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]


def call_claude(messages: list, model: str, max_tokens: int = 1024) -> tuple:
    """Send messages to Claude and return (text, usage)."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    t0 = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
    )
    elapsed = time.time() - t0
    text = response.content[0].text
    usage = response.usage
    return text, usage, elapsed


# ─── CLI ────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="phantom")
def cli():
    """👁️  Phantom Vision — AI image analysis powered by Claude."""
    pass


@cli.command()
@click.argument("image_path")
@click.option("--model", default="claude-opus-4-6", help="Claude model")
@click.option("--verbose", is_flag=True, help="Show token usage")
def describe(image_path, model, verbose):
    """Get a rich natural language description of an image."""
    console.print("[bold cyan]👁  Phantom Vision[/bold cyan] — Analyzing image...\n")
    b64, mt = load_image_as_b64(image_path)
    prompt = (
        "Describe this image in vivid, rich detail. Cover the main subject, "
        "background, colors, mood, lighting, and any notable elements. "
        "Write 2–4 compelling paragraphs."
    )
    messages = build_vision_message(b64, mt, prompt)
    text, usage, elapsed = call_claude(messages, model, max_tokens=1024)
    console.print(Panel(Markdown(text), title="📝 Description", border_style="cyan"))
    if verbose:
        console.print(f"[dim]Tokens: {usage.input_tokens} in / {usage.output_tokens} out | {elapsed:.2f}s[/dim]")


@cli.command()
@click.argument("image_path")
@click.option("--model", default="claude-opus-4-6", help="Claude model")
@click.option("--output", type=click.Choice(["text", "json"]), default="text")
@click.option("--verbose", is_flag=True)
def tag(image_path, model, output, verbose):
    """Auto-generate semantic tags for an image."""
    console.print("[bold cyan]👁  Phantom Vision[/bold cyan] — Generating tags...\n")
    b64, mt = load_image_as_b64(image_path)
    prompt = (
        "Generate a comprehensive list of semantic tags for this image. "
        "Include tags for: objects, scene type, colors, mood/emotion, style, "
        "time of day if applicable, and any text visible. "
        "Return ONLY a JSON array of lowercase strings, no explanation."
    )
    messages = build_vision_message(b64, mt, prompt)
    text, usage, elapsed = call_claude(messages, model, max_tokens=512)

    try:
        tags = json.loads(text.strip())
    except json.JSONDecodeError:
        # Fallback: extract comma-separated words
        tags = [t.strip().strip('"') for t in text.split(",")]

    if output == "json":
        click.echo(json.dumps(tags, indent=2))
    else:
        tag_str = "  ".join(f"[green]#{t}[/green]" for t in tags)
        console.print(Panel(tag_str, title="🏷️ Tags", border_style="green"))

    if verbose:
        console.print(f"[dim]Tokens: {usage.input_tokens} in / {usage.output_tokens} out | {elapsed:.2f}s[/dim]")


@cli.command()
@click.argument("image_path")
@click.argument("question")
@click.option("--model", default="claude-opus-4-6", help="Claude model")
@click.option("--verbose", is_flag=True)
def ask(image_path, question, model, verbose):
    """Ask a specific question about an image."""
    console.print("[bold cyan]👁  Phantom Vision[/bold cyan] — Thinking...\n")
    b64, mt = load_image_as_b64(image_path)
    prompt = f"Look at this image carefully and answer the following question:\n\n{question}"
    messages = build_vision_message(b64, mt, prompt)
    text, usage, elapsed = call_claude(messages, model, max_tokens=768)
    console.print(Panel(Markdown(text), title=f"❓ {question}", border_style="magenta"))
    if verbose:
        console.print(f"[dim]Tokens: {usage.input_tokens} in / {usage.output_tokens} out | {elapsed:.2f}s[/dim]")


@cli.command()
@click.argument("image_path")
@click.option("--model", default="claude-opus-4-6", help="Claude model")
@click.option("--output", type=click.Choice(["text", "json"]), default="text")
@click.option("--verbose", is_flag=True)
def analyze(image_path, model, output, verbose):
    """Full structured analysis of an image."""
    console.print("[bold cyan]👁  Phantom Vision[/bold cyan] — Deep analysis...\n")
    b64, mt = load_image_as_b64(image_path)
    prompt = (
        "Perform a comprehensive structured analysis of this image. "
        "Return a JSON object with these keys:\n"
        "  - scene: overall scene description (string)\n"
        "  - objects: list of detected objects [{name, confidence: high/med/low}]\n"
        "  - dominant_colors: top 5 colors as hex codes\n"
        "  - mood: emotional tone (string)\n"
        "  - composition: photographic/artistic composition notes\n"
        "  - text_detected: any visible text (list of strings, or empty list)\n"
        "  - quality: image quality assessment (string)\n"
        "  - tags: 10 descriptive tags (list of strings)\n"
        "Return ONLY valid JSON, no markdown fences, no explanation."
    )
    messages = build_vision_message(b64, mt, prompt)
    text, usage, elapsed = call_claude(messages, model, max_tokens=1500)

    try:
        data = json.loads(text.strip())
        if output == "json":
            click.echo(json.dumps(data, indent=2))
        else:
            console.print(Panel(
                Markdown(f"```json\n{json.dumps(data, indent=2)}\n```"),
                title="📊 Full Analysis",
                border_style="yellow"
            ))
    except json.JSONDecodeError:
        console.print(Panel(text, title="📊 Analysis", border_style="yellow"))

    if verbose:
        console.print(f"[dim]Tokens: {usage.input_tokens} in / {usage.output_tokens} out | {elapsed:.2f}s[/dim]")


@cli.command()
@click.argument("directory")
@click.option("--mode", type=click.Choice(["describe", "tag", "analyze"]), default="describe")
@click.option("--model", default="claude-opus-4-6", help="Claude model")
def batch(directory, mode, model):
    """Process all images in a directory."""
    dir_path = Path(directory)
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    images = [f for f in dir_path.iterdir() if f.suffix.lower() in extensions]

    if not images:
        console.print(f"[red]No images found in {directory}[/red]")
        sys.exit(1)

    console.print(f"[bold cyan]👁  Phantom Vision[/bold cyan] — Batch mode ({len(images)} images)\n")
    results = {}

    for img_path in images:
        console.print(f"[dim]Processing {img_path.name}...[/dim]")
        try:
            b64, mt = load_image_as_b64(str(img_path))
            prompts = {
                "describe": "Describe this image in 2 sentences.",
                "tag": "Return a JSON array of 8 tags for this image. No explanation.",
                "analyze": "Return a JSON object with: scene, mood, and tags (list). No explanation.",
            }
            messages = build_vision_message(b64, mt, prompts[mode])
            text, _, _ = call_claude(messages, model, max_tokens=512)
            results[img_path.name] = text
            console.print(f"[green]✓[/green] {img_path.name}")
        except Exception as e:
            results[img_path.name] = f"ERROR: {e}"
            console.print(f"[red]✗[/red] {img_path.name}: {e}")

    output_file = dir_path / "phantom_results.json"
    output_file.write_text(json.dumps(results, indent=2))
    console.print(f"\n[bold green]✅ Done![/bold green] Results saved to {output_file}")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
