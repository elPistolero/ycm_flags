import json
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("compile_commands", help="path to the compile_commands.json file")
parser.add_argument("flags", help="path for the output flags file")
args = parser.parse_args()

json_doc = None
with open(args.compile_commands, 'r') as json_file:
    json_doc = json.load(json_file)

if json_doc is None:
    sys.exit()

warnings = []
defines = []
includes = []
isystem = []
compiler_flags = []

for json_obj in json_doc:
    abs_dir = json_obj['directory']
    commands = json_obj['command']
    commands = commands.strip()
    commands = commands.split(" ")
    for idx, com in enumerate(commands):
        if "-W" == com[:2]:
            warnings.append(com)
        elif "-D" == com[:2]:
            defines.append(com)
        elif "-I" == com[:2]:
            if "/" != com[2]:
                dir_name = abs_dir + "/" + com[2:]
            else:
                dir_name = com[2:]

            if os.path.exists(dir_name):
                includes.append(dir_name)
        elif "-isystem" in com:
            if "/" != commands[idx+1][0]:
                dir_name = abs_dir + "/" + commands[idx+1]
            else:
                dir_name = commands[idx+1]
            if os.path.exists(dir_name):
                isystem.append(dir_name)
        elif "-std" in com:
            compiler_flags.append(com)

warnings = set(warnings)
defines = set(defines)
includes = set(includes)
isystem = set(isystem)
compiler_flags = set(compiler_flags)

flags_path = os.path.abspath(args.flags)
flags_dir = os.path.dirname(flags_path)

if not os.path.exists(flags_dir):
    os.makedirs(flags_dir)

with open(flags_path, 'w') as flags_file:
    flags_file.write("flags = [\n")
    for f in compiler_flags:
        flags_file.write("'" + f + "',\n")
    for f in defines:
        flags_file.write("'" + f + "',\n")
    for f in warnings:
        flags_file.write("'" + f + "',\n")
    for f in isystem:
        flags_file.write("'-isystem',\n")
        flags_file.write("'" + f + "',\n")
    for f in includes:
        flags_file.write("'-I',\n")
        flags_file.write("'" + f + "',\n")
    flags_file.write("]\n")
