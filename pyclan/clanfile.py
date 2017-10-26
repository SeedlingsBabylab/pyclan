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
    get_with_time = filters.get_with_time
    replace_with_keyword = filters.replace_with_keyword
    replace_comments = filters.replace_comment
    shift_timestamps = filters.shift_timestamps
    clear_pho_comments = filters.clear_pho
    delete_pho_comments = filters.delete_pho
    flatten = filters.flatten

    end_tag = "@End"

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.num_full_blocks = 0
        self.full_block_range = False
        self.block_index = [] # list of all the full block indices in this file
        self.line_map = self.parse_file()
        self.total_time = sum(line.total_time for line in self.line_map if line.is_tier_line)
        self.flat = False
        self.annotated = False

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
                # print line
                newline_str = "\r\n" if line.endswith("\r\n") else "\n"
                # if "36815810_36816240" in line:
                #     print
                clan_line = elements.ClanLine(index, line)
                if line.startswith("*"):
                    seen_tier = True
                if last_line:
                    clan_line.onset = last_line.onset
                    clan_line.offset = last_line.offset
                else:
                    clan_line.onset = 0
                    clan_line.offset = 0
                # if clan_line.onset is None and index > 20:
                #     print

                if conv_block_started:
                    clan_line.conv_block_num = current_conv_block
                    clan_line.within_conv_block = True
                else:
                    clan_line.conv_block_num = 0

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
                                    clan_line.onset = last_line.onset
                                    clan_line.offset = last_line.offset
                                else:
                                    clan_line.onset = 0
                                    clan_line.offset = 0
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
                elif line.startswith("@"):
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
                                    clan_line.onset = last_line.onset
                                    clan_line.offset = last_line.offset
                                else:
                                    clan_line.onset = 0
                                    clan_line.offset = 0
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

                    # clan_line.is_header = True
                    if "@End" in line:
                        clan_line.is_end_header = True

                    line_map.append(clan_line)
                    last_line = clan_line
                    continue

                if line.startswith("\t"):
                    if last_line.is_user_comment or last_line.is_tier_line or last_line.is_other_comment:
                        if not last_line.multi_line_parent:
                            last_line.is_multi_parent = True
                        clan_line.multi_line_parent = last_line
                        if last_line.is_tier_line:
                            clan_line.is_tier_line = True
                            clan_line.tier = clan_line.multi_line_parent.tier
                            clan_line.content = line.split("\t")[1].replace(timestamp+newline_str, "")
                    else:
                        clan_line.multi_line_parent = last_line.multi_line_parent
                        if clan_line.multi_line_parent.is_tier_line:
                            clan_line.is_tier_line = True
                            clan_line.tier = clan_line.multi_line_parent.tier


                if line.startswith("%"):
                    if line.startswith("%pho:"):
                        clan_line.tier = last_line.tier
                        if line == "%pho:\r\n" or line == "%pho:\n":
                            clan_line.content = ""
                        else:
                            clan_line.content = line.split("\t")[1].translate(None, '\r\n')

                    if line.startswith("%com:") or line.startswith("%xcom:"):
                        if line.count("|") > 3:
                            clan_line.clan_comment = True
                        else:
                            clan_line.is_user_comment = True
                        if last_line.tier:
                            clan_line.tier = last_line.tier

                    elif line.startswith("%xdb:"):
                        clan_line.xdb_line = True
                        xdb_regx_result = elements.xdb_regx.search(line)
                        if xdb_regx_result:
                            clan_line.xdb_average = xdb_regx_result.group(1)
                            clan_line.xdb_peak = xdb_regx_result.group(2)

                    else:
                        clan_line.is_other_comment = True

                interv_regx_result = elements.interval_regx.search(line)

                if interv_regx_result:
                    timestamp = interv_regx_result.group()
                    onset = int(timestamp.split("_")[0].replace("\x15", ""))
                    offset = int(timestamp.split("_")[1].replace("\x15", ""))
                    clan_line.onset = onset
                    clan_line.offset = offset
                    clan_line.total_time = offset - onset
                    clan_line._has_timestamp = True

                    # there's no timestamp on a tier line
                    # (it wraps around to the next line)
                    if last_line.is_tier_without_timestamp:
                        last_line.onset = onset
                        last_line.offset = offset
                        last_line.total_time = offset - onset

                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(timestamp+newline_str, "")
                        clan_line.is_tier_line = True
                    if line.startswith("\t"):
                        # clan_line.tier = line[1:4]
                        if last_line.tier:
                            clan_line.tier = last_line.tier
                        clan_line.content = line.split("\t")[1].replace(timestamp+newline_str, "")
                        clan_line.is_tier_line = True
                else:
                    if line.startswith("*"):
                        clan_line.tier = line[1:4]
                        clan_line.content = line.split("\t")[1].replace(newline_str, "")
                        clan_line.is_tier_line = True
                        clan_line.is_tier_without_timestamp = True

                clan_line.annotations = self._extract_annots(clan_line.tier, clan_line.onset, clan_line.offset, line)

                line_map.append(clan_line)
                last_line = clan_line

        self.num_blocks = current_conv_block
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
        """
        Pull out all the annotations and return them as a list
        of Annotation objects. Annotations should be in this form:

                word x_y_ZZZ

        :return: a list of Annotation objects
        """
        if self.flat and self.annotated:
            return self._flat_annotations()
        else:
            annots = []
            multiline = []
            for i, line in enumerate(self.line_map):
                if line.is_tier_line and not (line.is_multi_parent or line.multi_line_parent):
                    if multiline: # collect accumulated multiline
                        parsed_annots = self.__collect_multiline(multiline)
                        if parsed_annots:
                            annots.append(parsed_annots)
                    if line.annotations:
                        annots.append(line.annotations)
                elif (line.is_multi_parent or line.multi_line_parent) and line.is_tier_line:
                    multiline.append(line)
                else:
                    if multiline:
                        parsed_annots = self.__collect_multiline(multiline)
                        if parsed_annots:
                            annots.append(parsed_annots)

            return annots

    def _flat_annotations(self):
        result = []
        for line in self.line_map:
            if line.annotations:
                result += line.annotations
        return result

    def annotate(self):
        """
        Run a pass through the entire file, line by line, setting the
        line.annotations field for each ClanLine in self.line_map.

        Note: the file should be flat for this to return meaningful results.
                you can ensure this by calling self.flatten()
        :return:
        """
        for line in self.line_map:
            if line.is_tier_line:
                line.annotations = self._extract_annots(line.tier, line.onset,
                                                        line.offset, line.content,
                                                        line.index)
        self.annotated = True

    def assign_pho(self):
        """
        Assign a pho value to the CHI annotation that it belongs to.
        :return:
        """
        if not self.annotated:
            raise Exception("you need to call self.annotate() before being able to assign pho's to CHI annotations")

        phos = [x for x in self.line_map if x.line.startswith("%pho:")]
        chis = [x for x in self.annotations() if x.speaker == "CHI"]

        sorted_phos = sorted(list(set(phos)), key=lambda x: x.index)
        phos = []

        for pho in sorted_phos:
            results = pho.content.translate(None, '\r\n').split()
            phos += results

        if len(phos) != len(chis):
            raise Exception("\n\nchis vs phos count mismatch:\n\nchis ({}): {}\n\nphos ({}): {}".format(len(chis), chis, len(phos), phos))
        else:
            for idx, pho in enumerate(phos):
                chis[idx].pho_annot = pho

        print


    def _join_annot_cells(self, cells):
        chunked = {}
        for cell in cells:
            timestamp = "{}_{}".format(cell.onset, cell.offset)
            if timestamp not in chunked:
                chunked[timestamp] = cell.content.replace("\n", " ").replace("\t", " ")
            else:
                chunked[timestamp] += " " + cell.content.replace("\n", " ").replace("\t", " ")
        return chunked

    def _extract_annots(self, tier, onset, offset, line, index=0):
        annots = []
        codes = elements.code_regx.findall(line)
        if codes:
            for code in codes:
                word = code[0]
                utt_type = code[3]
                present = code[5]
                speaker = code[7]
                annot = elements.Annotation(tier, word, utt_type, present, speaker,
                                            onset, offset, index)
                annot.orig_string = ''.join(code)

                annots.append(annot)
        return annots

    def __collect_multiline(self, multiline):
        chunked_lines = self._join_annot_cells(multiline)
        results = []
        for timestamp, joined_line in chunked_lines.items():
            t = map(int, timestamp.split("_"))
            results += self._extract_annots(multiline[0].tier, t[0], t[1], joined_line)
        del multiline[:]
        return results


    def clear_annotations(self):
        for line in self.line_map:
            if line.annotations:
                for annot in line.annotations:
                    line.line = line.line.replace(annot.orig_string, "")
                    line.content = line.line.replace(annot.orig_string, "")

    def reindex(self):
        """
        Assign new indices to all the ClanLines in the line_map. This also assigns
        a new index to each annotation in every ClanLine.annotations
        """
        for idx, line in enumerate(self.line_map):
            line.index = idx
            if line.annotations:
                for x in line.annotations:
                    x.line_num = idx

    def get_header(self):
        return [line for line in self.line_map
                    if line.is_header]


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

    def new_file_from_time(self, path, onset, offset, rewrite_timestamps=True):

        with open(path, "wb") as output:
            header = self.get_header()
            lines = self.get_within_time(begin=onset, end=offset)
            if rewrite_timestamps:
                lines.shift_timestamps(dt = -onset)

            for line in header:
                if not line.is_end_header:
                    output.write(line.line)
            for line in lines.line_map:
                output.write(line.line)
            output.write(self.end_tag)

    def basic_level(self, out):
        annots = self.annotations()
        with open(out, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["tier", "word", "utterance_type", "object_present", "speaker", "timestamp", "basic_level"])
            for annot in annots:
                for a in annot:
                    writer.writerow([a.tier, a.word, a.utt_type, a.present, a.speaker, a.timestamp(), ""])

