#!.venv/bin/python

import argparse
import sys


from lexer import LexError, lex


parser = argparse.ArgumentParser(
    prog="cobrac", description="A hobby C compiler in Python", epilog=""
)

parser.add_argument("input")
parser.add_argument("--lex", action="store_true")
parser.add_argument("--parse", action="store_true")
parser.add_argument("--codegen", action="store_true")
parser.add_argument("--verbose", action="store_true")


def main():
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"cobrac: cannot read {args.input}: {e.strerror}", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = lex(source)
    except LexError as e:
        print(f"lex error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        for token in tokens:
            print(token)


if __name__ == "__main__":
    main()
