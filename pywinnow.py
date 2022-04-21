#!/usr/bin/env python3

import sys
import dis
import tokenize
import inspect
import ast

all_files = list([filename for filename in sys.argv[1:] if filename.endswith(".py")])

wheat, chaff, good, bad, ugly = [], [], [], [], []

def read_file(filename): # pywinnow:bad
    def maybe_append(filename, line, tok, listname, l): # pywinnow:good
        if "pywinnow:%s" % listname in tok:
            l.append((filename, line))

    with open(filename, 'rb') as file:
        # Get the comments from the file
        for toktype, tok, start, end, line in tokenize.tokenize(file.readline):
            if toktype == tokenize.COMMENT:
                # if the comment contains "pywinnow:wheat", "pywinnow:chaff" etc, then add the line
                # to the appropriate list
                global wheat, chaff, good, bad, ugly
                maybe_append(filename, line, tok, "wheat", wheat)
                maybe_append(filename, line, tok, "chaff", chaff)
                maybe_append(filename, line, tok, "good", good)
                maybe_append(filename, line, tok, "bad", bad)
                maybe_append(filename, line, tok, "ugly", ugly)

def walk_ast(statement):
    if isinstance(statement, list):
        for s in statement:
            for st in walk_ast(s):
                yield st
    elif type(statement) in (ast.FunctionDef, ast.With, ast.For, ast.FunctionDef):
        for s in walk_ast(statement.body):
            yield s
    elif isinstance(statement, ast.If):
        for s in walk_ast([statement.test, statement.body, statement.orelse]):
            yield s
    elif isinstance(statement, ast.Call):
        for s in walk_ast([statement.func, statement.args]):
            yield s
    elif isinstance(statement, ast.Tuple):
        for s in walk_ast(statement.elts):
            yield s
    elif isinstance(statement, ast.Assign):
        for s in walk_ast(statement.targets):
            yield s
        yield statement.value
    elif type(statement) in (ast.Import, ast.Global):
        print("ignoring ", statement)
    else:
        yield statement

def print_statement(filename, statement):
    try:
        string = statement.id
    except:
        string = statement
    print(f"{filename}:{statement.lineno}: {string}")

def check(filename, statement):
    if isinstance(statement, ast.Tuple):
        print(dir(statement))
    else:
        print_statement(filename, statement)

def process_file(filename):
    with open(filename, "rb") as file:
        for statement in walk_ast(ast.parse(file.read(), filename=filename).body):
            check(filename, statement)

for _pass in [read_file, process_file]:
    for fn in all_files:
        _pass(fn)

print("good: ", good)
