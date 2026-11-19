from dataclasses import dataclass

import parser

type Instruction = Return | Unary
type UnaryOperator = Complement | Negate
type Val = Constant | Var


@dataclass
class Program:
    function: Function


@dataclass
class Function:
    name: str
    body: list[Instruction]


@dataclass
class Return:
    val: Val


@dataclass
class Unary:
    unary_operator: UnaryOperator
    src: Val
    dst: Val


@dataclass
class Constant:
    number: int


@dataclass
class Var:
    name: str


@dataclass
class Complement:
    pass


@dataclass
class Negate:
    pass


class TackyError(Exception):
    pass


class Tacky:
    def __init__(self) -> None:
        self.temp_counter = 0

    def convert_operator(self, op: parser.UnaryOperator) -> UnaryOperator:
        match op:
            case parser.Complement():
                return Complement()
            case parser.Negate():
                return Negate()
            case _:
                raise TackyError(f"Unexpected operator: {op}")

    def temp_name(self) -> str:
        name = f"tmp.{self.temp_counter}"
        self.temp_counter += 1
        return name

    def gen_program(self, prog: parser.Program) -> Program:
        return Program(self.gen_function(prog.function))

    def gen_function(self, func: parser.Function) -> Function:
        return Function(func.name, self.gen_statement(func.statement))

    def gen_statement(self, st: parser.Return) -> list[Instruction]:
        instructions = []
        val = self.emit_tacky(st.exp, instructions)
        instructions.append(Return(val))
        return instructions

    def emit_tacky(
        self, exp: parser.Expression, instructions: list[Instruction]
    ) -> Val:
        match exp:
            case parser.Constant(val):
                return Constant(val)
            case parser.Unary(op, inner):
                src = self.emit_tacky(inner, instructions)
                dst_name = self.temp_name()
                dst = Var(dst_name)
                tacky_op = self.convert_operator(op)
                instructions.append(Unary(tacky_op, src, dst))
                return dst
            case _:
                raise TackyError(f"Error while processing TACKY at {exp}")
