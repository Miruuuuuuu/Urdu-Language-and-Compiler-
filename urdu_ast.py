# ==========================================
# URDU LANGUAGE AST NODES
# ==========================================

class Node:
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class VarDecl(Node):
    def __init__(self, type_, name, value):
        self.type = type_
        self.name = name
        self.value = value

    def __repr__(self):
        return f"VarDecl({self.type}, {self.name}, {self.value})"


class Assign(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assign({self.name}, {self.value})"


class Print(Node):
    def __init__(self, values):
        self.values = values
        self.value = values[0] if len(values) == 1 else values

    def __repr__(self):
        return f"Print({self.values})"


class Input(Node):
    def __init__(self, prompt=None):
        self.prompt = prompt or []

    def __repr__(self):
        return f"Input({self.prompt})"


class If(Node):
    def __init__(self, condition, then_block, else_block):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self):
        return f"If({self.condition}, then={self.then_block}, else={self.else_block})"


class Loop(Node):
    def __init__(self, var, start, end, body, kind="for"):
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.kind = kind

    def __repr__(self):
        return f"Loop({self.kind}, {self.var}, {self.start}, {self.end}, {self.body})"


class Function(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Function({self.name})"


class Return(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


class ListNode(Node):
    def __init__(self, name, items):
        self.name = name
        self.items = items

    def __repr__(self):
        return f"List({self.name}, {self.items})"


class ListAccess(Node):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    def __repr__(self):
        return f"ListAccess({self.name}, {self.index})"


class ListAdd(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"ListAdd({self.name}, {self.value})"


class ListRemove(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"ListRemove({self.name}, {self.value})"

class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Call({self.name}, {self.args})"
