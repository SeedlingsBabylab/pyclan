from pyclan import *

import sys


if __name__ == "__main__":
    file = sys.argv[1]

    clan_file = ClanFile(file)

    # clan_file.new_file_from_blocks("blocks_out.cha", [7, 8, 12, 33])
    #
    # clan_file.new_file_from_blocks("blocks_out_4-12.cha", begin=4, end=12)
    #
    # blocks_7_12_56_and_158 = clan_file.get_conv_blocks(select=[7, 12, 56, 158])
    #
    # blocks_7_12_56_and_158.total_time

    block1 = clan_file.get_conv_block(1)

    print