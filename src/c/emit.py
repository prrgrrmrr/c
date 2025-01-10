"""Creates actual asm instructions from asm tree"""

from c.assembly_tree import ASM_AST


def _emit_1byte(asm_ast, stream):
    """Used in set asm instructions because it expects 1-byte versions of registers"""
    if isinstance(asm_ast, ASM_AST.Register):
        _emit_1byte(asm_ast.reg, stream)
    elif isinstance(asm_ast, ASM_AST.AX):
        stream.write("%al")
    elif isinstance(asm_ast, ASM_AST.DX):
        stream.write("%dl")
    elif isinstance(asm_ast, ASM_AST.R10):
        stream.write("%r10b")
    elif isinstance(asm_ast, ASM_AST.R11):
        stream.write("%r11b")
    else:
        emit(
            asm_ast, stream
        )  # Stack references are handled correctly because AMD64 is little-endian, so normal emit


def emit(asm_ast, stream):
    """Writes asm instructions to stream"""
    # TODO Implement using visitor pattern
    if isinstance(asm_ast, ASM_AST.Program):
        emit(asm_ast.function_definition, stream)
        # TODO On linux targets emit .section .note.GNU-stack,"",@progbits
    elif isinstance(asm_ast, ASM_AST.Function):
        stream.write(f".globl _{asm_ast.name}\n")
        stream.write(
            f"_{asm_ast.name} :\n"
        )  # On MacOS should prefix names with underscore
        stream.write(
            "pushq %rbp\n"
        )  # Save caller's base to be able to restore it before function returns
        stream.write(
            "movq %rsp, %rbp\n"
        )  # Overwrite value of RBP to point to this function's base, RBP can now be used to reference memory addresses
        for inst in asm_ast.instructions:
            emit(inst, stream)
    elif isinstance(asm_ast, ASM_AST.AllocateStack):
        stream.write(f"subq ${asm_ast.nbytes}, %rsp\n")
    elif isinstance(asm_ast, ASM_AST.UnaryOperation):
        emit(asm_ast.unary_operator, stream)
        stream.write(" ")
        emit(asm_ast.operand, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.BinaryOperation):
        emit(asm_ast.binary_operator, stream)
        stream.write(" ")
        emit(asm_ast.src, stream)
        stream.write(", ")
        emit(asm_ast.dst, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.Idiv):
        stream.write("idivl ")
        emit(asm_ast.operand, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.Cdq):
        stream.write("cdq\n")
    elif isinstance(asm_ast, ASM_AST.Add):
        stream.write("addl")
    elif isinstance(asm_ast, ASM_AST.Sub):
        stream.write("subl")
    elif isinstance(asm_ast, ASM_AST.Mult):
        stream.write("imull")
    elif isinstance(asm_ast, ASM_AST.Mov):
        stream.write("movl ")
        emit(asm_ast.src, stream)
        stream.write(", ")
        emit(asm_ast.dst, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.Ret):
        stream.write("movq %rbp, %rsp\n")
        stream.write("popq %rbp\n")
        stream.write("ret\n")
    elif isinstance(asm_ast, ASM_AST.Register):
        emit(asm_ast.reg, stream)
    elif isinstance(asm_ast, ASM_AST.AX):
        stream.write("%eax")
    elif isinstance(asm_ast, ASM_AST.DX):
        stream.write("%edx")
    elif isinstance(asm_ast, ASM_AST.R10):
        stream.write("%r10d")
    elif isinstance(asm_ast, ASM_AST.R11):
        stream.write("%r11d")
    elif isinstance(asm_ast, ASM_AST.Imm):
        stream.write(f"${asm_ast.value}")
    elif isinstance(asm_ast, ASM_AST.StackOffset):
        stream.write(f"-{asm_ast.offset}(%rbp)")
    elif isinstance(asm_ast, ASM_AST.Negation):
        stream.write("negl")
    elif isinstance(asm_ast, ASM_AST.Complement):
        stream.write("notl")
    elif isinstance(asm_ast, ASM_AST.Cmp):
        stream.write("cmpl ")
        emit(asm_ast.operand_a, stream)
        stream.write(", ")
        emit(asm_ast.operand_b, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.Jmp):
        stream.write(
            f"jmp L{asm_ast.target}\n"
        )  # prefix labels with L on MacOS to avoid name conflicts
    elif isinstance(asm_ast, ASM_AST.JmpCC):
        stream.write(f"j{asm_ast.condition_code} L{asm_ast.target}\n")
    elif isinstance(asm_ast, ASM_AST.SetCC):
        stream.write(f"set{asm_ast.condition_code} ")
        _emit_1byte(asm_ast.dst, stream)
        stream.write("\n")
    elif isinstance(asm_ast, ASM_AST.Label):
        stream.write(f"L{asm_ast.identifier}:\n")
