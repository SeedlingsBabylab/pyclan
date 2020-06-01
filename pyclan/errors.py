class ParseError(Exception):
    def __init__(self, line_num, last_line, info=''):
        self.index = line_num
        self.last_line = last_line
        self.info = info

    def __repr__(self):
        ret = """Parser Error:
            index: {}
            line: {}
            Additional Info: {}""".format(self.index, self.last_line, self.info)
        
        return ret

    # We need to redefine our own __str__ because Exception base class defines
    # this (which ends up empty since the args attribute is empty)
    def __str__(self):
        return self.__repr__()
