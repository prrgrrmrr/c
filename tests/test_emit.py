from assembly_tree import ASSEMBLY_AST
from emit import emit
from io import StringIO

def test_emit():
    assembly_ast = ASSEMBLY_AST.Program(
        ASSEMBLY_AST.Function("main", ASSEMBLY_AST.Instructions((
            ASSEMBLY_AST.Mov(ASSEMBLY_AST.Imm("0"), ASSEMBLY_AST.Register()), ASSEMBLY_AST.Ret()
        ))))
    stream = StringIO()
    emit(assembly_ast, stream)
    assert stream.getvalue() == ".globl _main _main :\nmovl $0, %eax\nret\n"
    