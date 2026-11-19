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
    size: int


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
    func = gen_function(prog.function)
    replacer = PseudoReplacer()
    replaced_instructions, stack_size = replacer.replace_pass(func)  # pass 2
    fixedup_instructions = replacer.fixup_pass(replaced_instructions, stack_size)
    return Program(Function(func.name, fixedup_instructions))


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


class PseudoReplacer:
    def __init__(self) -> None:
        self.pseudo_regs: dict[str, int] = {}
        self.current_offset = 0

    def replace_operand(self, operand: Operand) -> Operand:
        match operand:
            case Pseudo(name):
                if name not in self.pseudo_regs:
                    self.current_offset -= 4
                    self.pseudo_regs[name] = self.current_offset
                return Stack(self.pseudo_regs[name])
            case _:
                return operand

    def replace_instruction(self, instruction: Instruction) -> Instruction:
        match instruction:
            case Mov(src, dst):
                return Mov(self.replace_operand(src), self.replace_operand(dst))
            case Unary(unary_op, operand):
                return Unary(unary_op, self.replace_operand(operand))
            case _:
                return instruction

    def replace_pass(self, function: Function) -> tuple[list[Instruction], int]:
        replaced_instructions = []
        for instruction in function.instructions:
            replaced_instructions.append(self.replace_instruction(instruction))
        return replaced_instructions, self.current_offset

    def fixup_pass(
        self, instructions: list[Instruction], stack_size: int
    ) -> list[Instruction]:
        fixedup_instructions = []
        if stack_size != 0:
            fixedup_instructions.append(AllocateStack(abs(stack_size)))

        for instruction in instructions:
            match instruction:
                case Mov(Stack() as src, Stack() as dst):
                    fixedup_instructions.append(Mov(src, Reg(R10())))
                    fixedup_instructions.append(Mov(Reg(R10()), dst))
                case _:
                    fixedup_instructions.append(instruction)

        return fixedup_instructions
