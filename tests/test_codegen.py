from syntax_tree import AST
from assembly_tree import ASSEMBLY_AST
from codegen import gen

def test_codegen():
    ast = AST.Program(AST.Function("main", AST.Return(AST.Constant("0"))))
    assembly_ast = gen(ast)
    assert assembly_ast == ASSEMBLY_AST.Program(ASSEMBLY_AST.Function("main", ASSEMBLY_AST.Instructions((
                ASSEMBLY_AST.Mov(ASSEMBLY_AST.Imm("0"), ASSEMBLY_AST.Register()),
                ASSEMBLY_AST.Ret()
            ))))