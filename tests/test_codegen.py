from c.intermediate_tree import INTERMEDIATE_AST
from c.assembly_tree import ASSEMBLY_AST
from c.codegen import asmgen

def test_codegen():
    ir = INTERMEDIATE_AST.Program(INTERMEDIATE_AST.Function("main", (
        INTERMEDIATE_AST.UnaryOperation(INTERMEDIATE_AST.Negation(), INTERMEDIATE_AST.Constant("42"), INTERMEDIATE_AST.Var("0")),
        INTERMEDIATE_AST.Return(INTERMEDIATE_AST.Var("0"))
    )))
    asm = asmgen(ir)
    assert asm == ASSEMBLY_AST.Program(ASSEMBLY_AST.Function("main", (
        ASSEMBLY_AST.AllocateStack(4),
        ASSEMBLY_AST.Mov(ASSEMBLY_AST.Imm("42"), ASSEMBLY_AST.StackOffset(4)),
        ASSEMBLY_AST.UnaryOperation(ASSEMBLY_AST.Negation(), ASSEMBLY_AST.StackOffset(4)),
        ASSEMBLY_AST.Mov(ASSEMBLY_AST.StackOffset(4), ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())),
        ASSEMBLY_AST.Ret()
        )))