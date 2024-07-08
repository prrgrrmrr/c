from assembly_tree import ASSEMBLY_AST

def emit(assembly_ast, stream):
    # TODO Implement using visitor pattern
    if isinstance(assembly_ast, ASSEMBLY_AST.Program):
        emit(assembly_ast.function_definition, stream)
        # TODO On linux targets emit .section .note.GNU-stack,"",@progbits
    elif isinstance(assembly_ast, ASSEMBLY_AST.Function):
        stream.write(f".globl _{assembly_ast.name}\n")
        stream.write(f"_{assembly_ast.name} :\n") # On MacOS should prefix names with underscore
        emit(assembly_ast.instructions, stream)
    elif isinstance(assembly_ast, ASSEMBLY_AST.Instructions):
        for inst in assembly_ast.instructions:
            emit(inst, stream)
    elif isinstance(assembly_ast, ASSEMBLY_AST.Mov):
        stream.write("movl ")
        emit(assembly_ast.src, stream)
        stream.write(", ")
        emit(assembly_ast.dest, stream)
        stream.write("\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Ret):
        stream.write("ret\n")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Register):
        stream.write("%eax")
    elif isinstance(assembly_ast, ASSEMBLY_AST.Imm):
        stream.write(f"${assembly_ast.value}")