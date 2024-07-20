from c.syntax_tree import AST
from c.intermediate_tree import INTERMEDIATE_AST
from c.irgen import irgen
from c.utils import tmp_unique_name

def test_irgen():
    ast = AST.Program(AST.Function("main", AST.Return(AST.UnaryOperation(AST.Complement(), AST.UnaryOperation(AST.Negation(), AST.Constant("10"))))))
    uname_generator = tmp_unique_name()
    ir_ast = irgen(ast, uname_generator)
    assert ir_ast == INTERMEDIATE_AST.Program(INTERMEDIATE_AST.Function("main", (INTERMEDIATE_AST.UnaryOperation(INTERMEDIATE_AST.Negation(), INTERMEDIATE_AST.Constant("10"), INTERMEDIATE_AST.Var("0")),
                                                                                 INTERMEDIATE_AST.UnaryOperation(INTERMEDIATE_AST.Complement(), INTERMEDIATE_AST.Var("0"), INTERMEDIATE_AST.Var("1")),
                                                                                 INTERMEDIATE_AST.Return(INTERMEDIATE_AST.Var("1")))))