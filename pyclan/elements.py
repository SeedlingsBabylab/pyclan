import re

import filters

class ClanLine(object):
    """
    ClanLine is the smallest unit of subdivision of
    a CLAN file. every single line in a CLAN file is
    represented by one of these objects
    """
    def __init__(self, index, line):
        self.index = index
        self.line = line
        self.is_header = False
        self.is_end_header = False
        self.is_conv_block_delimiter = False
        self.is_paus_block_delimiter = False
        self.is_tier_line = False
        self.is_tier_without_timestamp = False
        self.multi_line_parent = None
        self.is_multi_parent = False
        self.time_onset = 0
        self.time_offset = 0
        self.total_time = 0
        self.conv_block_num = 0
        self.within_conv_block = False
        self.within_paus_block = False
        self.is_clan_comment = False
        self.is_user_comment = False
        self.is_other_comment = False
        self.xdb_line = False
        self.tier = None
        self.content = None
        self.xdb_average = 0
        self.xdb_peak = 0

    def __repr__(self):
        return self.line

    def timestamp(self):
         return "{}_{}".format(self.time_onset, self.time_offset)



class LineRange(object):

    get_user_comments = filters.user_comments
    get_tiers = filters.tier
    filter_out_tiers = filters.filter_out_tier

    def __init__(self, line_range):
        self.line_map = line_range
        self.total_time = sum(x.total_time for x in line_range)

    def __len__(self):
        return len(self.line_map)

    # def __contains__(self, key):
    #

class ClanBlock(object):
    """
    A Block refers to a range of lines in between tags labeled:

    @Bg Conversation XYZ
    blah
    blah
    blah
    @Eg Conversation XYZ

    Where XYZ is the number of the block.

    The block will include those @Bg and @Eg tags along with it

    """
    get_user_comments = filters.user_comments
    get_tiers = filters.tier
    filter_out_tiers = filters.filter_out_tier

    def __init__(self, block_index, line_map):
        self.index = block_index
        self.line_map = line_map
        self.num_tier_lines = 0

        for line in self.line_map:
            if line.is_tier_line:
                self.onset = line.time_onset
                break
        for line in reversed(self.line_map):
            if line.is_tier_line:
                self.offset = line.time_offset
                break

        for line in self.line_map:
            if line.is_tier_line:
                self.num_tier_lines += 1

        self.length = self.offset - self.onset
        self.total_time = sum(x.total_time for x in line_map)

class BlockGroup(object):
    """
    BlockGroup is a collection of ClanBlocks.

    the range of all their lines are represented in
     BlockGroup's self.line_map. If these are not contiguous
     blocks then the lines will not be contiguous (in time), but they're
     all there in a single list
    """

    get_user_comments = filters.user_comments
    get_tiers = filters.tier
    filter_out_tiers = filters.filter_out_tier

    def __init__(self, blocks):
        self.blocks = blocks
        self.line_map = [element for block in blocks for element in block.line_map]
        self.total_time = sum(x.length for x in blocks)


interval_regx = re.compile("\\x15\d+_\d+\\x15")
block_regx = re.compile("Conversation (\d+)")
pause_regx = re.compile("Pause (\d+)")
xdb_regx = re.compile("average_dB=\"([-+]?[0-9]*\.?[0-9]+)\" peak_dB=\"([-+]?[0-9]*\.?[0-9]+)\"")

