from __future__ import annotations

from rich.console import Console
from rich.table import Table

from warehouse import config
from warehouse import crud_tabular
from warehouse import crud_vector
from warehouse import crud_s3
from warehouse.datasets import load_vector_items

console = Console()


def display_rows(title: str, rows) -> None:
    materialized = list(rows)
    table = Table(title=title)
    if not materialized:
        console.print(f"[yellow]No rows returned for {title}[/yellow]")
        return

    # Infer columns from first row
    for idx in range(len(materialized[0])):
        table.add_column(f"col_{idx}")

    for row in materialized:
        table.add_row(*[str(col) for col in row])

    console.print(table)


def main() -> None:
    cfg = config.load_config()

    console.rule("ClickHouse CRUD Demo")

    console.print("[bold]Tabular dataset[/bold]")
    rows = crud_tabular.fetch_events(limit=10, config=cfg)
    display_rows("events", rows)

    console.print("[bold]Vector similarity[/bold]")
    try:
        records = list(load_vector_items(config=cfg))
    except FileNotFoundError:
        console.print(
            "[yellow]Vector dataset not found. Run python python/scripts/generate_vector_dataset.py first.[/yellow]"
        )
    else:
        if records:
            query_vector = records[0].vector
            matches = crud_vector.similarity_search(query_vector, config=cfg)
            display_rows("vector matches", matches)
        else:
            console.print("[yellow]No vector data available[/yellow]")

    console.print("[bold]S3-backed dataset[/bold]")
    crud_s3.create_s3_mapped_table(config=cfg)
    s3_rows = crud_s3.query_s3_dataset(config=cfg)
    display_rows("s3 events (function)", s3_rows)

    console.print("[green]CRUD demo complete[/green]")


if __name__ == "__main__":
    main()
