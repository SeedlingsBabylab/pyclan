import re
from pyclan import codecheck
from collections import OrderedDict
from .regexes import *
from .errors import ParseError
from pdb import set_trace
import os.path

def check_annotation(annot):
    error = []
    # for annot in annotArr:
    try:
        if "*" in annot.tier:
            assert(codecheck.check_tier_audio(annot.tier))
        else:
            assert(codecheck.check_tier_audio("*"+annot.tier))
        assert(codecheck.check_word_audio(annot.word))
        assert(codecheck.check_utterance_type_audio(annot.utt_type))
        assert(codecheck.check_object_present_audio(annot.present))
        assert(codecheck.check_speaker_audio(annot.speaker))
        assert(codecheck.check_onset_offset(str(annot.onset), str(annot.offset)))
    except AssertionError:
        error.append(annot.__repr__() + " " + str(annot.onset) + " " + str(annot.offset))
            #print annot.tier, annot.word, annot.utt_type, annot.present, annot.speaker, str(annot.onset), str(annot.offset)
    return error

def user_comments(self):
    return [line for line in self.line_map if line.is_user_comment]


def conv_block(self, block_num):
    line_map = []
    for index, line in enumerate(self.line_map):
        if line.conv_block_num == block_num:
            line_map.append(line)

    return ClanBlock(block_num, line_map)


def conv_blocks(self, begin=1, end=None, select=None):
    """ Get specified conversation blocks

    Args:
        self:
        begin (int): beginning of contiguous range (default start from beginning)
        end (end): end of contiguous range (default go to the end)
        select : list of specific block indices to retrieve
                (result will be sorted in ascending order)

    Returns: a BlockGroup of specified conversation blocks
    """
    if not end:
        end = self.num_blocks

    blocks = OrderedDict()
    select = select if select else list(range(begin, end+1))

    for x in select:
        blocks[x] = []

    for line in self.line_map:
        if line.conv_block_num in select:
            blocks[line.conv_block_num].append(line)

    blocks = [ClanBlock(block_num, lines) for block_num, lines in list(blocks.items())]
    return BlockGroup(blocks)



    # select = range(begin, end+1)

    # for x in select:
    #     blocks[x] = []
    #
    # for line in self.line_map:
    #     if line.conv_block_num in select:
    #         blocks[line.conv_block_num].append(line)
    #
    # blocks = [ClanBlock(block_num, lines) for block_num, lines in blocks.items()]
    # return BlockGroup(blocks)

    # for block_num in selection_list:
    #     temp_block_lines = [line for line in self.line_map
    #                             if line.conv_block_num == block_num]
    #     blocks.append(ClanBlock(block_num, temp_block_lines))
    #
    # return BlockGroup(blocks)


def tier(self, *tiers):
    """ Get all ClanLines with specified tiers

    Args:
        self:
        *tiers: a list of tiers, e.g. ["MAN", "FAN", "CHN

    Returns: LineRange with all the lines
    """
    results = []
    for line in self.line_map:
        if line.tier in tiers:
            results.append(line)
        if line.multi_line_parent and\
           line.multi_line_parent.tier in tiers:
            results.append(line)
    return LineRange(results)


def filter_out_tier(self, *tiers):
    """ Remove all lines with specified tiers

    This function scans the lines that are held by the calling object
    and removes all the lines that contain the specified tiers.

    Args:
        self:
        *tiers (str): variable number of arguments specifying
                      which tiered lines to remove

    Returns:
        LineRange: With all the lines that were filtered out

    Examples:
        >>> clan_file = ClanFile("/path/to/file.cha")
        >>> block_33 = clan_file.get_block(33)
        >>> filtered_line_range = block_33.filter_out_tiers("MAN", "CHN")

    Will delete all the "MAN" and "CHN" tiered lines from the object
    representing block 33.
    """
    results = []
    for index, line in enumerate(self.line_map):
        if line.tier in tiers:
            results.append(line)
            del self.line_map[index]
    return LineRange(results)


def time(self, begin=None, end=None):
    """ Get all lines within a time range

    Args:
        self:
        begin (int): beginning time in milliseconds
        end (int): ending time in milliseconds

    Returns:
        LineRange: With all the lines within the time range


    Examples:
        >>> clan_file = ClanFile("/path/to/file.cha")
        >>> lines_in_time_range = clan_file.get_within_time(begin=12345, end=123456)
    """
    results = []

    region_started = False
    region_ended = False

    if begin and not end:
        for line in self.line_map:
            if line.onset >= begin:
                region_started = True
            if region_started:
                results.append(line)

    elif end and not begin:
        for line in self.line_map:
            if line.offset >= end:
                region_ended = True
            if not region_ended:
                if line.is_header:
                    continue
                results.append(line)

    elif begin and end:
        for line in self.line_map:

            if line.onset >= end:
                region_ended = True
            if line.onset >= begin:
                region_started = True
            if region_started and not region_ended:
                results.append(line)

    return LineRange(results)


def get_with_keyword(self, keyword):
    """
    Args:
        self:
        keyword: some string to search for

    Returns:
    """
    line_map = []

    for index, line in enumerate(self.line_map):
        if line.content:
            if keyword in line.content:
                line_map.append(line)

    return LineRange(line_map)


def replace_with_keyword(self, line_range, orig_key, new_key):
    for line in line_range.line_map:
        if orig_key in line.content:
            line.content = line.content.replace(orig_key, new_key)
            line.line = line.line.replace(orig_key, new_key)



def replace_comment(self, orig_keywords=[], new_comment=""):
    """
    Replace the comment lines containing any of the keywords in a given
    list, with a new string. This will only handle original comments
    which span a single line

    Args:
        self:
        orig_keywords: keywords to look for in replaced comments
        new_comment: the content of the comment which replaces

    Returns:

    """
    new_linemap = []
    for line in self.line_map:
        if line.is_user_comment and any(x in line.line for x in orig_keywords):
            line.line = "%xcom:\t{}{}".format(new_comment,
                                              line.line[line.line.find("\n"):])
        new_linemap.append(line)


def get_with_speaker(self, speaker):
    line_map = []
    for line in self.line_map:
        if line.is_tier_line:
            matches = code_regx.findall(line.content)
            if matches:
                for m in matches:
                    if m[7] == speaker:
                        line_map.append(line)
    return line_map

def get_with_time(self, onset, offset):
    results = []
    for line in self.line_map:
        if line.onset == onset and line.offset == offset:
            results.append(line)


def shift_timestamps(self, dt):
    for line in self.line_map:
        orig_tstamp = "{}_{}".format(line.onset, line.offset)
        new_onset = line.onset+dt
        new_offset = line.offset+dt
        line.onset = new_onset
        line.offset = new_offset

        interv_re = interval_regx.search(line.line)
        if interv_re:
            line.line = line.line.replace(orig_tstamp,
                                          "{}_{}".format(new_onset,
                                                         new_offset))

def clear_pho(self):
    for line in self.line_map:
        if line.line.startswith("%pho:"):
            line.line = "%pho:\t\n"

def delete_pho(self):
    new_map = [x for x in self.line_map if not x.line.startswith("%pho:")]
    self.line_map = new_map
    self.reindex()

def _preparse_flatten(path):
    """
    Flatten the file so none of the lines wrap to the next line.

    Note: can only handle comments spanning at most 2 lines
    :param:  path
    :return: original line list, flattened line list, flatten to original index
    dictionary, original to flatten index dictionary
    """

    flattenedlines = []
    breaks = []
    temp_block = []
    tier = False
    comment = False
    bp = 0
    last_tier_index = 0
    with open(path, "r") as input:
        # try:
        for index, line in enumerate(input):
            timestamp = interval_regx.search(line)
            lineclean = line.strip()

            if timestamp and not lineclean.endswith(timestamp.group(0)):

                raise ParseError(index, line)
            if tier and line.startswith("\t"):
                if not timestamp:
                    temp_block.append(line)
                    continue
                elif len(temp_block):
                    temp_block.append(line)
                    newline, arr = _block(temp_block)
                    last_tier_index = len(flattenedlines)
                    flattenedlines.append(newline)
                    breaks.append(arr)
                    temp_block = []
                    continue
            #Even if the last tier line is not ended with timestamp, it is flattened and temp_block emptied
            if (tier or comment) and not line.startswith("\t"):
                tier = False
                comment = False
                if len(temp_block):
                    newline, arr = _block(temp_block)
                    if tier:
                        last_tier_index = len(flattenedlines)
                    flattenedlines.append(newline)
                    breaks.append(arr)
                    temp_block = []
            if line.startswith("*"):
                tier = True
                if not timestamp:
                    temp_block.append(line)
                    continue
            if line.startswith("%com:") or line.startswith("%xcom:"):
                comment = True
                temp_block.append(line)
                continue
            if comment and line.startswith("\t") and not timestamp:
                temp_block.append(line)
                continue
            if (not tier) and timestamp and line.startswith("\t"):
                lastline = flattenedlines[last_tier_index]
                if not interval_regx.search(lastline):
                    arr = breaks[last_tier_index]
                    arr.append(len(lastline)+1)
                    breaks[last_tier_index] = arr
                    flattenedlines[last_tier_index] = lastline + " " + line.strip()
                else:
                    flattenedlines.insert(last_tier_index+1, line)
                    breaks.insert(last_tier_index+1, [0])
                    last_tier_index += 1
                continue
            if tier:
                last_tier_index = len(flattenedlines)
            flattenedlines.append(line)
            breaks.append([0])
        # except Exception, e:
        #     print e
        #     raise ParseError(index, line)
    return flattenedlines, breaks

def _block(temp_block):
    bp = 0
    if temp_block[0].startswith("*") or temp_block[0].startswith("%"):
        newline = ""
    else:
        newline = "\t"
    arr = []
    for each in temp_block:
        arr.append(bp)
        newline += each.strip() + " "
        bp += len(each.strip()) + 1
    newline = newline[:-1] + "\n"
    return newline, arr

    # new_lines = []
    #
    # line_index = 0
    #
    # while line_index < len(self.line_map):
    #     line = self.line_map[line_index]
    #     if line.is_tier_line:
    #         multi_group = []
    #         multi_group.append(line)
    #         runner_index = line_index + 1
    #         found_time_stamp = False
    #         if line._has_timestamp:
    #             timestamp = line.timestamp()
    #             found_time_stamp = True
    #         while runner_index < len(self.line_map) \
    #               and self.line_map[runner_index].line.startswith('\t') \
    #               and not found_time_stamp:
    #             multi_group.append(self.line_map[runner_index])
    #             if self.line_map[runner_index]._has_timestamp:
    #                 found_time_stamp = True
    #                 timestamp = self.line_map[runner_index].timestamp()
    #             runner_index += 1
    #         flatten_line = _flatten(len(new_lines), multi_group, timestamp)
    #         new_lines.append(flatten_line)
    #         flatten_line.index = len(new_lines)
    #         line_index = runner_index
    #     elif line.is_user_comment:
    #         multi_group = []
    #         multi_group.append(line)
    #         runner_index = line_index + 1
    #         while runner_index < len(self.line_map) \
    #               and self.line_map[runner_index].line.startswith('\t'):
    #             multi_group.append(self.line_map[runner_index])
    #             runner_index += 1
    #         flatten_line = _flatten_comment(len(new_lines), multi_group)
    #         new_lines.append(flatten_line)
    #         flatten_line.index = len(new_lines)
    #         line_index = runner_index
    #     else:
    #         new_lines.append(line)
    #         line.index = len(new_lines)
    #         line_index += 1

    # new_lines = []
    # multi_group_comment = []
    # multi_group_other = []

    # for i, line in enumerate(self.line_map):
    #
    #     if line.line.startswith("\t"): #This is middle part of a multiline
    #         if line.is_tier_line: #This is part of a multi tier line
    #             multi_group_other.append(line)
    #             if line._has_timestamp:
    #                 flatten_line = _flatten(len(new_lines), multi_group_other, line.timestamp())
    #                 new_lines.append(flatten_line)
    #                 flatten_line.index = len(new_lines)
    #                 del multi_group_other[:]
    #         elif line.is_user_comment_child: #This is child of a comment line root
    #                 multi_group_comment.append(line)
    #         else:
    #             new_lines.append(line)
    #             line.index = len(new_lines)
    #     else: #This is a single line or start of a multiline
    #         if line.is_tier_line:
    #             if multi_group_other: #Non empty group found
    #                 flatten_line = _flatten(len(new_lines), multi_group_other, multi_group_other[0].timestamp())
    #                 new_lines.append(flatten_line)
    #                 flatten_line.index = len(new_lines)
    #                 del multi_group_other[:]
    #             multi_group_other.append(line)
    #         elif line.is_user_comment:
    #             if multi_group_comment: #Found a new comment root, but buffer not empty
    #                 flatten_line = _flatten_comment(len(new_lines), multi_group_comment)
    #                 new_lines.append(flatten_line)
    #                 flatten_line.index = len(new_lines)
    #                 del multi_group_comment[:]
    #             multi_group_comment.append(line)
    #         else:
    #             new_lines.append(line)
    #             line.index = len(new_lines)

    # self.line_map = new_lines
    # self.reindex_timestamps()
    # self.flat = True


def _flatten(idx, group, ts):
    final_string = ""
    tier = None
    for i,  cell in enumerate(group):
        if i > 0:
            final_string += " " + cell.content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        else:
            final_string += cell.content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        tier = cell.tier

    if "." in final_string:
        line_str = "*{}:\t{} \x15{}\x15".format(cell.tier, final_string, ts)
    else:
        line_str = "*{}:\t{} . \x15{}\x15".format(cell.tier, final_string, ts)
    line = ClanLine(idx, line_str)
    line.tier = tier
    line.onset = cell.onset
    line.offset = cell.offset
    line.is_tier_line = cell.is_tier_line
    line.conv_block_num = cell.conv_block_num
    line.within_conv_block = cell.within_conv_block
    if line.line.startswith("*"):
        line.content = line.line.split("\t")[1].replace(ts+"\n", "")
    elif line.line.startswith("%"):
        if line.line == "%pho:\r\n":
            line.content = ""
        else:
            line.content = line.line.split("\t")[1]
    return line

def _flatten_comment(idx, lines):
    # new_line = "".join([x.line for x in lines])
    # try:
    #     first_tab_idx = new_line.index("\t")
    # except:
    #     print new_line
    # prefix = new_line[:first_tab_idx+1].rstrip('\t')
    # new_line = prefix + new_line[first_tab_idx:]
    # #new_line = prefix + re.sub("[\t]+", "\t", new_line[first_tab_idx:])
    # new_line = new_line.replace("\n", "")
    for line in lines:
        if line.line.startswith('\t'):
            new_line += ' ' + line.line.rstrip().lstrip('\t')
        else:
            new_line = line.line.rstrip()
    line = ClanLine(idx, new_line)
    line.is_user_comment = True
    line.onset = lines[0].onset
    line.offset = lines[0].offset
    line.conv_block_num = lines[0].conv_block_num
    return line

def reindex_ts(self):
    self.ts_index = {}
    for index, line in enumerate(self.line_map):
        line.index = index
        ts = line.timestamp()
        if ts in self.ts_index:
            self.ts_index[ts].append(line)
        else:
            self.ts_index[ts] = [line]


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

    get_user_comments = user_comments
    get_tiers = tier
    filter_out_tiers = filter_out_tier
    shift_timestamps = shift_timestamps
    clear_pho_comments = clear_pho

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
    get_user_comments = user_comments
    get_tiers = tier
    filter_out_tiers = filter_out_tier
    shift_timestamps = shift_timestamps
    clear_pho_comments = clear_pho

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

    get_user_comments = user_comments
    get_tiers = tier
    filter_out_tiers = filter_out_tier
    shift_timestamps = shift_timestamps
    clear_pho_comments = clear_pho

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



