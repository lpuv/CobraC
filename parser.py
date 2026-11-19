from dataclasses import dataclass

from lexer import Token

type UnaryOperator = Complement | Negate
type Expression = Constant | Unary


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
class Complement:
    pass


@dataclass
class Negate:
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

    def parse_exp(self) -> Expression:
        tok = self.peek()
        match tok:
            case ("CONST", _):
                token = self.expect("CONST")
                return Constant(int(token[1]))
            case ("TILDE", _):
                self.expect("TILDE")
                operator = Complement()
                operand = self.parse_exp()
                return Unary(operator, operand)
            case ("HYPHEN", _):
                self.expect("HYPHEN")
                operator = Negate()
                operand = self.parse_exp()
                return Unary(operator, operand)
            case ("LPAREN", _):
                self.expect("LPAREN")
                inner_exp = self.parse_exp()
                self.expect("RPAREN")
                return inner_exp
            case _:
                raise ParseError(f"Unexpected token in expression: {tok}")

    def parse_statement(self) -> Return:
        self.expect("RETURN")
        exp = self.parse_exp()
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
