from c.assembly_tree import ASSEMBLY_AST
from c.emit import emit
from io import StringIO

def test_emit():
    assembly_ast = ASSEMBLY_AST.Program(
        ASSEMBLY_AST.Function("main", (
            ASSEMBLY_AST.Mov(ASSEMBLY_AST.Imm("0"), ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())), ASSEMBLY_AST.Ret()
        )))
    stream = StringIO()
    emit(assembly_ast, stream)
    assert stream.getvalue() == ".globl _main\n_main :\npushq %rbp\nmovq %rsp, %rbp\nmovl $0, %eax\nmovq %rbp, %rsp\npopq %rbp\nret\n"
    