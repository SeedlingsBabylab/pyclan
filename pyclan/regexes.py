""" File to hold regexes used throughout the program """
import re

interval_regx = re.compile("\\x15\d+_\d+\\x15")
block_regx = re.compile("Conversation (\d+)")
pause_regx = re.compile("Pause (\d+)")
xdb_regx = re.compile(
    "average_dB=\"([-+]?[0-9]*\.?[0-9]+)\" peak_dB=\"([-+]?[0-9]*\.?[0-9]+)\"")
code_regx = re.compile(

    '([a-zA-Z][a-z+]*)( +)(&=)([A-Za-z]{1})(_)([A-Za-z]{1})(_)([A-Z]{1}[A-Z0-9]{2})(_)?(0x[a-z0-9]{6})?', re.IGNORECASE | re.DOTALL)
code_regx_id = re.compile(
    '([a-zA-Z][a-z+]*)( +)(&=)([A-Za-z]{1})(_)([A-Za-z]{1})(_)([A-Z]{1}[A-Z0-9]{2})(_)(0x[a-z0-9]{6})', re.IGNORECASE | re.DOTALL)
#code_regx = re.compile(
#    '([a-zA-Z+]+)( +)(&=)(.)(_)(.)(_)([a-zA-Z0-9]{3})', re.IGNORECASE | re.DOTALL)
# annot_regx = re.compile('(&=)(.)(_)(.)(_)([a-zA-Z0-9]{3})')
