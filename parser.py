from dataclasses import dataclass

from lexer import Token

type UnaryOperator = Complement | Negate
type BinaryOperator = Add | Subtract | Multiply | Divide | Remainder
type Expression = Constant | Unary | Binary


BINARY_OP_PRECEDENCE = {
    "PLUS": 45,
    "HYPHEN": 45,
    "PERCENT": 50,
    "SLASH": 50,
    "STAR": 50,
}


# node types
@dataclass
class Program:
    function: Function


@dataclass
class Function:
    name: str
    statement: Return


@dataclass
class Return:
    exp: Expression


@dataclass
class Constant:
    number: int


@dataclass
class Unary:
    unary_operator: UnaryOperator
    exp: Expression


@dataclass
class Binary:
    binary_operator: BinaryOperator
    exp: Expression
    exp2: Expression


@dataclass
class Complement:
    pass


@dataclass
class Negate:
    pass


@dataclass
class Add:
    pass


@dataclass
class Subtract:
    pass


@dataclass
class Multiply:
    pass


@dataclass
class Divide:
    pass


@dataclass
class Remainder:
    pass


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, token_list: list[Token]) -> None:
        self.token_list = token_list
        self.pos = 0

    def expect(self, expected_type: str) -> Token:
        if self.pos >= len(self.token_list):
            raise ParseError(f"Expected {expected_type}, got end of file!")

        current_token = self.token_list[self.pos]
        if current_token[0] != expected_type:
            raise ParseError(f"Expected {expected_type}, got {current_token[0]}")

        self.pos += 1
        return current_token

    def peek(self) -> Token | None:
        if self.pos >= len(self.token_list):
            return None

        current_token = self.token_list[self.pos]

        return current_token

    def convert_binop(self, token: Token) -> BinaryOperator:
        match token[0]:
            case "PLUS":
                return Add()
            case "HYPHEN":
                return Subtract()
            case "STAR":
                return Multiply()
            case "SLASH":
                return Divide()
            case "PERCENT":
                return Remainder()
            case _:
                raise ParseError(f"Unexpected token in expression: {token}")

    def parse_factor(self) -> Expression:
        tok = self.peek()
        match tok:
            case ("CONST", _):
                token = self.expect("CONST")
                return Constant(int(token[1]))
            case ("TILDE", _):
                self.expect("TILDE")
                operator = Complement()
                inner_exp = self.parse_factor()
                return Unary(operator, inner_exp)
            case ("HYPHEN", _):
                self.expect("HYPHEN")
                operator = Negate()
                inner_exp = self.parse_factor()
                return Unary(operator, inner_exp)
            case ("LPAREN", _):
                self.expect("LPAREN")
                inner_exp = self.parse_exp(0)
                self.expect("RPAREN")
                return inner_exp
            case _:
                raise ParseError(f"Unexpected token in expression: {tok}")

    def parse_exp(self, min_prec: int) -> Expression:
        left = self.parse_factor()
        next_tok = self.peek()
        while (
            next_tok is not None
            and next_tok[0] in BINARY_OP_PRECEDENCE
            and BINARY_OP_PRECEDENCE[next_tok[0]] >= min_prec
        ):
            operator = self.convert_binop(self.expect(next_tok[0]))
            right = self.parse_exp(BINARY_OP_PRECEDENCE[next_tok[0]] + 1)
            left = Binary(operator, left, right)
            next_tok = self.peek()
        return left

    def parse_statement(self) -> Return:
        self.expect("RETURN")
        exp = self.parse_exp(0)
        self.expect("SEMI")
        return Return(exp)

    def parse_function(self) -> Function:
        self.expect("INT")
        name = self.expect("IDENT")
        self.expect("LPAREN")
        self.expect("VOID")
        self.expect("RPAREN")
        self.expect("LBRACE")
        statement = self.parse_statement()
        self.expect("RBRACE")
        return Function(name[1], statement)

    def parse_program(self) -> Program:
        function = self.parse_function()
        if self.pos != len(self.token_list):
            raise ParseError(f"Leftover token: {self.token_list[self.pos]}")
        return Program(function)
