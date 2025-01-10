"""Converts IR AST to another tree representation useful for assembly generation"""

from functools import reduce
from c.intermediate_tree import IR_AST
from c.assembly_tree import ASM_AST


def _replace_pseudo_registers(asm_ast, offset_dict):
    """Replaces pseudo registers (for IR tmp vars) in asm tree from IR GEN with stack references"""
    # offset_dict stores stack offset in bytes for given tmp identifier
    # We don't want to rebuild an entire tree here - keep what we can

    # Program
    if isinstance(asm_ast, ASM_AST.Program):
        asm_ast.function_definition = _replace_pseudo_registers(
            asm_ast.function_definition, offset_dict
        )

    # Function
    elif isinstance(asm_ast, ASM_AST.Function):
        # Already a list of asm instructions - no fear of getting an iterable from recursive call here
        instructions = tuple(
            _replace_pseudo_registers(inst, offset_dict)
            for inst in asm_ast.instructions
        )
        asm_ast.instructions = instructions

    # asm instructions

    # Unary asm instruction
    elif isinstance(asm_ast, ASM_AST.UnaryOperation):
        asm_ast.operand = _replace_pseudo_registers(asm_ast.operand, offset_dict)

    # Binary asm instruction
    elif isinstance(asm_ast, ASM_AST.BinaryOperation):
        asm_ast.src = _replace_pseudo_registers(asm_ast.src, offset_dict)
        asm_ast.dst = _replace_pseudo_registers(asm_ast.dst, offset_dict)

    # Idiv
    elif isinstance(asm_ast, ASM_AST.Idiv):
        asm_ast.operand = _replace_pseudo_registers(asm_ast.operand, offset_dict)

    # Mov
    elif isinstance(asm_ast, ASM_AST.Mov):
        asm_ast.src = _replace_pseudo_registers(asm_ast.src, offset_dict)
        asm_ast.dst = _replace_pseudo_registers(asm_ast.dst, offset_dict)

    # Cmp
    elif isinstance(asm_ast, ASM_AST.Cmp):
        asm_ast.operand_a = _replace_pseudo_registers(asm_ast.operand_a, offset_dict)
        asm_ast.operand_b = _replace_pseudo_registers(asm_ast.operand_b, offset_dict)

    # Set
    elif isinstance(asm_ast, ASM_AST.SetCC):
        asm_ast.dst = _replace_pseudo_registers(asm_ast.dst, offset_dict)

    # Replace tmp identifier by stack reference
    elif isinstance(asm_ast, ASM_AST.Pseudo):
        if asm_ast.identifier in offset_dict:
            offset = offset_dict[asm_ast.identifier]
        else:
            offset = 4  # 4 bytes for int
            key = max(offset_dict, key=offset_dict.get, default=None)
            if key:
                offset = 4 + offset_dict[key]
            offset_dict[asm_ast.identifier] = offset
        return ASM_AST.StackOffset(offset)

    # If none of above, don't touch
    return asm_ast


def _fix_instructions(asm_ast, stack_alloc):
    """Fixes asm tree instructions (i.e., src and dst of Mov instruction cannot both be stack references)"""
    # Keep tree and change only what needs to be changed

    # Program
    if isinstance(asm_ast, ASM_AST.Program):
        asm_ast.function_definition = _fix_instructions(
            asm_ast.function_definition, stack_alloc
        )

    # Function
    elif isinstance(asm_ast, ASM_AST.Function):
        # Add stack frame allocation for function (this is a high level asm tree instruction, actual asm instructions emitted by asm code emitter)
        instructions = [ASM_AST.AllocateStack(stack_alloc)]
        for inst in asm_ast.instructions:
            fixed = _fix_instructions(inst, stack_alloc)
            if isinstance(fixed, tuple):
                instructions.extend(fixed)
            else:
                instructions.append(fixed)
        asm_ast.instructions = tuple(instructions)

    # Fix Mov asm instruction - src and dst cannot be both stack references so we use our scratch register R10 as intermediate
    elif isinstance(asm_ast, ASM_AST.Mov):
        if isinstance(asm_ast.src, ASM_AST.StackOffset) and isinstance(
            asm_ast.dst, ASM_AST.StackOffset
        ):
            return (
                ASM_AST.Mov(asm_ast.src, ASM_AST.Register(ASM_AST.R10())),
                ASM_AST.Mov(ASM_AST.Register(ASM_AST.R10()), asm_ast.dst),
            )

    # Fix Cmp - operands cannot both be stack references and second operand cannot be constant
    elif isinstance(asm_ast, ASM_AST.Cmp):
        if isinstance(asm_ast.operand_a, ASM_AST.StackOffset) and isinstance(
            asm_ast.operand_b, ASM_AST.StackOffset
        ):
            # Convention is to use R10 to fix sources (first operand)
            return (
                ASM_AST.Mov(asm_ast.operand_a, ASM_AST.Register(ASM_AST.R10())),
                ASM_AST.Cmp(ASM_AST.Register(ASM_AST.R10()), asm_ast.operand_b),
            )
        elif isinstance(asm_ast.operand_b, ASM_AST.Imm):
            # Convention is to use R11 to fix destinations (second operand)
            return (
                ASM_AST.Mov(asm_ast.operand_b, ASM_AST.Register(ASM_AST.R11())),
                ASM_AST.Cmp(asm_ast.operand_a, ASM_AST.Register(ASM_AST.R11())),
            )

    # Fix Add, Sub and Mult
    elif isinstance(asm_ast, ASM_AST.BinaryOperation):
        # Fix Add and Sub like Mov above
        if isinstance(asm_ast.binary_operator, ASM_AST.Add) or isinstance(
            asm_ast.binary_operator, ASM_AST.Sub
        ):
            if isinstance(asm_ast.src, ASM_AST.StackOffset) and isinstance(
                asm_ast.dst, ASM_AST.StackOffset
            ):
                return (
                    ASM_AST.Mov(asm_ast.src, ASM_AST.Register(ASM_AST.R10())),
                    ASM_AST.BinaryOperation(
                        (
                            ASM_AST.Add()
                            if isinstance(asm_ast.binary_operator, ASM_AST.Add)
                            else ASM_AST.Sub()
                        ),
                        ASM_AST.Register(ASM_AST.R10()),
                        asm_ast.dst,
                    ),
                )

        # Fix Mult
        elif isinstance(asm_ast.binary_operator, ASM_AST.Mult):
            # Mult instruction can’t use a memory address as its destination, regardless of its source operand
            # To fix an instruction’s destination operand, we use the R11 register instead of R10
            if isinstance(asm_ast.dst, ASM_AST.StackOffset):
                return (
                    ASM_AST.Mov(asm_ast.dst, ASM_AST.Register(ASM_AST.R11())),
                    ASM_AST.BinaryOperation(
                        ASM_AST.Mult(),
                        asm_ast.src,
                        ASM_AST.Register(ASM_AST.R11()),
                    ),
                    ASM_AST.Mov(ASM_AST.Register(ASM_AST.R11()), asm_ast.dst),
                )

    # Fix Idiv asm instruction - Whenever idiv needs to operate on a constant, we copy that constant into our scratch register first
    elif isinstance(asm_ast, ASM_AST.Idiv):
        if isinstance(asm_ast.operand, ASM_AST.Imm):
            return (
                ASM_AST.Mov(asm_ast.operand, ASM_AST.Register(ASM_AST.R10())),
                ASM_AST.Idiv(ASM_AST.Register(ASM_AST.R10())),
            )

    # Else, don't touch
    return asm_ast


def asm_tree(ir_ast):
    """Generates tree of assembly instructions from IR tree - this step uses pseudo registers for variables"""

    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node

    # Program
    if isinstance(ir_ast, IR_AST.Program):
        function_definition = asm_tree(ir_ast.function_definition)
        return ASM_AST.Program(function_definition)

    # Function
    elif isinstance(ir_ast, IR_AST.Function):
        name = ir_ast.name
        assert isinstance(ir_ast.instructions, tuple)  # TODO remove
        instructions = reduce(
            lambda acc, inst: acc + inst,
            (asm_tree(inst) for inst in ir_ast.instructions),
        )  # TODO this is inefficient - use a O(1) list append
        return ASM_AST.Function(name, instructions)

    # Expressions

    # Unary expressions
    elif isinstance(ir_ast, IR_AST.UnaryOperation):
        # Note that vals in IR can be identifiers (Var) or constants (Constant)
        # src, dst tmp vars will be replaced by pseudo registers by recursive calls
        # constants will be converted to immediate asm values
        src = asm_tree(ir_ast.src_val)
        dst = asm_tree(ir_ast.dst_val)

        # Logical Not is implemented differently (!x is implemented as x == 0)
        if isinstance(ir_ast.unary_operator, IR_AST.Not):
            return (
                ASM_AST.Cmp(ASM_AST.Imm(0), src),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("e", dst),
            )
        else:
            # Complement, Negation
            unary_operator = asm_tree(ir_ast.unary_operator)
            # If dst is converted to an immediate value, it will be fixed in later fix stages to become a register (or stack reference if that is allowed by assembly instruction)
            return (
                ASM_AST.Mov(src, dst),
                ASM_AST.UnaryOperation(unary_operator, dst),
            )

    # Binary expressions
    elif isinstance(ir_ast, IR_AST.BinaryOperation):
        src1 = asm_tree(ir_ast.src_val1)
        src2 = asm_tree(ir_ast.src_val2)
        dst = asm_tree(ir_ast.dst_val)
        if (
            isinstance(ir_ast.binary_operator, IR_AST.Addition)
            or isinstance(ir_ast.binary_operator, IR_AST.Subtraction)
            or isinstance(ir_ast.binary_operator, IR_AST.Multiplication)
        ):
            binary_operator = asm_tree(ir_ast.binary_operator)
            return (
                ASM_AST.Mov(src1, dst),
                ASM_AST.BinaryOperation(binary_operator, src2, dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.Division):
            return (
                ASM_AST.Mov(src1, ASM_AST.Register(ASM_AST.AX())),
                ASM_AST.Cdq(),
                ASM_AST.Idiv(src2),
                ASM_AST.Mov(ASM_AST.Register(ASM_AST.AX()), dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.Remainder):
            return (
                ASM_AST.Mov(src1, ASM_AST.Register(ASM_AST.AX())),
                ASM_AST.Cdq(),
                ASM_AST.Idiv(src2),
                ASM_AST.Mov(ASM_AST.Register(ASM_AST.DX()), dst),
            )

        # Relational operations
        # Clear dst before setting it - set instructions acts on bytes so might endup with wrong value if dst is not cleared
        # Mov does not change RFLAGS, so when SetCC looks at them, they are intact
        elif isinstance(ir_ast.binary_operator, IR_AST.Equal):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("e", dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.NotEqual):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("ne", dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.GreaterThan):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("g", dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.GreaterOrEqual):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("ge", dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.LessThan):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("l", dst),
            )
        elif isinstance(ir_ast.binary_operator, IR_AST.LessOrEqual):
            return (
                ASM_AST.Cmp(src2, src1),
                ASM_AST.Mov(ASM_AST.Imm(0), dst),
                ASM_AST.SetCC("le", dst),
            )

    # Operators

    # Unary Operators - no need lists here as these are not ASM instructions
    elif isinstance(ir_ast, IR_AST.Complement):
        return ASM_AST.Complement()
    elif isinstance(ir_ast, IR_AST.Negation):
        return ASM_AST.Negation()

    # Binary operators - no need lists here as these are not ASM instructions
    elif isinstance(ir_ast, IR_AST.Addition):
        return ASM_AST.Add()
    elif isinstance(ir_ast, IR_AST.Subtraction):
        return ASM_AST.Sub()
    elif isinstance(ir_ast, IR_AST.Multiplication):
        return ASM_AST.Mult()
    # Division and Remainder handled in a special way above in binary operation by using Idiv and Cdq instructions

    # Jump instructions
    elif isinstance(ir_ast, IR_AST.Jump):
        return (ASM_AST.Jmp(ir_ast.target),)
    elif isinstance(ir_ast, IR_AST.JumpIfZero):
        condition = asm_tree(ir_ast.condition)
        return (
            ASM_AST.Cmp(ASM_AST.Imm(0), condition),
            ASM_AST.JmpCC("e", ir_ast.target),
        )
    elif isinstance(ir_ast, IR_AST.JumpIfNotZero):
        condition = asm_tree(ir_ast.condition)
        return (
            ASM_AST.Cmp(ASM_AST.Imm(0), condition),
            ASM_AST.JmpCC("ne", ir_ast.target),
        )
    elif isinstance(ir_ast, IR_AST.Copy):
        src = asm_tree(ir_ast.src)
        print("dst", ir_ast.dst)
        dst = asm_tree(ir_ast.dst)
        return (ASM_AST.Mov(src, dst),)
    elif isinstance(ir_ast, IR_AST.Label):
        return (ASM_AST.Label(ir_ast.name),)

    # Return instruction
    elif isinstance(ir_ast, IR_AST.Return):
        val = asm_tree(ir_ast.val)
        return (
            ASM_AST.Mov(val, ASM_AST.Register(ASM_AST.AX())),
            ASM_AST.Ret(),
        )

    # IR constants - no need to convert to list, not an instruction
    elif isinstance(ir_ast, IR_AST.Constant):
        return ASM_AST.Imm(ir_ast.value)

    # IR vars (tmp vars) - no need to convert to list, not an instruction
    elif isinstance(ir_ast, IR_AST.Var):
        return ASM_AST.Pseudo(ir_ast.identifier)

    raise Exception("Missed something !")


def asmgen(ir_ast):
    asm_ast = asm_tree(ir_ast)
    offset_dict = {}  # Stack offset in bytes for given identifier key
    asm_ast = _replace_pseudo_registers(asm_ast, offset_dict)
    stack_alloc = 0
    key = max(offset_dict, key=offset_dict.get, default=None)
    if key:
        stack_alloc = offset_dict[key]
    asm_ast = _fix_instructions(asm_ast, stack_alloc)
    return asm_ast
