from __future__ import annotations

from rich.console import Console

from warehouse import config
from warehouse import crud_tabular
from warehouse import crud_vector
from warehouse import crud_s3
from warehouse.datasets import load_vector_items

console = Console()


def main() -> None:
    cfg = config.load_config()

    console.rule("ClickHouse Bootstrap")

    console.print("[bold]Setting up tabular table[/bold]")
    crud_tabular.ensure_table(config=cfg)
    inserted = crud_tabular.load_sample_data(config=cfg)
    console.print(f"Loaded {inserted} tabular records")

    console.print("[bold]Setting up vector table[/bold]")
    try:
        vector_records = list(load_vector_items(config=cfg))
    except FileNotFoundError as exc:
        console.print(f"[red]Vector dataset missing:[/red] {exc}")
        console.print("Run python python/scripts/generate_vector_dataset.py before bootstrapping.")
        raise SystemExit(1) from exc

    crud_vector.ensure_table(config=cfg, records=vector_records)
    vectors = crud_vector.load_sample_vectors(config=cfg, records=vector_records)
    console.print(f"Loaded {vectors} vector records")

    console.print("[bold]Staging S3 dataset[/bold]")
    key = crud_s3.stage_sample_dataset(config=cfg)
    console.print(f"Uploaded sample dataset to s3://{cfg.s3.bucket}/{key}")

    console.print("[bold]Creating mapped S3 table[/bold]")
    crud_s3.create_s3_mapped_table(config=cfg)
    console.print("S3 table available as `s3_events`")

    console.print("[green]Bootstrap complete[/green]")


if __name__ == "__main__":
    main()
