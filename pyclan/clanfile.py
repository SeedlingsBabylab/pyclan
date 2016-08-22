import csv
import os

import filters
from elements import *

class ClanFile(object):

    get_user_comments = filters.user_comments
    get_conv_block = filters.conv_block
    get_conv_blocks = filters.conv_blocks
    # get_paus_block = filters.paus_block
    # get_paus_blocks = filters.paus_blocks
    get_tiers = filters.tier
    get_within_time = filters.time
    get_with_keyword = filters.get_with_keyword
    replace_with_keyword = filters.replace_with_keyword

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.num_blocks = 0
        self.line_map = self.parse_file()

    def parse_file(self):
        line_map = []
        with open(self.clan_path, "rU") as input:
            current_conv_block = 0
            current_paus_block = 0
            
            conv_block_started = False
            conv_block_ended = False
            paus_block_started = False
            paus_block_ended = False

            last_line = None
            for index, line in enumerate(input):
                clan_line = ClanLine(index, line)

                if line.startswith("@") or index < 10:
                    block_delimiter = False
                    if line.startswith("@Bg") or line.startswith("@Eg"):
                        conv_block_regx_result = block_regx.search(line)
                        paus_block_regx_result = pause_regx.search(line)
                        if conv_block_regx_result:
                            current_conv_block = int(conv_block_regx_result.group(1))
                            block_delimiter = True
                            if "@Bg" in line:
                                conv_block_started = True
                                conv_block_ended = False
                            if "@Eg" in line:
                                conv_block_started = False
                                conv_block_ended = True
                                clan_line.is_conv_block_delimiter = True
                                clan_line.conv_block_num = current_conv_block
                                clan_line.within_conv_block = True
                                line_map.append(clan_line)
                                last_line = clan_line
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
                    clan_line.time_onset = None
                    clan_line.time_offset = None
                    line_map.append(clan_line)
                    last_line = clan_line
                    continue

                if line.startswith("\t"):
                    if last_line.is_user_comment or last_line.is_tier_line:
                        last_line.is_multi_parent = True
                        clan_line.multi_line_parent = last_line
                    else:
                        clan_line.multi_line_parent = last_line.multi_line_parent

                if line.startswith("%com:") or line.startswith("%xcom:"):
                    if line.count("|") > 3:
                        clan_line.clan_comment = True
                    else:
                        clan_line.is_user_comment = True
                    clan_line.content = line.split("\t")[1]

                    if conv_block_started:
                        clan_line.conv_block_num = current_conv_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.conv_block_num = 0

                if line.startswith("%xdb:"):
                    clan_line.xdb_line = True
                    xdb_regx_result = xdb_regx.search(line)
                    if xdb_regx_result:
                        clan_line.xdb_average = xdb_regx_result.group(1)
                        clan_line.xdb_peak = xdb_regx_result.group(2)

                    if conv_block_started:
                        clan_line.conv_block_num = current_conv_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.conv_block_num = 0


                interv_regx_result = interval_regx.search(line)

                if interv_regx_result:
                    timestamp = interv_regx_result.group()
                    onset = int(timestamp.split("_")[0].replace("\x15", ""))
                    offset = int(timestamp.split("_")[1].replace("\x15", ""))
                    clan_line.time_onset = onset
                    clan_line.time_offset = offset
                    clan_line.total_time = offset - onset
                    if conv_block_started:
                        clan_line.conv_block_num = current_conv_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.conv_block_num = 0
                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(timestamp+"\n", "")
                        clan_line.is_tier_line = True
                line_map.append(clan_line)
                last_line = clan_line

        self.num_blocks = current_conv_block
        return line_map

    def block_map(self):
        return True

    def write_entries_to_csv(self, path):
        with open(path, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["file", "line", "timestamp"])


    def write_to_cha(self, path):
        with open(path, "wb") as output:
            for line in self.line_map:
                output.write(line.line)

