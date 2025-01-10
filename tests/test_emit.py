from c.assembly_tree import ASM_AST
from c.emit import emit
from io import StringIO


def test_emit():
    assembly_ast = ASM_AST.Program(
        ASM_AST.Function(
            "main",
            (
                ASM_AST.Mov(
                    ASM_AST.Imm("0"), ASM_AST.Register(ASM_AST.AX())
                ),
                ASM_AST.Ret(),
            ),
        )
    )
    stream = StringIO()
    emit(assembly_ast, stream)
    assert (
        stream.getvalue()
        == ".globl _main\n_main :\npushq %rbp\nmovq %rsp, %rbp\nmovl $0, %eax\nmovq %rbp, %rsp\npopq %rbp\nret\n"
    )
