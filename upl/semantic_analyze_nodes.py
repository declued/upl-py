from enum import Enum

class BasicType(Enum):
    Bool        = 0
    Int         = 1
    Real        = 2

class AnalyzeNode(object):
    pass

class FuncDefAnalyzeNode(AnalyzeNode):
    def __init__(self, name, arg_types, return_type):
        self.name = name
        self.arg_types = arg_types
        self.return_type = return_type
        self.body = None

    def to_dict(self):
        return dict(
            type = "FuncDefAnalyzeNode",
            name = self.name,
            arg_types = [str(arg_type) for arg_type in self.arg_types],
            return_type = str(self.return_type),
            body = self.body and self.body.to_dict()
        )

class FuncArgAnalyzeNode(AnalyzeNode):
    def __init__(self, index, type):
        self.index = index
        self.type = type

    def to_dict(self):
        return dict(
            type = "FuncArgAnalyzeNode",
            index = self.index,
            arg_type = str(self.type)
        )

class ConstantAnalyzeNode(AnalyzeNode):
    def __init__(self, index, const_table):
        self.index = index
        self.const_table = const_table

    def to_dict(self):
        return dict(
            type = "ConstantAnalyzeNode",
            value = self.const_table[self.index][1],
            value_type = str(self.const_table[self.index][0])
        )

class FuncCallAnalyzeNode(AnalyzeNode):
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def to_dict(self):
        return dict(
            type = "FuncCallAnalyzeNode",
            function = self.function.name,
            args = [arg.to_dict() for arg in self.args]
        )

class ConditionalAnalyzeNode(AnalyzeNode):
    def __init__(self, condition, on_true, on_false):
        self.condition = condition
        self.on_true = on_true
        self.on_false = on_false

    def to_dict(self):
        return dict(
            type = "ConditionalAnalyzeNode",
            condition = self.condition.to_dict(),
            on_true = self.on_true.to_dict(),
            on_false = self.on_false.to_dict()
        )