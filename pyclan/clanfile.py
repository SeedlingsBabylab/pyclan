import csv
import os

from filter import *
from elements import *

class ClanFile(object):

    get_user_comments = user_comments
    get_block = block
    get_blocks = blocks

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.num_blocks = 0
        self.line_map = self.parse_file()

    def parse_file(self):
        line_map = []
        with open(self.clan_path, "rU") as input:
            current_block = 0

            block_started = False
            block_ended = False
            for index, line in enumerate(input):

                clan_line = ClanLine(index, line)

                if line.startswith("@") or index < 10:
                    block_delimiter = False
                    if line.startswith("@Bg") or line.startswith("@Eg"):
                        block_regx_result = block_regx.search(line)
                        if block_regx_result:
                            current_block = int(block_regx_result.group(1))
                            block_delimiter = True
                            if "@Bg" in line:
                                block_started = True
                                block_ended = False
                            if "@Eg" in line:
                                block_started = False
                                block_ended = True
                                clan_line.is_block_delimiter = True
                                clan_line.block_num = current_block
                                clan_line.within_conv_block = True
                                line_map.append(clan_line)
                                continue
                        clan_line.is_block_delimiter = block_delimiter
                        if block_started:
                            clan_line.block_num = current_block
                            clan_line.within_conv_block = True
                        else:
                            clan_line.block_num = 0
                            #clan_line.within_conv_block = False
                        line_map.append(clan_line)
                        continue

                    clan_line.is_header = True
                    clan_line.time_onset = None
                    clan_line.time_offset = None
                    line_map.append(clan_line)
                    continue

                if line.startswith("%com:") or line.startswith("%xcom:"):
                    if line.count("|") > 3:
                        clan_line.clan_comment = True
                    else:
                        clan_line.user_comment = True
                    clan_line.content = line.split("\t")[1]

                    if block_started:
                        clan_line.block_num = current_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.block_num = 0

                if line.startswith("%xdb:"):
                    clan_line.xdb_line = True
                    xdb_regx_result = xdb_regx.search(line)
                    if xdb_regx_result:
                        clan_line.xdb_average = xdb_regx_result.group(1)
                        clan_line.xdb_peak = xdb_regx_result.group(2)

                    if block_started:
                        clan_line.block_num = current_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.block_num = 0


                interv_regx_result = interval_regx.search(line)

                if interv_regx_result:
                    timestamp = interv_regx_result.group()
                    onset = int(timestamp.split("_")[0].replace("\x15", ""))
                    offset = int(timestamp.split("_")[1].replace("\x15", ""))
                    clan_line.time_onset = onset
                    clan_line.time_offset = offset
                    if block_started:
                        clan_line.block_num = current_block
                        clan_line.within_conv_block = True
                    else:
                        clan_line.block_num = 0
                        #clan_line.within_conv_block = False
                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(timestamp+"\n", "")
                line_map.append(clan_line)

        self.num_blocks = current_block
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

