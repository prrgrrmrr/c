from c.syntax_tree import AST
from c.intermediate_tree import IR_AST
from c.irgen import irgen
from c.utils import tmp_unique_name


def test_irgen():
    ast = AST.Program(
        AST.Function(
            "main",
            AST.Return(
                AST.UnaryOperation(
                    AST.Complement(),
                    AST.UnaryOperation(AST.Negation(), AST.Constant("10")),
                )
            ),
        )
    )
    uname_generator = tmp_unique_name()
    ir_ast = irgen(ast, uname_generator)
    assert ir_ast == IR_AST.Program(
        IR_AST.Function(
            "main",
            (
                IR_AST.UnaryOperation(
                    IR_AST.Negation(), IR_AST.Constant("10"), IR_AST.Var("0")
                ),
                IR_AST.UnaryOperation(
                    IR_AST.Complement(), IR_AST.Var("0"), IR_AST.Var("1")
                ),
                IR_AST.Return(IR_AST.Var("1")),
            ),
        )
    )
