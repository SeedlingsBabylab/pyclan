# pyclan

This is a Python library for working with CHAT (.cha) files that are used by the CLAN audio annotation program.

More info about CLAN [here](http://childes.psy.cmu.edu/clan/)



## usage examples:

```python

import pyclan


# First construct a ClanFile object by giving it a path
# to a .cha file. It will parse the file upon construction.
# After that, you're ready to use the library.

clan_file = ClanFile("/path/to/cha/file.cha")



# Example methods on ClanFile object:


# pull out all comments entered by the user
# It'll leave out machine generated comments
all_user_comments = clan_file.get_user_comments()

# get a single specific conversation block by index
block_33 = clan_file.get_block(33)

# get a group of blocks by specific index
blocks_5_19_12_and_45 = clan_file.get_blocks(select=[5, 19, 12, 45])

# get a range of blocks
blocks_7_through_33 = clan_file.get_blocks(begin=7, end=33)

# get all lines with specified tier.
# (function takes variable number of arguments)
all_FAN_and_MAN_tiers = clan_file.get_tiers("FAN", "MAN")

# get all lines within a time range (in milliseconds)
between_123456_and_1234567 = clan_file.get_within_time(begin=123456, end=1234567)

greater_than_123456 = clan_file.get_within_time(begin=123456)

less_than_123456 = clan_file.get_within_time(end=123456)




# There are some helpful functions for editing the CLAN file.

# You can find all the lines which contain a given keyword:
lines_with_keywords = clan_file.get_with_keyword("apple")

# You can then replace all those lines with a new keyword in
# its place. So in this example, all instances of "apple" will
# be replaced with "blueberry":
clan_file.replace_with_keyword(lines_with_keywords, "apple", "blueberry")

# Note that the get_with_keyword() method returns a
# dictionary of line numbers. You can filter these results
# before passing that dictionary to the replace_with_keyword()
# method. replace_with_keyword() will only replace lines that
# are in that dictionary.




```
