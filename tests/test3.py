import pyclan


clan_file = pyclan.ClanFile("../sample_data/44_17_coderSD_final.cha")

clan_file.replace_comments(["multi-word", "MWU", "mwu"], "this is a test")


clan_file.write_to_cha("44_17_new.cha")

# print clan_file.total_time