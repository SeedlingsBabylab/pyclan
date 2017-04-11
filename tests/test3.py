import pyclan as pc


clan_file = pc.ClanFile("../sample_data/44_17_coderSD_final.cha")

results = clan_file.get_with_speaker("CHI")


for x in results:
    line = pc.ClanLine(index=x.index+1, line="%pho:\t\n")
    clan_file.insert_line(line, x.index+1)

print

clan_file.write_to_cha("44_17_with_pho.cha")

# clan_file.replace_comments(["multi-word", "MWU", "mwu"], "this is a test")


# clan_file.write_to_cha("44_17_new.cha")

# print clan_file.total_time