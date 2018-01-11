import re
from collections import OrderedDict

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
    select = select if select else range(begin, end+1)

    for x in select:
        blocks[x] = []

    for line in self.line_map:
        if line.conv_block_num in select:
            blocks[line.conv_block_num].append(line)

    blocks = [ClanBlock(block_num, lines) for block_num, lines in blocks.items()]
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

def flatten(self):
    """
    Flatten the file so none of the lines wrap to the next line.

    Note: can only handle comments spanning at most 2 lines
    :param self:
    :return:
    """
    new_lines = []
    multi_group = []
    for i, line in enumerate(self.line_map):

        if line.line.startswith("\t") \
                and multi_group\
                and multi_group[0].is_user_comment\
                and not line.is_tier_line:
            multi_group.append(line)
            new_lines.append(_flatten_comment(len(new_lines),
                                              multi_group))
            del multi_group[:]
            continue

        elif line.is_tier_line and line.line.startswith("\t") and not multi_group:
            multi_group.append(line)
            if line._has_timestamp:
                new_lines.append(_flatten(len(new_lines), multi_group, line.timestamp()))
                del multi_group[:]
            # del multi_group[:]
            continue

        elif multi_group and line.is_tier_line and line.line.startswith("\t") and multi_group[0].is_user_comment:
            new_lines.append(_flatten_comment(len(new_lines), multi_group))
            del multi_group[:]

            multi_group.append(line)
            if line._has_timestamp:
                new_lines.append(_flatten(len(new_lines), multi_group, line.timestamp()))
                del multi_group[:]
                continue
            # del multi_group[:]
            # continue

        elif line.is_tier_line:
            # if multi_group and multi_group[0].is_user_comment:
            #     new_lines.append(_flatten_comment(len(new_lines), multi_group))
            #     multi_group[:]
            if line.is_multi_parent or line.multi_line_parent:
                multi_group.append(line)
                if line._has_timestamp:
                    new_lines.append(_flatten(len(new_lines), multi_group, line.timestamp()))
                    del multi_group[:]
            else:
                line.index = len(new_lines)
                new_lines.append(line)
        elif line.is_user_comment:
            multi_group.append(line)
        else:
            if multi_group and multi_group[0].is_user_comment:
                new_lines.append(_flatten_comment(len(new_lines), multi_group))
                multi_group[:]
            line.index = len(new_lines)
            new_lines.append(line)
            del multi_group[:]

    self.line_map = new_lines
    self.reindex_timestamps()
    self.flat = True


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
    new_line = " ".join([x.line for x in lines])
    first_tab_idx = new_line.index("\t")
    prefix = new_line[:first_tab_idx+1]
    new_line = prefix + new_line[first_tab_idx:].replace("\t", "")
    new_line = new_line.replace("\n", "")
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


from elements import *
from clanfile import *