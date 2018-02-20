class ParseError(Exception):
    def __init__(self, line_num, last_line):
        self.index = line_num
        self.last_line = last_line
