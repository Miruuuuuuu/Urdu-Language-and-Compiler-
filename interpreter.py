# ==========================================
# URDU LANGUAGE INTERPRETER
# ==========================================

from urdu_ast import *


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self):
        self.scopes = [{}]
        self.funcs = {}

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def set_var(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

        self.scopes[-1][name] = value

    def declare_var(self, name, value):
        self.scopes[-1][name] = value

    def get_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        raise Exception(f"Runtime Error: variable '{name}' not defined")

    def set_func(self, name, node):
        self.funcs[name] = node

    def get_func(self, name):
        if name in self.funcs:
            return self.funcs[name]

        raise Exception(f"Runtime Error: function '{name}' not defined")


class Interpreter:
    def __init__(self):
        self.env = Environment()

    def run(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.generic)
        return method(node)

    def generic(self, node):
        raise Exception(f"No interpreter rule for {type(node).__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            if isinstance(stmt, Function):
                self.run(stmt)

        for stmt in node.statements:
            if not isinstance(stmt, Function):
                self.run(stmt)

    def visit_VarDecl(self, node):
        value = self.eval(node.value, expected_type=node.type)
        self.env.declare_var(node.name, value)

    def visit_Assign(self, node):
        self.env.set_var(node.name, self.eval(node.value))

    def visit_Print(self, node):
        values = [self.eval(value) for value in node.values]
        print("\033[96m", end="")
        print(*values)
        print("\033[0m", end="")

    def visit_If(self, node):
        statements = node.then_block if self.eval_condition(node.condition) else node.else_block

        self.env.push()
        try:
            self.run_block(statements)
        finally:
            self.env.pop()

    def visit_Loop(self, node):
        self.env.push()
        try:
            if node.kind == "for":
                start = self.eval(node.start)
                end = self.eval(node.end)
                if not isinstance(start, int) or isinstance(start, bool):
                    raise Exception("Runtime Error: for loop start must be an integer")
                if not isinstance(end, int) or isinstance(end, bool):
                    raise Exception("Runtime Error: for loop end must be an integer")

                step = 1 if start <= end else -1
                stop = end + step

                for value in range(start, stop, step):
                    self.env.declare_var(node.var, value)
                    self.run_block(node.body)
            elif node.kind == "while":
                while self.eval_condition(node.start):
                    self.run_block(node.body)
            elif node.kind == "do_while":
                while True:
                    self.run_block(node.body)
                    if not self.eval_condition(node.start):
                        break
            else:
                raise Exception(f"Runtime Error: unknown loop kind '{node.kind}'")
        finally:
            self.env.pop()

    def run_block(self, statements):
        for stmt in statements:
            self.run(stmt)

    def visit_Function(self, node):
        self.env.set_func(node.name, node)

    def visit_FunctionCall(self, node):
        func = self.env.get_func(node.name)
        args = [self.eval(arg) for arg in node.args]

        self.env.push()
        try:
            for index, param in enumerate(func.params):
                value = args[index] if index < len(args) else None
                self.env.declare_var(param, value)

            for stmt in func.body:
                self.run(stmt)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.env.pop()

        return None

    def visit_Return(self, node):
        raise ReturnSignal(self.eval(node.value))

    def visit_Input(self, node):
        return self.eval(node)

    def visit_ListNode(self, node):
        self.env.declare_var(node.name, [self.eval(item) for item in node.items])

    def visit_ListAdd(self, node):
        items = self.env.get_var(node.name)
        if not isinstance(items, list):
            raise Exception(f"Runtime Error: '{node.name}' is not a list")
        items.append(self.eval(node.value))

    def visit_ListRemove(self, node):
        items = self.env.get_var(node.name)
        if not isinstance(items, list):
            raise Exception(f"Runtime Error: '{node.name}' is not a list")

        value = self.eval(node.value)
        if value in items:
            items.remove(value)

    def eval_condition(self, condition):
        if condition is None:
            return False

        if isinstance(condition, tuple) and len(condition) == 2:
            op, value = condition
            if op == "nahi":
                return not self.eval_condition(value)

        if isinstance(condition, tuple) and len(condition) == 3:
            op, left, right = condition

            if op == "aur":
                return self.eval_condition(left) and self.eval_condition(right)
            if op == "ya":
                return self.eval_condition(left) or self.eval_condition(right)

            left_val = self.eval(left)
            right_val = self.eval(right)

            if op == ">":
                if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                    raise Exception(f"Runtime Error: Cannot compare {type(left_val).__name__} and {type(right_val).__name__} with >")
                return left_val > right_val
            if op == "<":
                if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                    raise Exception(f"Runtime Error: Cannot compare {type(left_val).__name__} and {type(right_val).__name__} with <")
                return left_val < right_val
            if op == ">=":
                if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                    raise Exception(f"Runtime Error: Cannot compare {type(left_val).__name__} and {type(right_val).__name__} with >=")
                return left_val >= right_val
            if op == "<=":
                if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                    raise Exception(f"Runtime Error: Cannot compare {type(left_val).__name__} and {type(right_val).__name__} with <=")
                return left_val <= right_val
            if op == "==":
                return left_val == right_val
            if op == "!=":
                return left_val != right_val

        return bool(self.eval(condition))

    def eval(self, expr, expected_type=None):
        if isinstance(expr, ListAccess):
            items = self.env.get_var(expr.name)
            if not isinstance(items, list):
                raise Exception(f"Runtime Error: '{expr.name}' is not a list")
            return items[self.eval(expr.index)]

        if isinstance(expr, Input):
            prompt = " ".join(str(self.eval(value)) for value in expr.prompt)
            raw_value = input(f"{prompt} " if prompt else "")
            return self.convert_input(raw_value, expected_type)

        if isinstance(expr, FunctionCall):
            return self.visit_FunctionCall(expr)

        if isinstance(expr, tuple) and len(expr) == 2 and expr[0] == "var":
            _, name = expr
            return self.env.get_var(name)

        if isinstance(expr, tuple) and len(expr) == 3:
            op, left, right = expr
            left_val = self.eval(left)
            right_val = self.eval(right)

            if op == "+":
                return left_val + right_val
            if op == "-":
                return left_val - right_val
            if op == "*":
                return left_val * right_val
            if op == "/":
                if isinstance(left_val, int) and isinstance(right_val, int) and left_val % right_val == 0:
                    return left_val // right_val
                return left_val / right_val
            if op == "%":
                return left_val % right_val

        if isinstance(expr, (int, float, bool, str)) or expr is None:
            return expr

        return expr

    def convert_input(self, value, expected_type):
        if expected_type == "ginti":
            return int(value)
        if expected_type == "decimal":
            return float(value)
        if expected_type == "sachjhoot":
            normalized = value.strip().lower()
            if normalized in ("sach", "true", "1"):
                return True
            if normalized in ("jhoot", "false", "0"):
                return False
            raise Exception("Runtime Error: expected sach or jhoot")
        if expected_type == "harf":
            return value[0] if value else ""
        return value
