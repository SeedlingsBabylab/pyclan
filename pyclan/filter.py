


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


from elements import *


