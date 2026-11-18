from dataclasses import dataclass

import parser

type Instruction = Mov | Ret
type Operand = Imm | Register


# node types
@dataclass
class Program:
    function_definition: Function


@dataclass
class Function:
    name: str
    instructions: list[Instruction]


@dataclass
class Mov:
    src: Operand
    dst: Operand


@dataclass
class Imm:
    value: int


@dataclass
class Ret:
    pass


@dataclass
class Register:
    pass


def gen_program(prog: parser.Program) -> Program:
    return Program(gen_function(prog.function))


def gen_function(func: parser.Function) -> Function:
    return Function(func.name, gen_statement(func.statement))


def gen_statement(statment: parser.Return) -> list[Instruction]:
    return [Mov(gen_exp(statment.exp), Register()), Ret()]


def gen_exp(exp: parser.Constant) -> Operand:
    return Imm(exp.number)
