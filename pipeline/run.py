"""
Accountability Ledger — pipeline runner.

Usage:
    python -m pipeline.run [--entities data/entities.csv] [--output data/output/ledger.json]

Run `python -m pipeline.run --help` for options.
"""
import argparse
import logging
import sys
from pathlib import Path

from pipeline.assemble.assembler import Assembler


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Accountability Ledger curation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps before running:
  1. Download raw data files — see data/raw/README.md for instructions per source.
  2. Create or populate data/entities.csv (see data/entities_template.csv).
  3. Run this script; output lands in data/output/ledger.json.
  4. Open frontend/index.html in a browser to explore the results.
        """,
    )
    parser.add_argument(
        "--entities",
        default="data/entities.csv",
        help="Path to entity list CSV (default: data/entities.csv)",
    )
    parser.add_argument(
        "--output",
        default="data/output/ledger.json",
        help="Path for output JSON (default: data/output/ledger.json)",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Directory containing raw source data (default: data/raw)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s — %(message)s",
    )

    try:
        assembler = Assembler(raw_dir=Path(args.raw_dir))
        records = assembler.run(entity_list_path=Path(args.entities))
        Assembler.write(records, output_path=Path(args.output))
        print(f"\nDone. {len(records)} records written to {args.output}")
        print(f"Open frontend/index.html in a browser to explore.")
        return 0
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logging.exception("Pipeline failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
