import sys

import pyclan


if __name__ == "__main__":

    file_path = sys.argv[1]

    clan_file = pyclan.ClanFile(file_path)

    print