import subprocess
import sys
import shutil
from c.compile import compile

args = sys.argv[1:]
modifiers = ("lex", "parse", "tacky", "codegen", "S", "--lex", "--parse", "--tacky", "--codegen", "--S")
input_path = [a for a in args if a not in modifiers][0]

assert input_path.endswith(".c"), input_path
preprocessor_output_path = input_path[:-2] + ".i"
subprocess.run(["arch", "-x86_64", "gcc", "-E", "-P", input_path, "-o", preprocessor_output_path])

other_args = [a for a in args if a != input_path]
args = [preprocessor_output_path] + other_args
output = compile(args)
if output:
    # Write to file
    assembly_output_path = input_path[:-2] + ".s"
    with open(assembly_output_path, "w") as fd:
        output.seek(0)
        shutil.copyfileobj(output, fd)
    # Assemble and link
    subprocess.run(["arch", "-x86_64", "gcc", assembly_output_path, "-o", input_path[:-2]])
