from Expressions.Number import Number
from Expressions.Operations.Plus import Plus
from Expressions.Operations.Minus import Minus
from Expressions.Operations.Times import Times
from Expressions.Operations.Division import Division
from Expressions.Operations.Function import Function
from Expressions.Operations.Pow import Pow
from Expressions.Operations.LogicalAnd import LogicalAnd
from Expressions.Operations.LogicalOr import LogicalOr
from Expressions.Operations.Equals import Equals
from Expressions.Operations.NotEquals import NotEquals
from Expressions.Bool import Bool
from Expressions.Var import Var
from Expressions.String import String
from Expressions.Nil import Nil
from Expressions.Exception import ExceptionClass

class Interpreter(object):

    def __init__(self, context, text):
        self.context = context
        self.text = text
        self.pos = 0
        self.current_token = None
        self.current_char = self.text[self.pos]
        self.eaten = []
        self.ops = []
        self.funcs = []

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def go_back(self):
        self.pos -= 1
        if self.pos < 0:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def error(self):
        raise Exception("Invalid Format")

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def string(self):
        result = ''
        self.advance()
        while self.current_char is not None:
            if self.current_char == '"':
                self.advance()
                return String(result)
            result += self.current_char
            self.advance()
        return Nil

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if len(result) > 0:
            return Number(int(result))
        else:
            return None

    def brackets(self):
        result = ''
        bracket_count = 1
        self.advance()
        while self.current_char is not None:
            if self.current_char == "(":
                bracket_count += 1
            if self.current_char == ")":
                bracket_count -= 1
            if bracket_count == 0:
                self.advance()
                return Interpreter(self.context, result).parse()
            result += self.current_char
            self.advance()
        return Nil()

    def advance_string(self, str):
        for i in range(len(str)):
            char = str[i]
            if self.current_char != char:
                for j in range(i-1):
                    self.go_back()
                return False
            self.advance()
        return True

    def var_declaration(self):
        self.skip_whitespace()
        name = ''
        value = ''
        while self.current_char is not None and self.current_char.isalpha():
            name += self.current_char
            self.advance()
        if len(name) <= 0:
            raise Exception("Invalid declaration")
        self.skip_whitespace()
        if self.current_char != "=":
            raise Exception("Invalid declaration")
        self.advance()
        self.skip_whitespace()
        while self.current_char is not None:
            value += self.current_char
            self.advance()
        if len(value) > 0:
            value_result = Interpreter(self.context, value).parse()
            self.context.setValueForVar(name, value_result)
            return Var(name, self.context)
        return Nil

    def function(self):
        result = ""
        params = []
        while self.current_char is not None:
            result += self.current_char
            self.advance()
        while len(self.eaten) > 0:
            item = self.eaten.pop()
            if isinstance(item, Var):
                params.append(item.name)
            else:
                break
        return Function(params, self.context, result)

    def var(self):
        result = ''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        if len(result) > 0:
            return Var(result, self.context)
        else:
            return Nil

    def eat(self, item):
        type = item.type()
        if not (type == None) and type == Function and len(self.funcs) < 1:
            self.funcs.append(item.get())
        else:
            self.eaten.append(item)

    def eatBinaryOp(self, op):
        self.ops.append(op)

    def popBinaryOp(self, current):
        if len(self.ops) > 0 and len(self.eaten) > 0:
            op = self.ops.pop()
            last = self.eaten.pop()
            current = op(last, current)
            return current
        return None

    def parse_loop(self, current):
        if self.current_char.isspace():
            self.skip_whitespace()
        if isinstance(current, Var) or isinstance(current, Number) or isinstance(current, String) or isinstance(current, Bool):
            self.eat(current)
        elif isinstance(current, Function):
            self.eat(current)
        if self.advance_string("->"):
            item = self.function()
            if isinstance(item, Function):
                current = item
        elif self.current_char.isdigit():
            current = self.integer()
            if len(self.ops) > 0 and len(self.eaten) > 0:
                op = self.ops.pop()
                last = self.eaten.pop()
                current = op(last, current)
        elif self.advance_string("true"):
            current = Bool(True)
            if len(self.ops) > 0 and len(self.eaten) > 0:
                op = self.ops.pop()
                last = self.eaten.pop()
                current = op(last, current)
        elif self.advance_string("false"):
            current = Bool(False)
            if len(self.ops) > 0 and len(self.eaten) > 0:
                op = self.ops.pop()
                last = self.eaten.pop()
                current = op(last, current)
        elif self.advance_string("**"):
            self.eatBinaryOp(Pow)
        elif self.advance_string("*"):
            self.eatBinaryOp(Times)
        elif self.advance_string("/"):
            self.eatBinaryOp(Division)
        elif self.advance_string("+"):
            self.eatBinaryOp(Plus)
        elif self.advance_string("-"):
            self.eatBinaryOp(Minus)
        elif self.advance_string("&"):
            self.eatBinaryOp(LogicalAnd)
        elif self.advance_string("|"):
            self.eatBinaryOp(LogicalOr)
        elif self.advance_string("=="):
            self.eatBinaryOp(Equals)
        elif self.advance_string("!="):
            self.eatBinaryOp(NotEquals)
        elif self.current_char == '(':
            current = self.brackets()
            popped = self.popBinaryOp(current)
            if not popped == None:
                current = popped
        elif self.advance_string("let"):
            item = self.var_declaration()
            current = item
        elif self.current_char == '"':
            current = self.string()
            popped = self.popBinaryOp(current)
            if not popped == None:
                current = popped
        else:
            current = self.var()
            popped = self.popBinaryOp(current)
            if not popped == None:
                current = popped
        return current

    def parse(self):
        current = Nil()
        try:
            while self.current_char is not None:
                current = self.parse_loop(current)
        except Exception as e:
            current = ExceptionClass(e)
        if len(self.funcs) > 0:
            params = [current]
            while len(self.eaten) > 0:
                params = [self.eaten.pop()] + params
            current = self.funcs.pop()
            current.apply(params)
        return current

    def result(self):
        item = self.parse()
        try:
            return item.to_cli()
        except Exception as e:
            return ExceptionClass(e).to_cli()
