from codegen import Function, Imm, Instruction, Mov, Operand, Program, Reg, Ret


class EmitError(Exception):
    pass


def emit_program(asm_prog: Program) -> str:
    prog = "\n".join(emit_function(asm_prog.function_definition))
    prog += '\n\t.section .note.GNU-stack,"",@progbits\n'
    return prog


def emit_function(asm_func: Function) -> list[str]:
    instructions = [f"\t.globl {asm_func.name}", f"{asm_func.name}:"]
    for asm_instruction in asm_func.instructions:
        instructions.append("\t" + emit_instruction(asm_instruction))

    return instructions


def emit_instruction(asm_instruction: Instruction) -> str:
    match asm_instruction:
        case Mov(src, dst):
            return f"movl\t{emit_operand(src)}, {emit_operand(dst)}"
        case Ret():
            return "ret"
        case _:
            raise EmitError(f"Unexpected instruction: {asm_instruction}")


def emit_operand(asm_operand: Operand) -> str:
    match asm_operand:
        case Imm(val):
            return f"${val}"
        case Reg(register):
            return f"%{register}"
        case _:
            raise EmitError(f"Unexpected operand: {asm_operand}")
