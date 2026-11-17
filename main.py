#!.venv/bin/python

import argparse
import re
import sys

# Order matters for ties: keywords come before IDENT so that "int" lexes as INT.
TOKENS = [
    ("INT", r"int\b"),
    ("VOID", r"void\b"),
    ("RETURN", r"return\b"),
    ("IDENT", r"[a-zA-Z_]\w*\b"),
    ("CONST", r"[0-9]+\b"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("SEMI", r";"),
]

compiled_rules = [(name, re.compile(pattern)) for name, pattern in TOKENS]
WHITESPACE = re.compile(r"\s+")
COMMENTS = re.compile(r"//.*")
COMMENTS_MULTILINE = re.compile(r"/\*(?:\*(?!/)|[^*])*\*/")
skip_rules = [WHITESPACE, COMMENTS, COMMENTS_MULTILINE]


class LexError(Exception):
    pass


def fast_longest_match(
    text: str, pos: int, rules: list[tuple[str, re.Pattern]]
) -> tuple[str, str] | None:
    """Return (token_type, lexeme) for the longest match at text[pos:], or None.

    On equal-length matches, the earliest rule wins (strict >).
    """
    best = None
    best_len = 0

    for name, regex in rules:
        m = regex.match(text, pos)
        if m and m.end() - pos > best_len:
            best_len = m.end() - pos
            best = (name, m.group(0))

    return best


def lex(source: str) -> list[tuple[str, str]]:
    tokens = []
    pos = 0

    while pos < len(source):
        for pattern in skip_rules:
            m = pattern.match(source, pos)
            if m:
                pos = m.end()
                break
        else:
            match = fast_longest_match(source, pos, compiled_rules)
            if match is None:
                raise LexError(
                    f"unexpected input at offset {pos}: {source[pos : pos + 20]!r}"
                )

            tokens.append(match)
            pos += len(match[1])

    return tokens


parser = argparse.ArgumentParser(
    prog="cobrac", description="A hobby C compiler in Python", epilog=""
)

parser.add_argument("input")
parser.add_argument("--lex", action="store_true")


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

    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
