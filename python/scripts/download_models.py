from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download
from rich.console import Console
from rich.progress import Progress

from warehouse.config import load_config
from warehouse.embeddings import model_directory

console = Console()


def download_model(model_name: str, target_dir: Path) -> None:
    console.print(f"[bold cyan]Downloading {model_name}[/bold cyan] -> {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)

    with Progress() as progress:
        task = progress.add_task("Fetching", total=None)
        snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        progress.update(task, completed=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download embedding models to local cache")
    parser.add_argument(
        "--model",
        action="append",
        help="Optional Hugging Face model name to download (defaults to configured models)",
    )
    args = parser.parse_args()

    cfg = load_config()
    targets = args.model or [cfg.models.primary, cfg.models.secondary]

    for model_name in targets:
        path = model_directory(model_name, cfg.paths.model_cache_dir)
        download_model(model_name, path)

    console.print("[green]Download complete[/green]")


if __name__ == "__main__":
    main()
