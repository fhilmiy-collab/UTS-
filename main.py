"""Titik masuk Student Data Analyzer.

Mode menu  : python main.py
Mode batch : python main.py --batch --input data/mahasiswa_input.csv --output output
"""

import argparse
import sys

from studentapp import cli, logging_setup, pipeline
from studentapp.exceptions import StudentError


def build_parser():
    parser = argparse.ArgumentParser(description="Student Data Analyzer (UTS TK091)")
    parser.add_argument("--batch", action="store_true", help="jalankan tanpa menu")
    parser.add_argument("--input", default=cli.DEFAULT_INPUT, help="file .csv/.json")
    parser.add_argument("--output", default=cli.DEFAULT_OUTPUT_DIR, help="folder hasil")
    parser.add_argument("--debug", action="store_true", help="log level DEBUG")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    logging_setup.setup_logging(args.debug)
    try:
        if args.batch:
            return pipeline.run_batch(args.input, args.output)
        return cli.run_menu()
    except StudentError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nDibatalkan pengguna.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
