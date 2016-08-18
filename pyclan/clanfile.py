import csv
import re
import os

from collections import OrderedDict

interval_regx = re.compile("\\x15\d+_\d+\\x15")
block_regx = re.compile("Conversation (\d+)")
xdb_regx = re.compile("average_dB=\"([-+]?[0-9]*\.?[0-9]+)\" peak_dB=\"([-+]?[0-9]*\.?[0-9]+)\"")

class ClanLine(object):
    def __init__(self, index, line):
        self.index = index
        self.line = line
        self.is_header = False
        self.is_block_delimiter = False
        self.time_onset = 0
        self.time_offset = 0
        self.block_num = 0
        self.within_conv_block = False
        self.clan_comment = False
        self.user_comment = False
        self.xdb_line = False
        self.tier = None
        self.content = None
        self.xdb_average = 0
        self.xdb_peak = 0

    def timestamp(self):
         return "{}_{}".format(self.time_onset, self.time_offset)


class ClanFile(object):

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.file_map = self.parse_file()


    def parse_file(self):
        file_map = OrderedDict()
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
                                file_map[index] = clan_line
                                continue
                        clan_line.is_block_delimiter = block_delimiter
                        if block_started:
                            clan_line.block_num = current_block
                            clan_line.within_conv_block = True
                        else:
                            clan_line.block_num = 0
                            #clan_line.within_conv_block = False
                        file_map[index] = clan_line
                        continue

                    clan_line.is_header = True
                    clan_line.time_onset = None
                    clan_line.time_offset = None
                    file_map[index] = clan_line
                    continue

                if line.startswith("%com:") or line.startswith("%xcom:"):
                    if line.count("|") > 3:
                        clan_line.clan_comment = True
                    else:
                        clan_line.user_comment = True
                    clan_line.content = line.split("\t")[1]

                if line.startswith("%xdb:"):
                    clan_line.xdb_line = True
                    xdb_regx_result = xdb_regx.search(line)
                    if xdb_regx_result:
                        clan_line.xdb_average = xdb_regx_result.group(1)
                        clan_line.xdb_peak = xdb_regx_result.group(2)


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
                file_map[index] = clan_line

        return file_map

    def block_map(self):
        return True

    def write_entries_to_csv(self, path):
        with open(path, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["file", "line", "timestamp"])


    def write_to_cha(self, path):
        with open(path, "wb") as output:
            for _, line in self.file_map.iteritems():
                output.write(line.line)

