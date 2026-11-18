from dataclasses import dataclass

from lexer import Token


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
    exp: Constant


@dataclass
class Constant:
    number: int


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

    def parse_exp(self) -> Constant:
        token = self.expect("CONST")
        return Constant(int(token[1]))

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
