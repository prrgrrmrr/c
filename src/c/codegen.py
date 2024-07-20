"""Converts IR AST to another tree representation useful for assembly generation"""

from functools import reduce
from c.intermediate_tree import INTERMEDIATE_AST
from c.assembly_tree import ASSEMBLY_AST

def asm_tree(ir_ast):
    """Generates tree of assembly instructions from intermediate representation AST - this step uses pseudo registers for variables"""
    
    # Simple if-else for now
    # TODO Visitor design pattern solves this better by defining visit method for each node
    # Program
    if isinstance(ir_ast, INTERMEDIATE_AST.Program):
        function_definition = asm_tree(ir_ast.function_definition)
        return ASSEMBLY_AST.Program(function_definition)
    # Function
    elif isinstance(ir_ast, INTERMEDIATE_AST.Function):
        name = ir_ast.name
        instructions = reduce(lambda acc, inst: acc + inst, (asm_tree(inst) for inst in ir_ast.instructions))
        return ASSEMBLY_AST.Function(name, instructions)
    # Expressions
    elif isinstance(ir_ast, INTERMEDIATE_AST.UnaryOperation):
        # src, dst tmp vars will be replaced by pseudo registers by recursive calls
        # constants will be mapped to immediate asm valeus
        src = asm_tree(ir_ast.src_val)
        dst = asm_tree(ir_ast.dst_val)
        unary_operator = asm_tree(ir_ast.unary_operator)
        return (ASSEMBLY_AST.Mov(src, dst), ASSEMBLY_AST.UnaryOperation(unary_operator, dst))
    elif isinstance(ir_ast, INTERMEDIATE_AST.Return):
        val = asm_tree(ir_ast.val)
        return ((ASSEMBLY_AST.Mov(val, ASSEMBLY_AST.Register(ASSEMBLY_AST.AX())), ASSEMBLY_AST.Ret()))
    elif isinstance(ir_ast, INTERMEDIATE_AST.Constant):
        return ASSEMBLY_AST.Imm(ir_ast.value)
    elif isinstance(ir_ast, INTERMEDIATE_AST.Var):
        return ASSEMBLY_AST.Pseudo(ir_ast.identifier)
    elif isinstance(ir_ast, INTERMEDIATE_AST.Complement):
        return ASSEMBLY_AST.Complement()
    elif isinstance(ir_ast, INTERMEDIATE_AST.Negation):
        return ASSEMBLY_AST.Negation()
    
def replace_pseudo_registers(asm_ast, offset_dict):
    # We don't want to rebuild an entire tree here - keep what we can
    if isinstance(asm_ast, ASSEMBLY_AST.Program):
        asm_ast.function_definition = replace_pseudo_registers(asm_ast.function_definition, offset_dict)
    elif isinstance(asm_ast, ASSEMBLY_AST.Function):
        # Already a list of asm instructions - no fear of getting an iterable from recursive call here
        instructions = tuple(replace_pseudo_registers(inst, offset_dict) for inst in asm_ast.instructions)
        asm_ast.instructions = instructions
    elif isinstance(asm_ast, ASSEMBLY_AST.UnaryOperation):
        asm_ast.operand = replace_pseudo_registers(asm_ast.operand, offset_dict)
        asm_ast.unary_operator = replace_pseudo_registers(asm_ast.unary_operator, offset_dict)
    elif isinstance(asm_ast, ASSEMBLY_AST.Ret):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Mov):
        asm_ast.src = replace_pseudo_registers(asm_ast.src, offset_dict)
        asm_ast.dst = replace_pseudo_registers(asm_ast.dst, offset_dict)
    elif isinstance(asm_ast, ASSEMBLY_AST.Imm):
        # TODO can this be anything other than an immediate value ? Means no need for recursive call
        asm_ast.value = replace_pseudo_registers(asm_ast.value, offset_dict)
    elif isinstance(asm_ast, ASSEMBLY_AST.Pseudo):
        if asm_ast.identifier in offset_dict:
            offset = offset_dict[asm_ast.identifier]
        else:
            offset = 4 # 4 bytes for int
            key = max(offset_dict, key = offset_dict.get, default = None)
            if key:
                offset = 4 + offset_dict[key]
            offset_dict[asm_ast.identifier] = offset
            offset_dict[asm_ast.identifier] = offset
        return ASSEMBLY_AST.StackOffset(offset)
    elif isinstance(asm_ast, ASSEMBLY_AST.Complement):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Negation):
        pass
    return asm_ast

def fix_instructions(asm_ast, stack_alloc):
    # Keep tree and change only what needs to be changed
    if isinstance(asm_ast, ASSEMBLY_AST.Program):
        asm_ast.function_definition = fix_instructions(asm_ast.function_definition, stack_alloc)
    elif isinstance(asm_ast, ASSEMBLY_AST.Function):
        # Add stack frame allocation for function (this is a high level asm tree instruction, actual asm instructions emitted by asm code emitter)
        instructions = [ASSEMBLY_AST.AllocateStack(stack_alloc)]
        for inst in asm_ast.instructions:
            fixed = fix_instructions(inst, stack_alloc)
            if isinstance(fixed, tuple):
                instructions.extend(fixed)
            else:
                instructions.append(fixed)
        asm_ast.instructions = tuple(instructions)
    elif isinstance(asm_ast, ASSEMBLY_AST.Mov):
        if isinstance(asm_ast.src, ASSEMBLY_AST.StackOffset) and isinstance(asm_ast.dst, ASSEMBLY_AST.StackOffset):
            return (
                ASSEMBLY_AST.Mov(asm_ast.src, ASSEMBLY_AST.Register(ASSEMBLY_AST.R10())),
                ASSEMBLY_AST.Mov(ASSEMBLY_AST.Register(ASSEMBLY_AST.R10()), asm_ast.dst)
            )
    elif isinstance(asm_ast, ASSEMBLY_AST.UnaryOperation):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Ret):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Imm):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.StackOffset):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Complement):
        pass
    elif isinstance(asm_ast, ASSEMBLY_AST.Negation):
        pass
    return asm_ast

def asmgen(ir_ast):
    asm_ast = asm_tree(ir_ast)
    offset_dict = {} # Stack offset in bytes for given identifier key
    asm_ast = replace_pseudo_registers(asm_ast, offset_dict)
    stack_alloc = 0
    key = max(offset_dict, key = offset_dict.get, default = None)
    if key:
        stack_alloc = offset_dict[key]
    asm_ast = fix_instructions(asm_ast, stack_alloc)
    return asm_ast
