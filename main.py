#!.venv/bin/python

import argparse
import sys
from pprint import pprint


from codegen import gen_program
from lexer import LexError, lex
from parser import ParseError, Parser


arg_parser = argparse.ArgumentParser(
    prog="cobrac", description="A hobby C compiler in Python", epilog=""
)

arg_parser.add_argument("input")
arg_parser.add_argument("--lex", action="store_true")
arg_parser.add_argument("--parse", action="store_true")
arg_parser.add_argument("--codegen", action="store_true")
arg_parser.add_argument("--verbose", action="store_true")


def main():
    args = arg_parser.parse_args()

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
        print("lex output:")
        for token in tokens:
            pprint(token)

    if args.lex:
        sys.exit(0)

    parser = Parser(tokens)
    try:
        program = parser.parse_program()
    except ParseError as e:
        print(f"parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print("parse output:")
        pprint(program)

    if args.parse:
        sys.exit(0)

    asm_program = gen_program(program)

    if args.verbose:
        print("codegen output:")
        pprint(asm_program)

    if args.codegen:
        sys.exit(0)


if __name__ == "__main__":
    main()
