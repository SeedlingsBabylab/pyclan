class ParseError(Exception):
    def __init__(self, line_num, last_line):
        self.index = line_num
        self.last_line = last_line

    def __repr__(self):
    	return "Parser Error:\n\t index: {}\n\tline: {}".format(self.index, self.last_line)