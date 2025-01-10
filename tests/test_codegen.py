from c.intermediate_tree import IR_AST
from c.assembly_tree import ASM_AST
from c.codegen import asmgen


def test_codegen():
    ir = IR_AST.Program(
        IR_AST.Function(
            "main",
            (
                IR_AST.UnaryOperation(
                    IR_AST.Negation(), IR_AST.Constant("42"), IR_AST.Var("0")
                ),
                IR_AST.Return(IR_AST.Var("0")),
            ),
        )
    )
    asm = asmgen(ir)
    assert asm == ASM_AST.Program(
        ASM_AST.Function(
            "main",
            (
                ASM_AST.AllocateStack(4),
                ASM_AST.Mov(ASM_AST.Imm("42"), ASM_AST.StackOffset(4)),
                ASM_AST.UnaryOperation(
                    ASM_AST.Negation(), ASM_AST.StackOffset(4)
                ),
                ASM_AST.Mov(
                    ASM_AST.StackOffset(4),
                    ASM_AST.Register(ASM_AST.AX()),
                ),
                ASM_AST.Ret(),
            ),
        )
    )
