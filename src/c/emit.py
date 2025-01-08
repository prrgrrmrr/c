from c.assembly_tree import ASSEMBLY_AST

def emit(assembly_ast, stream):
    # TODO Implement using visitor pattern
    if isinstance(assembly_ast, ASSEMBLY_AST.Program):
        emit(assembly_ast.function_definition, stream)
        # TODO On linux targets emit .section .note.GNU-stack,"",@progbits
    elif isinstance(assembly_ast, ASSEMBLY_AST.Function):
        stream.write(f".globl _{assembly_ast.name}\n")
        stream.write(f"_{assembly_ast.name} :\n") # On MacOS should prefix names with underscore
        stream.write("pushq %rbp\n") # Save caller's base to be able to restore it before function returns
        stream.write("movq %rsp, %rbp\n") # Overwrite value of RBP to point to this function's base, RBP can now be used to reference memory addresses
        for inst in assembly_ast.instructions:
            emit(inst, stream)
    elif isinstance(assembly_ast, ASSEMBLY_AST.AllocateStack):
        stream.write(f"subq ${assembly_ast.nbytes}, %rsp\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.UnaryOperation):
        emit(assembly_ast.unary_operator, stream)
        stream.write(" ")
        emit(assembly_ast.operand, stream)
        stream.write("\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.BinaryOperation):
        emit(assembly_ast.binary_operator, stream)
        stream.write(" ")
        emit(assembly_ast.src, stream)
        stream.write(", ")
        emit(assembly_ast.dst, stream)
        stream.write("\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Idiv):
        stream.write("idivl ")
        emit(assembly_ast.operand, stream)
        stream.write("\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Cdq):
        stream.write("cdq\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Add):
        stream.write("addl")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Sub):
        stream.write("subl")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Mult):
        stream.write("imull")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Mov):
        stream.write("movl ")
        emit(assembly_ast.src, stream)
        stream.write(", ")
        emit(assembly_ast.dst, stream)
        stream.write("\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Ret):
        stream.write("movq %rbp, %rsp\n")
        stream.write("popq %rbp\n")
        stream.write("ret\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Register):
        emit(assembly_ast.reg, stream)
    elif isinstance(assembly_ast, ASSEMBLY_AST.AX):
        stream.write("%eax")
    elif isinstance(assembly_ast, ASSEMBLY_AST.DX):
        stream.write("%edx")
    elif isinstance(assembly_ast, ASSEMBLY_AST.R10):
        stream.write("%r10d")
    elif isinstance(assembly_ast, ASSEMBLY_AST.R11):
        stream.write("%r11d")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Imm):
        stream.write(f"${assembly_ast.value}")
    elif isinstance(assembly_ast, ASSEMBLY_AST.StackOffset):
        stream.write(f"-{assembly_ast.offset}(%rbp)")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Negation):
        stream.write("negl")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Complement):
        stream.write("notl")
