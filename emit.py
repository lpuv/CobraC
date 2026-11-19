from codegen import AX, R10, AllocateStack, Function, Imm, Instruction, Mov, Neg, Not, Operand, Program, Reg, Ret, Stack, Unary


class EmitError(Exception):
    pass


def emit_program(asm_prog: Program) -> str:
    prog = "\n".join(emit_function(asm_prog.function_definition))
    prog += '\n\t.section .note.GNU-stack,"",@progbits\n'
    return prog


def emit_function(asm_func: Function) -> list[str]:
    instructions = [f"\t.globl {asm_func.name}", f"{asm_func.name}:", "\tpushq\t%rbp", "\tmovq\t%rsp, %rbp"]
    for asm_instruction in asm_func.instructions:
        instructions.extend(emit_instruction(asm_instruction))

    return instructions


def emit_instruction(asm_instruction: Instruction) -> list[str]:
    match asm_instruction:
        case Mov(src, dst):
            return [f"\tmovl\t{emit_operand(src)}, {emit_operand(dst)}"]
        case Ret():
            return ["\tmovq\t%rbp, %rsp", "\tpopq\t%rbp", "\tret"]
        case Unary(Neg(), operand):
            return [f"\tnegl\t{emit_operand(operand)}"]
        case Unary(Not(), operand):
            return [f"\tnotl\t{emit_operand(operand)}"]
        case AllocateStack(size):
            return [f"\tsubq\t${size}, %rsp"]
        case _:
            raise EmitError(f"Unexpected instruction: {asm_instruction}")


def emit_operand(asm_operand: Operand) -> str:
    match asm_operand:
        case Imm(val):
            return f"${val}"
        case Reg(AX()):
            return "%eax"
        case Reg(R10()):
            return "%r10d"
        case Stack(offset):
            return f"{offset}(%rbp)"
        case _:
            raise EmitError(f"Unexpected operand: {asm_operand}")
