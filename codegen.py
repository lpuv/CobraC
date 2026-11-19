from dataclasses import dataclass

import tacky

type Instruction = Mov | Unary | AllocateStack | Ret
type Operand = Imm | Reg | Pseudo | Stack
type Register = AX | R10
type UnaryOperator = Neg | Not


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
class Unary:
    unary_op: UnaryOperator
    operand: Operand


@dataclass
class AllocateStack:
    offset: int


@dataclass
class Reg:
    register: Register


@dataclass
class Pseudo:
    name: str


@dataclass
class Stack:
    offset: int


@dataclass
class AX:
    pass


@dataclass
class R10:
    pass


@dataclass
class Neg:
    pass


@dataclass
class Not:
    pass


class CodegenError(Exception):
    pass


def gen_program(prog: tacky.Program) -> Program:
    return Program(gen_function(prog.function))


def gen_function(func: tacky.Function) -> Function:
    asm_instructions = []
    for instruction in func.body:
        asm_instructions.extend(gen_instruction(instruction))
    return Function(func.name, asm_instructions)


def gen_instruction(instruction: tacky.Instruction) -> list[Instruction]:
    asm_instructions = []
    match instruction:
        case tacky.Return(val):
            asm_instructions.append(Mov(gen_val(val), Reg(AX())))
            asm_instructions.append(Ret())
        case tacky.Unary(unary_operator, src, dst):
            asm_instructions.append(Mov(gen_val(src), gen_val(dst)))
            asm_instructions.append(Unary(gen_operator(unary_operator), gen_val(dst)))
        case _:
            raise CodegenError(
                f"Error processing TACKY instruction during codegen: {instruction}"
            )
    return asm_instructions


def gen_val(val: tacky.Val) -> Operand:
    match val:
        case tacky.Constant(value):
            return Imm(value)
        case tacky.Var(name):
            return Pseudo(name)
        case _:
            raise CodegenError(f"Error processing TACKY value during codegen: {val}")


def gen_operator(op: tacky.UnaryOperator) -> UnaryOperator:
    match op:
        case tacky.Complement():
            return Not()
        case tacky.Negate():
            return Neg()
        case _:
            raise CodegenError(f"Error processing TACKY operator during codegen: {op}")
