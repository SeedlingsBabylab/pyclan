import sys

import pyclan


if __name__ == "__main__":

    file_path = sys.argv[1]

    clan_file = pyclan.ClanFile(file_path)

    all_user_comments = clan_file.get_user_comments()

    #blocks_3_to_7 = clan_file.blocks()

    block_33 = clan_file.get_block(33)

    blocks_5_19_12_and_45 = clan_file.get_blocks(select=[5, 19, 12, 45])

    print

