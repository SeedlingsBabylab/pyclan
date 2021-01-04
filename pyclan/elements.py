import re
from . import filters
from .regexes import *


class ClanLine(object):
    """
    ClanLine is the smallest unit of subdivision of
    a CLAN file. every single line in a CLAN file is
    represented by one of these objects
    """

    def __init__(self, index, line):
        self.index = index
        if line[-1] != "\n":
            line += "\n"
        self.line = line
        self.is_header = False
        self.is_end_header = False
        self.is_conv_block_delimiter = False
        self.is_paus_block_delimiter = False
        self.is_tier_line = False
        self.is_tier_without_timestamp = False
        self.multi_line_parent = None
        self.is_multi_parent = False
        self.onset = 0
        self.offset = 0
        self.total_time = 0
        self.conv_block_num = 0
        self.within_conv_block = False
        self.within_paus_block = False
        self.is_clan_comment = False
        self.is_user_comment = False
        self.is_user_comment_child = False
        self.is_pho = False
        self.is_other_comment = False
        self.xdb_line = False
        self.tier = None
        self.content = None
        self.xdb_average = 0
        self.xdb_peak = 0
        self._has_timestamp = False
        self.breaks = []
        self.in_skip_region = None
        self.parent_tier = None

        self.annotations = []
        self.user_comment = None
        self.phos = []

    def __repr__(self):
        return self.line

    def timestamp(self):
        return "{}_{}".format(self.onset, self.offset)


class LineRange(object):

    get_user_comments = filters.user_comments
    get_tiers = filters.tier
    filter_out_tiers = filters.filter_out_tier
    shift_timestamps = filters.shift_timestamps
    clear_pho_comments = filters.clear_pho

    def __init__(self, line_range):
        self.line_map = line_range
        self.total_time = sum(x.total_time for x in line_range)

    def __len__(self):
        return len(self.line_map)


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
    shift_timestamps = filters.shift_timestamps
    clear_pho_comments = filters.clear_pho

    def __init__(self, block_index, line_map):
        self.index = block_index
        self.line_map = line_map
        self.num_tier_lines = 0

        for line in self.line_map:
            if line.is_tier_line:
                self.onset = line.onset
                break
        for line in reversed(self.line_map):
            if line.is_tier_line:
                self.offset = line.offset
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
    shift_timestamps = filters.shift_timestamps
    clear_pho_comments = filters.clear_pho

    def __init__(self, blocks):
        self.blocks = blocks
        self.line_map = [
            element for block in blocks for element in block.line_map]
        self.total_time = sum(x.length for x in blocks)
        self.block_map = {}
        for x in blocks:
            self.block_map[x.index] = x

    def get(self, n):
        """
        get the block with number 'n'
        """
        return self.block_map[n]


class Annotation(object):
    """
    Annotation is a class to encapsulate all our object word
    annotations and the metadata associated with them.
    """

    def __init__(self, tier, word, utt_type, present,
                 speaker, annotation_id, onset=0, offset=0, line_num=0):
        self.tier = tier
        self.word = word
        self.utt_type = utt_type
        self.present = present
        self.speaker = speaker
        self.annotation_id = annotation_id
        self.onset = onset
        self.offset = offset
        self.orig_string = ""
        self.line_num = line_num
        self.index = 0
        self.pho_annot = ""
        self.pho = None

    def __repr__(self):
        if self.annotation_id:
            return "{} &={}_{}_{}_{}".format(self.word, self.utt_type, self.present, self.speaker, self.annotation_id)
        else:
            return "{} &={}_{}_{}".format(self.word, self.utt_type, self.present, self.speaker)
    def annot_string(self, word=True, utt_type=True, present=True, speaker=True, annotation_id=True):

        w = self.word if word else "XXXX"
        u = self.utt_type if utt_type else "X"
        p = self.present if present else "X"
        s = self.speaker if speaker else "XXX"
        i = self.annotation_id if annotation_id else "XXXXXXXXX"

        return "{} &={}_{}_{}_{}".format(w, u, p, s, i)

    def timestamp(self):
        return "{}_{}".format(self.onset, self.offset)


class UserComment(object):
    """
    UserComment is a class to encapsulate all user comments and the metadata associated with them.
    """
    orig_string = None
    root_line = None
    parent_line = None
    annotation_id = None

    def __init__(self, line_content):
        self.orig_string = line_content
        match_id = re.search(r'####([A-Za-z0-9]{8})', line_content)
        if match_id:
            self.annotation_id = match_id.group(0).lstrip("####")

    def __repr__(self):
        return self.orig_string

    def trace_root(self, parent_line):
        self.parent_line = parent_line
        if parent_line.is_user_comment_child:
            self.root_line = parent_line.user_comment.root_line
        else:
            self.root_line = parent_line
        if self.annotation_id:
            self.__trace_add_root_annot_id()

    def __trace_add_root_annot_id(self):
        cur_line = self.parent_line
        while cur_line:
            cur_line.user_comment.annotation_id = self.annotation_id
            cur_line = cur_line.user_comment.parent_line


class Pho(object):
    """
    Pho is a class to encapsulate all user comments and the metadata associated with them.
    """

    content = None
    annotation_ref = None
    pho_id = None
    annotation = None

    def __init__(self, content):
        content = content.strip()
        num_underscore = content.count('_')
        if num_underscore == 0:
            self.content = content
        elif num_underscore == 1:
            self.content = content.split('_')[0]
            self.pho_id = content.split('_')[1]
        elif num_underscore == 2:
            self.content = content.split('_')[0]
            self.pho_id = content.split('_')[1]
            self.annotation_ref = content.split('_')[2]

    def __repr__(self):
        if self.annotation_ref:
            return "{}_{}_{}".format(self.content, self.pho_id, self.annotation_ref)
        elif self.pho_id:
            return "{}_{}".format(self.content, self.pho_id)
        else:
            return self.content


