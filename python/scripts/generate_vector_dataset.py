from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from warehouse.config import load_config
from warehouse.datasets import VECTOR_DATASET_FILENAME
from warehouse.embeddings import embed_texts

console = Console()


DUMMY_ITEMS = [
    {"category": "electronics", "text": "Wireless noise-cancelling headphones with 40-hour battery life."},
    {"category": "apparel", "text": "Breathable running shoes designed for marathon training on city streets."},
    {"category": "home", "text": "Smart thermostat that learns household schedules to optimize heating and cooling."},
    {"category": "books", "text": "A science-fiction novel following explorers establishing the first colony on Mars."},
    {"category": "beauty", "text": "Vitamin C face serum targeting uneven skin tone and early-aging signs."},
]


def write_jsonl(records: list[dict], path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Target file {path} already exists. Use --overwrite to regenerate.")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_preview_table(records: list[dict]) -> Table:
    table = Table(title="Vector Dataset Preview")
    table.add_column("item_id", justify="right")
    table.add_column("category")
    table.add_column("text")
    table.add_column("vector-dim", justify="right")

    for record in records:
        table.add_row(
            str(record["item_id"]),
            record["category"],
            record["text"],
            str(len(record["vector"])),
        )
    return table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the vector dataset JSONL using the active embedding model.")
    parser.add_argument(
        "--model",
        help="Optional Hugging Face model name to override ACTIVE_EMBEDDING_MODEL.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path (defaults to assets/data/vector_items.jsonl).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing dataset file.",
    )
    args = parser.parse_args()

    cfg = load_config()
    model_name = args.model or cfg.models.active

    console.print(f"[bold cyan]Using embedding model:[/bold cyan] {model_name}")

    try:
        vectors = embed_texts((item["text"] for item in DUMMY_ITEMS), model_name=model_name, config=cfg)
    except FileNotFoundError as exc:
        console.print(f"[red]Embedding model not found:[/red] {exc}")
        console.print("Run python python/scripts/download_models.py to populate assets/models.")
        raise SystemExit(1) from exc

    records: list[dict] = []
    for idx, (item, vector) in enumerate(zip(DUMMY_ITEMS, vectors), start=1):
        records.append(
            {
                "item_id": idx,
                "category": item["category"],
                "text": item["text"],
                "model": model_name,
                "vector": [float(v) for v in vector],
            }
        )

    output_path = args.output or (cfg.paths.data_dir / VECTOR_DATASET_FILENAME)
    write_jsonl(records, output_path, overwrite=args.overwrite)

    console.print(f"[green]Vector dataset written to[/green] {output_path}")
    console.print(build_preview_table(records))


if __name__ == "__main__":
    main()
