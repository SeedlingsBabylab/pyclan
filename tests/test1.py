import sys

import pyclan


if __name__ == "__main__":

    file_path = sys.argv[1]

    clan_file = pyclan.ClanFile(file_path)

    all_user_comments = clan_file.get_user_comments()

    block_33 = clan_file.get_block(33)

    blocks_5_19_12_and_45 = clan_file.get_blocks(select=[5, 19, 12, 45])

    block_18 = clan_file.get_block(18) # block 18 has a Multi-line CHN tier.

    all_FAN_and_MAN_tiers = clan_file.get_tiers("FAN", "MAN")

    all_CHN_tiers = clan_file.get_tiers("CHN")

    print

