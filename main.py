#!.venv/bin/python

import argparse
import os
from pathlib import Path
import subprocess
import sys
from pprint import pprint


from codegen import gen_program
from emit import emit_program
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

    filename = Path(args.input).with_suffix("")
    try:
        subprocess.run(
            ["gcc", "-E", "-P", args.input, "-o", f"{filename}.i"], check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"gcc error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(f"{filename}.i", "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"cobrac: input file {filename}.i missing: {e.strerror}", file=sys.stderr)
        sys.exit(1)
    try:
        os.unlink(f"{filename}.i")
    except OSError as e:
        print(f"cobrac: cannot unlink {filename}.i: {e.strerror}", file=sys.stderr)
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

    try:
        with open(f"{filename}.s", "w", encoding="utf-8") as f:
            f.write(emit_program(asm_program))
    except OSError as e:
        print(f"cobrac: cannot write to {filename}.s: {e.strerror}", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["gcc", f"{filename}.s", "-o", filename], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"gcc error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            os.unlink(f"{filename}.s")
        except OSError as e:
            print(
                f"cobrac: cannot unlink {filename}.s: {e.strerror}",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
