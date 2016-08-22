import sys

import pyclan
from pyclan.filters import *


if __name__ == "__main__":

    file_path = sys.argv[1]

    clan_file = pyclan.ClanFile(file_path)

    all_user_comments = clan_file.get_user_comments()

    block_33 = clan_file.get_conv_block(33)

    blocks_5_19_12_and_45 = clan_file.get_conv_blocks(select=[5, 19, 12, 45])

    block_18 = clan_file.get_conv_block(18) # block 18 has a Multi-line CHN tier.

    all_FAN_and_MAN_tiers = clan_file.get_tiers("FAN", "MAN")

    all_CHN_tiers = clan_file.get_tiers("CHN")

    between_123456_and_1234567 = clan_file.get_within_time(begin=123456, end=1234567)

    greater_than_123456 = clan_file.get_within_time(begin=123456)

    less_than_123456 = clan_file.get_within_time(end=123456)



    lines_with_keyword = clan_file.get_with_keyword("apple")

    clan_file.replace_with_keyword(lines_with_keyword, "apple", "blueberry")

    #clan_file.set_content_from_new_map(new_editted_line_map)

    clan_file.write_to_cha("31_14_new.cha")

    comments_in_block_group = blocks_5_19_12_and_45.get_user_comments()

    CHN_OLN_and_NOF_in_line_range = between_123456_and_1234567.get_tiers("CHN", "OLN", "NOF")

    print

