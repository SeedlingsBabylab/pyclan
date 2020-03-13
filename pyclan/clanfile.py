import csv
import os
import re

from pyclan import filters
from pyclan import elements
from pyclan import errors
from pyclan import parse

class ClanFile(object):
    """A class to represent a given cha file"""

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
    reindex_timestamps = filters.reindex_ts
    parse_file = parse.parse_file

    end_tag = "@End"

    def __init__(self, path):
        self.clan_path = path
        self.filename = os.path.basename(self.clan_path)
        self.num_full_blocks = 0
        self.full_block_range = False
        self.block_index = [] # list of all the full block indices in this file
        self.ts_index = {}
        # try:
        # print("here")
        flattenedlines, breaks= filters._preparse_flatten(self.clan_path)
        # print("there")
        self.line_map = self.parse_file(flattenedlines, breaks)
        # print("and back")
        # except Exception as e:
            # print e
            # print "\n\nParsing Error:\n\nfile: {}\nline: {}\nonset:{}\n\n".format(self.filename, e.index, e.last_line.onset)
        self.total_time = sum(line.total_time for line in self.line_map if line.is_tier_line)
        self.flat = False
        self.annotated = False



    def insert_line(self, line, index):
        """Insert a ClanLine into the middle of a ClanFile at
        a given index.
        
        If index == 15, then the current ClanLine at 15 will
        be pushed to 16, and the new ClanLine will take its
        place.

        :param line: ClanLine object to insert into the ClanFile
        :param index: index to insert at

        """
        self.line_map.insert(index, line)
        for i, x in enumerate(self.line_map):
            x.index = i

    def annotations(self):
        """Pull out all the annotations and return them as a list
        of Annotation objects. Annotations should be in this form:
        
                word x_y_ZZZ
        
        :return: a list of Annotation objects


        """
        if self.annotated:
            return self._flat_annotations()
        else:
            self.annotate()
            return self._flat_annotations()


    def _flat_annotations(self):
        """ """
        result = []
        for line in self.line_map:
            if line.annotations:
                result += line.annotations
        return result

    def annotate(self):
        """Run a pass through the entire file, line by line, setting the
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
        """Assign a pho value to the CHI annotation that it belongs to.
        :return:


        """
        if not self.annotated:
            raise Exception("you need to call self.annotate() before being able to assign pho's to CHI annotations")

        phos = [x for x in self.line_map if x.line.startswith("%pho:")]
        chis = [x for x in self.annotations() if x.speaker == "CHI"]

        sorted_phos = sorted(list(set(phos)), key=lambda x: x.index)
        phos = []

        for pho in sorted_phos:
            results = re.split(r'[\t| ]', pho.content.translate(None, '\r\n'))
            phos += results

        if len(phos) != len(chis):
            raise Exception("\n\nchis vs phos count mismatch:\n\nchis ({}): {}\n\nphos ({}): {}".format(len(chis), chis, len(phos), phos))
        else:
            for idx, pho in enumerate(phos):
                chis[idx].pho_annot = pho

    def _join_annot_cells(self, cells):
        """

        :param cells: 

        """
        chunked = {}
        for cell in cells:
            timestamp = "{}_{}".format(cell.onset, cell.offset)
            if timestamp not in chunked:
                chunked[timestamp] = cell.content.replace("\n", " ").replace("\t", " ")
            else:
                chunked[timestamp] += " " + cell.content.replace("\n", " ").replace("\t", " ")
        return chunked

    def _extract_annots(self, tier, onset, offset, line, index=0):
        """

        :param tier: 
        :param onset: 
        :param offset: 
        :param line: 
        :param index:  (Default value = 0)

        """
        annots = []
        codes = elements.code_regx.findall(line)
        if codes:
            for code in codes:
                word = code[0]
                utt_type = code[3]
                present = code[5]
                speaker = code[7]
                annotation_id = code[9]
                if annotation_id:
                    annotation_id = annotation_id.lstrip('_')
                annot = elements.Annotation(tier, word, utt_type, present, speaker, annotation_id,
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
        """ """
        for line in self.line_map:
            if line.annotations:
                for annot in line.annotations:
                    line.line = line.line.replace(annot.orig_string, "")
                    line.content = line.line.replace(annot.orig_string, "")

    def reindex(self):
        """Assign new indices to all the ClanLines in the line_map. This also assigns
        a new index to each annotation in every ClanLine.annotations


        """
        for idx, line in enumerate(self.line_map):
            line.index = idx
            if line.annotations:
                for x in line.annotations:
                    x.line_num = idx

    def get_header(self):
        """ """
        return [line for line in self.line_map if line.is_header]

    def length(self):
        """Get the length of the CLAN file
        :return: number of lines in the file


        """
        return len(self.line_map)


    def write_to_cha(self, path):
        """

        :param path: 

        """
        with open(path, "wb") as output:
            for line in self.line_map:
                if len(line.breaks)>1:
                    for i in range(1, len(line.breaks)):
                        output.write(line.line[line.breaks[i-1]:line.breaks[i]].strip() + '\n\t')
                    output.write(line.line[line.breaks[-1]:])
                else:
                    output.write(line.line)

    def new_file_from_blocks(self, path, blocks=[], rewrite_timestamps=False,
                             begin=1, end=None):
        """This produces a new cha file with only the blocks specified

        :param path: path to the new output cha file
        :param blocks: list of indices of blocks (Default value = [])
        :param rewrite_timestamps: if True, then timestamps will be rewritten to
                                start from 0 and be contiguous with each other (Default value = False)
        :param begin:  (Default value = 1)
        :param end:  (Default value = None)

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
        """

        :param path: 
        :param onset: 
        :param offset: 
        :param rewrite_timestamps:  (Default value = True)

        """

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

    def phos(self):
        """ """
        phos = []
        for line in self.line_map:
            phos += line.phos
        return phos

    def create_pho_chi_linkage(self):
        """ """
        self.annotate()
        annots = self.annotations()
        if not annots:
            return
        else:
            annotations = []
            for annot in annots:
                if type(annot) is list:
                    annotations.extend(annot)
                elif type(annot) is elements.Annotation:
                    annotations.append(annot)
            match = {}
            for annot in annotations:
                match[annot.annotation_id] = annot
            phos = self.phos()
            for pho in phos:
                pho.annotation = match[pho.annotation_ref]
                match[pho.annotation_ref].pho = pho

    def basic_level(self, out):
        """

        :param out: 

        """
        annots = []
        for line in self.line_map:
            if line.is_tier_line and not line.in_skip_region:
                annots += self._extract_annots(line.tier, line.onset,
                                                        line.offset, line.content,
                                                        line.index)
        error = []
        for annot in annots:
            error.extend(filters.check_annotation(annot))
        if error:
            print "Error(s) in annotation:\n"
            for err in error:
                print err + "\n"
            return
        with open(out, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["tier", "word", "utterance_type", "object_present", "speaker", "timestamp", "annotation_id", "basic_level"])
            for a in annots:
                # for a in annot:
                writer.writerow([a.tier, a.word, a.utt_type, a.present, a.speaker, a.timestamp(), a.annotation_id, ""])
