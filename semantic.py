# ==========================================
# URDU LANGUAGE SEMANTIC ANALYZER
# ==========================================

from urdu_ast import *


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def declare(self, name, type_, value=None):
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: '{name}' already declared in this scope")

        self.scopes[-1][name] = {
            "type": type_,
            "value": value,
        }

    def assign(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]["value"] = value
                return

        raise Exception(f"Semantic Error: '{name}' not declared")

    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        raise Exception(f"Semantic Error: '{name}' not defined")

    def exists_current_scope(self, name):
        return name in self.scopes[-1]


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()
        self.functions = {}
        self.in_function = 0

    def analyze(self, node):
        method = getattr(self, f"visit_{type(node).__name__}", self.generic)
        return method(node)

    def generic(self, node):
        raise Exception(f"No semantic rule for {type(node).__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            if isinstance(stmt, Function):
                self.register_function(stmt)

        for stmt in node.statements:
            self.analyze(stmt)

    def register_function(self, node):
        if node.name in self.functions:
            raise Exception(f"Semantic Error: function '{node.name}' already defined")

        self.functions[node.name] = {
            "params": node.params,
            "body": node.body,
            "has_return": self.contains_return(node.body),
        }

    def contains_return(self, statements):
        for stmt in statements:
            if isinstance(stmt, Return):
                return True
            if isinstance(stmt, If):
                if self.contains_return(stmt.then_block) or self.contains_return(stmt.else_block):
                    return True
            if isinstance(stmt, Loop) and self.contains_return(stmt.body):
                return True
        return False

    def visit_VarDecl(self, node):
        if self.symbols.exists_current_scope(node.name):
            raise Exception(f"Semantic Error: '{node.name}' redeclared")

        value = self.evaluate(node.value)
        self.check_type(node.type, value, "expected")
        self.symbols.declare(node.name, node.type, value)

    def visit_Assign(self, node):
        var = self.symbols.get(node.name)
        value = self.evaluate(node.value)
        self.check_type(var["type"], value, "cannot assign")
        self.symbols.assign(node.name, value)

    def visit_Print(self, node):
        for value in node.values:
            self.evaluate(value)

    def visit_If(self, node):
        self.evaluate_condition(node.condition)
        self.symbols.push()
        for stmt in node.then_block:
            self.analyze(stmt)
        self.symbols.pop()

        if node.else_block:
            self.symbols.push()
            for stmt in node.else_block:
                self.analyze(stmt)
            self.symbols.pop()

    def visit_Loop(self, node):
        self.symbols.push()
        if node.kind == "for":
            start = self.evaluate(node.start)
            end = self.evaluate(node.end)
            self.check_type("ginti", start, "for loop start must be")
            self.check_type("ginti", end, "for loop end must be")
            self.symbols.declare(node.var, "ginti", start)
        else:
            self.evaluate_condition(node.start)

        for stmt in node.body:
            self.analyze(stmt)
        self.symbols.pop()

    def visit_Function(self, node):
        self.symbols.push()
        self.in_function += 1

        for param in node.params:
            self.symbols.declare(param, "param", None)

        for stmt in node.body:
            self.analyze(stmt)

        self.in_function -= 1
        self.symbols.pop()

    def visit_Return(self, node):
        if self.in_function == 0:
            raise Exception("Semantic Error: return outside function")

        self.evaluate(node.value)

    def visit_FunctionCall(self, node):
        self.check_function_call(node)

    def visit_Input(self, node):
        for prompt_part in node.prompt:
            self.evaluate(prompt_part)

    def visit_ListNode(self, node):
        items = [self.evaluate(item) for item in node.items]
        self.symbols.declare(node.name, "list", items)

    def visit_ListAdd(self, node):
        list_var = self.symbols.get(node.name)
        if list_var["type"] != "list":
            raise Exception(f"Semantic Error: '{node.name}' is not a list")
        self.evaluate(node.value)

    def visit_ListRemove(self, node):
        list_var = self.symbols.get(node.name)
        if list_var["type"] != "list":
            raise Exception(f"Semantic Error: '{node.name}' is not a list")
        self.evaluate(node.value)

    def check_function_call(self, node, used_as_expression=False):
        if node.name not in self.functions:
            raise Exception(f"Semantic Error: function '{node.name}' not defined")

        func = self.functions[node.name]
        if len(node.args) != len(func["params"]):
            print(f"Warning: argument count mismatch for function '{node.name}'")

        for arg in node.args:
            self.evaluate(arg)

        if used_as_expression and not func["has_return"]:
            print(f"Warning: function '{node.name}' returns nothing")

    def check_type(self, type_, value, prefix):
        if value is None:
            return

        if type_ == "ginti" and (not isinstance(value, int) or isinstance(value, bool)):
            raise Exception(f"Type Error: {prefix} integer")
        if type_ == "decimal" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            raise Exception(f"Type Error: {prefix} float")
        if type_ == "text" and not isinstance(value, str):
            raise Exception(f"Type Error: {prefix} text")

    def evaluate_condition(self, condition):
        if condition is None:
            return False

        if isinstance(condition, tuple) and len(condition) == 2:
            op, value = condition
            if op == "nahi":
                result = self.evaluate_condition(value)
                return None if result is None else not result

        if isinstance(condition, tuple) and len(condition) == 3:
            op, left, right = condition

            if op == "aur":
                left_result = self.evaluate_condition(left)
                right_result = self.evaluate_condition(right)
                if left_result is None or right_result is None:
                    return None
                return left_result and right_result
            if op == "ya":
                left_result = self.evaluate_condition(left)
                right_result = self.evaluate_condition(right)
                if left_result is None or right_result is None:
                    return None
                return left_result or right_result

            left_val = self.evaluate(left)
            right_val = self.evaluate(right)

            if left_val is None or right_val is None:
                return None

            if op == ">":
                return left_val > right_val
            if op == "<":
                return left_val < right_val
            if op == ">=":
                return left_val >= right_val
            if op == "<=":
                return left_val <= right_val
            if op == "==":
                return left_val == right_val
            if op == "!=":
                return left_val != right_val

        return bool(self.evaluate(condition))

    def evaluate(self, expr):
        if isinstance(expr, ListAccess):
            list_var = self.symbols.get(expr.name)
            if list_var["type"] != "list":
                raise Exception(f"Semantic Error: '{expr.name}' is not a list")
            self.evaluate(expr.index)
            return None

        if isinstance(expr, Input):
            for prompt_part in expr.prompt:
                self.evaluate(prompt_part)
            return None

        if isinstance(expr, FunctionCall):
            self.check_function_call(expr, used_as_expression=True)
            return None

        if isinstance(expr, tuple) and len(expr) == 2 and expr[0] == "var":
            _, name = expr
            return self.symbols.get(name)["value"]

        if isinstance(expr, tuple) and len(expr) == 3:
            op, left, right = expr
            left_val = self.evaluate(left)
            right_val = self.evaluate(right)

            if left_val is None or right_val is None:
                return None

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
