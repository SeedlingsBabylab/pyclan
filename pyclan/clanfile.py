import csv
import os

from pyclan import filters
from pyclan import elements

class ClanFile(object):

    get_user_comments = filters.user_comments
    get_conv_block = filters.conv_block
    get_conv_blocks = filters.conv_blocks
    get_tiers = filters.tier
    get_within_time = filters.time
    get_with_keyword = filters.get_with_keyword
    get_with_speaker = filters.get_with_speaker
    replace_with_keyword = filters.replace_with_keyword
    replace_comments = filters.replace_comment

    end_tag = "@End"

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.num_full_blocks = 0
        self.full_block_range = False
        self.block_index = [] # list of all the full block indices in this file
        self.line_map = self.parse_file()
        self.total_time = sum(line.total_time for line in self.line_map if line.is_tier_line)

    def parse_file(self):
        line_map = []
        with open(self.clan_path, "r") as input:
            current_conv_block = 0
            current_paus_block = 0

            conv_block_started = False
            conv_block_ended = False

            last_conv_block_type = ""
            last_conv_block_num = 0

            paus_block_started = False
            paus_block_ended = False

            last_line = None
            seen_tier = False
            for index, line in enumerate(input):
                clan_line = elements.ClanLine(index, line)
                if line.startswith("*"):
                    seen_tier = True
                if last_line:
                    clan_line.time_onset = last_line.time_onset
                    clan_line.time_offset = last_line.time_offset
                else:
                    clan_line.time_onset = 0
                    clan_line.time_offset = 0
                if clan_line.time_onset is None and index > 20:
                    print
                if (line.startswith("@") or index < 11) and not seen_tier:
                    block_delimiter = False
                    if line.startswith("@Bg") or line.startswith("@Eg"):
                        conv_block_regx_result = elements.block_regx.search(line)
                        paus_block_regx_result = elements.pause_regx.search(line)
                        if conv_block_regx_result:
                            current_conv_block = int(conv_block_regx_result.group(1))
                            block_delimiter = True
                            if "@Bg" in line:
                                last_conv_block_type = "@Bg"
                                last_conv_block_num = current_conv_block
                                conv_block_started = True
                                conv_block_ended = False

                            if "@Eg" in line:
                                if last_conv_block_type == "@Bg" and last_conv_block_num == current_conv_block:
                                        self.num_full_blocks += 1
                                        self.block_index.append(current_conv_block)
                                last_conv_block_type = "@Eg"
                                last_conv_block_num = current_conv_block
                                conv_block_started = False
                                conv_block_ended = True
                                clan_line.is_conv_block_delimiter = True
                                clan_line.conv_block_num = current_conv_block
                                clan_line.within_conv_block = True
                                line_map.append(clan_line)
                                last_line = clan_line
                                if last_line:
                                    clan_line.time_onset = last_line.time_onset
                                    clan_line.time_offset = last_line.time_offset
                                else:
                                    clan_line.time_onset = 0
                                    clan_line.time_offset = 0
                                continue
                        clan_line.is_conv_block_delimiter = block_delimiter
                        if conv_block_started:
                            clan_line.conv_block_num = current_conv_block
                            clan_line.within_conv_block = True
                        else:
                            clan_line.conv_block_num = 0
                        line_map.append(clan_line)
                        last_line = clan_line
                        continue

                    clan_line.is_header = True
                    if "@End" in line:
                        clan_line.is_end_header = True

                    line_map.append(clan_line)
                    last_line = clan_line
                    continue

                if line.startswith("\t"):
                    if last_line.is_user_comment or last_line.is_tier_line or last_line.is_other_comment:
                        last_line.is_multi_parent = True
                        clan_line.multi_line_parent = last_line
                        if last_line.is_tier_line:
                            clan_line.is_tier_line = True
                            clan_line.tier = clan_line.multi_line_parent.tier
                    else:
                        clan_line.multi_line_parent = last_line.multi_line_parent
                        if clan_line.multi_line_parent.is_tier_line:
                            clan_line.is_tier_line = True
                            clan_line.tier = clan_line.multi_line_parent.tier


                if line.startswith("%"):
                    clan_line.content = line.split("\t")[1]

                    if line.startswith("%com:") or line.startswith("%xcom:"):
                        if line.count("|") > 3:
                            clan_line.clan_comment = True
                        else:
                            clan_line.is_user_comment = True
                        # print line
                        # clan_line.content = line.split("\t")[1]

                        if conv_block_started:
                            clan_line.conv_block_num = current_conv_block
                            clan_line.within_conv_block = True
                        else:
                            clan_line.conv_block_num = 0

                    elif line.startswith("%xdb:"):
                        clan_line.xdb_line = True
                        xdb_regx_result = elements.xdb_regx.search(line)
                        if xdb_regx_result:
                            clan_line.xdb_average = xdb_regx_result.group(1)
                            clan_line.xdb_peak = xdb_regx_result.group(2)

                        if conv_block_started:
                            clan_line.conv_block_num = current_conv_block
                            clan_line.within_conv_block = True
                        else:
                            clan_line.conv_block_num = 0
                    else:
                        clan_line.is_other_comment = True

                interv_regx_result = elements.interval_regx.search(line)

                if interv_regx_result:
                    timestamp = interv_regx_result.group()
                    onset = int(timestamp.split("_")[0].replace("\x15", ""))
                    offset = int(timestamp.split("_")[1].replace("\x15", ""))
                    clan_line.time_onset = onset
                    clan_line.time_offset = offset
                    clan_line.total_time = offset - onset

                    # there's no timestamp on a tier line
                    # (it wraps around to the next line)
                    if last_line.is_tier_without_timestamp:
                        last_line.time_onset = onset
                        last_line.time_offset = offset
                        last_line.total_time = offset - onset

                    if conv_block_started:
                        clan_line.conv_block_num = current_conv_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.conv_block_num = 0
                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(timestamp+"\n", "")
                        clan_line.is_tier_line = True
                    if line.startswith("\t"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(timestamp+"\n", "")
                        clan_line.is_tier_line = True
                else:
                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace("\n", "")
                        clan_line.is_tier_line = True
                        clan_line.is_tier_without_timestamp = True

                codes = elements.code_regx.findall(line)
                if codes:
                    for code in codes:
                        word = code[0]
                        utt_type = code[3]
                        present = code[5]
                        speaker = code[7]
                        annot = elements.Annotation(word, utt_type, present, speaker,
                                                    onset = clan_line.time_onset,
                                                    offset = clan_line.time_offset)

                        clan_line.annotations.append(annot)

                line_map.append(clan_line)
                last_line = clan_line

        # self.num_blocks = current_conv_block
        return line_map

    def insert_line(self, line, index):
        """
        Insert a ClanLine into the middle of a ClanFile at
        a given index.

        If index == 15, then the current ClanLine at 15 will
        be pushed to 16, and the new ClanLine will take its
        place.

        Args:
            line: ClanLine object to insert into the ClanFile
            index: index to insert at
        """
        self.line_map.insert(index, line)
        for i, x in enumerate(self.line_map):
            x.index = i

    def annotations(self):

        annots = [x for line in self.line_map for x in line.annotations]
        return annots

    def block_map(self):
        return True

    def get_header(self):
        return [line for line in self.line_map
                    if line.is_header]

    def write_entries_to_csv(self, path):
        with open(path, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["file", "line", "timestamp"])


    def write_to_cha(self, path):
        with open(path, "wb") as output:
            for line in self.line_map:
                output.write(line.line)

    def new_file_from_blocks(self, path, blocks=[], rewrite_timestamps=False,
                             begin=1, end=None):
        """
        This produces a new cha file with only the blocks specified

        Args:
            path: path to the new output cha file
            blocks: list of indices of blocks
            rewrite_timestamps: if True, then timestamps will be rewritten to
                                start from 0 and be contiguous with each other

        """
        blocks = sorted(blocks) #make sure they're in ascending order

        with open(path, "wb") as output:
            header = self.get_header()
            if blocks:
                blocks = self.get_conv_blocks(select=blocks)
            else:
                blocks = self.get_conv_blocks(begin=begin, end=end)

            for line in header:
                if not line.is_end_header:
                    output.write(line.line)

            for line in blocks.line_map:
                output.write(line.line)

            output.write(self.end_tag)
