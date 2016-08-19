import re

import filter

class ClanLine(object):
    def __init__(self, index, line):
        self.index = index
        self.line = line
        self.is_header = False
        self.is_block_delimiter = False
        self.is_tier_line = False
        self.multi_line_parent = None
        self.is_multi_parent = False
        self.time_onset = 0
        self.time_offset = 0
        self.block_num = 0
        self.within_conv_block = False
        self.is_clan_comment = False
        self.is_user_comment = False
        self.xdb_line = False
        self.tier = None
        self.content = None
        self.xdb_average = 0
        self.xdb_peak = 0

    def timestamp(self):
         return "{}_{}".format(self.time_onset, self.time_offset)

class ClanBlock(object):

    get_user_comments = filter.user_comments

    def __init__(self, block_index, line_map):
        self.index = block_index
        self.line_map = line_map

        for line in self.line_map:
            if line.time_onset != 0:
                self.onset = line.time_onset
                break
        for line in reversed(self.line_map):
            if line.time_offset != 0:
                self.offset = line.time_offset
                break

        self.length = self.offset - self.onset



interval_regx = re.compile("\\x15\d+_\d+\\x15")
block_regx = re.compile("Conversation (\d+)")
xdb_regx = re.compile("average_dB=\"([-+]?[0-9]*\.?[0-9]+)\" peak_dB=\"([-+]?[0-9]*\.?[0-9]+)\"")