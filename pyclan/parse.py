from . import elements
from . import errors

def parse_file(self, line_list, breaks):
    line_map = []
    # with open(self.clan_path, "r") as input:
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
    try:
        for index, line in enumerate(line_list):
            # print line
            newline_str = "\r\n" if line.endswith("\r\n") else "\n"
            # if "36815810_36816240" in line:
            #     print
            clan_line = elements.ClanLine(index, line)
            clan_line.breaks = breaks[index]
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
                if last_line.is_user_comment or last_line.is_tier_line or last_line.is_other_comment or last_line.is_user_comment_child or last_line.is_pho:
                    if not last_line.multi_line_parent:
                        last_line.is_multi_parent = True
                    clan_line.multi_line_parent = last_line
                    if last_line.is_user_comment or last_line.is_user_comment_child:
                        clan_line.is_user_comment_child = True
                        clan_line.user_comment = elements.UserComment(line)
                        clan_line.user_comment.trace_root(last_line)
                    if last_line.is_tier_line:
                        clan_line.is_tier_line = True
                        clan_line.tier = clan_line.multi_line_parent.tier
                        clan_line.content = line.split("\t")[1].replace(timestamp+newline_str, "")
                    #temp solution to pho tab
                    if last_line.is_pho:
                        # print last_line, clan_line, last_line.tier
                        clan_line.is_pho = True
                        clan_line.tier = last_line.tier
                else:
                    clan_line.multi_line_parent = last_line.multi_line_parent
                    if clan_line.multi_line_parent.is_tier_line:
                        clan_line.is_tier_line = True
                        clan_line.tier = clan_line.multi_line_parent.tier

            #Issue with pho line block tier missing, need to be record?
            if line.startswith("%"):
                if line.startswith("%pho:"):
                    clan_line.is_pho = True
                    clan_line.tier = last_line.tier
                    if line == "%pho:\r\n" or line == "%pho:\n":
                        clan_line.content = ""
                        phoObj = elements.Pho("")
                        clan_line.phos.append(phoObj)
                    else:
                        clan_line.content = line.split("\t", 1)[1].rstrip()
                        phos = clan_line.content.split('\t')
                        for pho in phos:
                            phoObj = elements.Pho(pho)
                            clan_line.phos.append(phoObj)

                if line.startswith("%com:") or line.startswith("%xcom:"):
                    if line.count("|") > 3:
                        clan_line.clan_comment = True
                    else:
                        clan_line.is_user_comment = True
                        clan_line.user_comment = elements.UserComment(line)
                        clan_line.content = line.split("\t", 1)[1].replace(newline_str, "")
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

            interv_regx_result = elements.interval_regx.findall(line)

            if interv_regx_result:
                timestamp = interv_regx_result[-1]
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
                # if line.startswith("\t"):
                #     # clan_line.tier = line[1:4]
                #     if last_line.tier:
                #         clan_line.tier = last_line.tier
                #     # if clan_line.multi_line_parent and clan_line.multi_line_parent.is_tier_line:
                #     #     temp_line = clan_line.multi_line_parent
                #     #     temp_line.annotations = self._extract_annots(temp_line.tier, onset, offset, temp_line.line)
                #     #     while temp_line.multi_line_parent and temp_line.multi_line_parent.is_tier_line:
                #     #         tempn = temp_line.multi_line_parent
                #     #         tempn.annotations = self._extract_annots(tempn.tier, onset, offset, tempn.line)
                #     #         temp_line = tempn
                #     clan_line.content = line.split("\t")[1].replace(timestamp+newline_str, "")
                #     clan_line.is_tier_line = True
            else:
                if line.startswith("*"):
                    clan_line.tier = line[1:4]
                    clan_line.content = line.split("\t")[1].replace(newline_str, "")
                    clan_line.is_tier_line = True
                    clan_line.is_tier_without_timestamp = True

            clan_line.annotations = self._extract_annots(clan_line.tier, clan_line.onset, clan_line.offset, line)

            line_map.append(clan_line)
            ts = "{}_{}".format(clan_line.onset, clan_line.offset)

            if ts in self.ts_index:
                self.ts_index[ts].append(clan_line)
            else:
                self.ts_index[ts] = [clan_line]

            last_line = clan_line
    except Exception, e:
        print e
        print line
        raise errors.ParseError(index, last_line)

    self.num_blocks = current_conv_block
    return line_map
