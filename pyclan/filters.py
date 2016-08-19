def user_comments(self):
    return [line for line in self.line_map if line.is_user_comment]

def block(self, block_num):
    line_map = []
    for index, line in enumerate(self.line_map):
        if line.block_num == block_num:
            line_map.append(line)

    return ClanBlock(block_num, line_map)

def blocks(self, begin=0, end=None, select=None):
    blocks = []

    if select:
        selection_list = sorted(select)
        current_block_num = selection_list[0]

        current_block = []
        for line in self.line_map:
            if line.block_num in selection_list:
                if line.block_num == current_block_num:
                    current_block.append(line)
                    if current_block_num == selection_list[-1]:
                        blocks.append(ClanBlock(current_block_num, current_block))
                        break
                else:
                    blocks.append(ClanBlock(current_block_num, current_block))
                    current_block = []
                    current_block.append(line)
                    current_block_num = line.block_num
        return blocks

    if begin and end:
        current_block_num = begin
        current_block = []
        for line in self.line_map:
            if line.block_num >= current_block_num:
                if line.block_num == current_block_num:
                    current_block.append(line)
                    if current_block_num == end:
                        blocks.append(ClanBlock(current_block_num, current_block))
                        break
                else:
                    blocks.append(ClanBlock(current_block_num, current_block))
                    current_block = []
                    current_block.append(line)
                    current_block_num = line.block_num
        return blocks

def tier(self, *tiers):
    results = []
    print tier
    for line in self.line_map:
        if line.tier in tiers:
            results.append(line)
        if line.multi_line_parent and\
           line.multi_line_parent.tier in tiers:
            results.append(line)
    return results

def time(self, begin=None, end=None):
    results = []

    region_started = False
    region_ended = False

    if begin and not end:
        for line in self.line_map:
            if line.time_onset >= begin:
                region_started = True
            if region_started:
                results.append(line)

    elif end and not begin:
        for line in self.line_map:
            if line.time_offset >= end:
                region_ended = True
            if not region_ended:
                if line.is_header:
                    continue
                results.append(line)

    elif begin and end:
        for line in self.line_map:
            if line.time_onset >= end:
                region_ended = True
            if line.time_onset >= begin:
                region_started = True
            if region_started and not region_ended:
                results.append(line)

    return results

from elements import *