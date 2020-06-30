import sys
import csv

# Functions to check for video files
acceptable_utterance_types = ['s', 'n', 'd', 'r', 'q', 'i', 'o', 'u']
comment = "%com:"

# video ordinal column format checking
def check_ordinal_video(ordinal, total_lines = 0, ordinal_list = 0):
    digit_list = ['0']
    for y in ordinal:
        if y.isdigit():
            digit_list.append(y)
    string_digits = ''.join(digit_list)
    int_digits = int(string_digits)

    try:
        if ordinal_list:
            #Check for repeat values
            assert(not (ordinal in ordinal_list))
        #Check for non-digit characters
        assert(x.isdigit() for x in ordinal)
        if total_lines:
            #Check that ordinal value is from 1 to total_lines-1, inclusive
            assert(int_digits >= 0 and int_digits <= total_lines - 1)

    except AssertionError:
        return False

    return True

# video onset column format checking
def check_onset_video(onset):
    try:
        assert(x.isdigit() for x in onset)
    except AssertionError:
        return False

    return True

# video offset column format checking
def check_offset_video(offset):
    try:
        assert(x.isdigit() for x in offset)
    except AssertionError:
        return False

    return True

# video object column format checking
def check_object_video(obj):
    cap = 0
    try:
    	if not obj.startswith(comment):
            for char in obj:
                assert (char.isalpha() or char == "+" or char == "'")
                if char.isupper():
                    cap += 1
            assert (cap <= 1)
    except AssertionError:
        return False

    return True

# video utterance_type column format checking
def check_utterance_type_video(utterance_type, word = 0):
    try:
    	if word.startswith(comment):
    		assert (utterance_type == "NA")
    	else:
        	assert (utterance_type in acceptable_utterance_types)
    except AssertionError:
        return False

    return True

# video object_present column format checking
def check_object_present_video(obj_pres, word = 0):
    try:
    	if word.startswith(comment):
    		assert (obj_pres == "NA")
    	else:
        	assert(obj_pres == "y" or obj_pres == "n" or obj_pres == "o" or obj_pres == "u")
    except AssertionError:
        return False

    return True

# check if a speaker is valid
def isValid(speaker):
    if len(speaker) != 3:
        return False
    if speaker[0].isalpha() and speaker[0].isupper():
        if (speaker[1].isalpha() and speaker[1].isupper()) or speaker[1].isdigit():
            if (speaker[2].isalpha() and speaker[2].isupper()) or speaker[2].isdigit():
                return True
    return False

# video speaker column format checking
def check_speaker_video(speaker, word = 0):
    try:
        if word.startswith(comment):
            assert (speaker == "NA")
        else:
            assert(isValid(speaker))
    except AssertionError:
        return False

    return True

# video basic_level column format checking
def check_basic_level_video(basic_level, word = 0):
    cap = 0
    try:
    	if word.startswith(comment):
    	    assert (basic_level == "NA")
    	else:
            if "TIME" not in basic_level and "FIX ME" not in basic_level and "NA" not in basic_level:
                for char in basic_level:
                    assert (char.isalpha() or char == "+" or char == "'" or char == " ")
                    if char.isupper():
                        cap += 1
                assert(cap <= 1)
    except AssertionError:
        return False

    return True


#Functions to check for audio files

acceptable_tier = ['CHF', 'CHN', 'CXF', 'CXN', 'FAF', 'FAN', 'NOF',
                   'MAF', 'MAN', 'NON', 'OLF', 'OLN', 'SIL', 'TVF', 'TVN']

#FIXME if asterisk is to be kept
acceptable_tier = ['*'+tier for tier in acceptable_tier]

# audio tier column format checking
def check_tier_audio(tier):
    try:
        assert(tier in acceptable_tier)
    except AssertionError:
        return False

    return True

# audio word column format checking
def check_word_audio(word):
    cap = 0
    try:
        for char in word:
            assert (char.isalpha() or char == "+" or char == "'")
            if char.isupper():
                cap += 1
        assert(cap <= 1)
    except AssertionError:
        return False

    return True

# audio utterance_type column format checking
def check_utterance_type_audio(utterance_type):
    try:
        assert (utterance_type in acceptable_utterance_types)
    except AssertionError:
        return False

    return True

# audio object_present column format checking
def check_object_present_audio(obj_pres):
    try:
        assert(obj_pres == "y" or obj_pres == "n" or obj_pres == "u" or obj_pres == "o")
    except AssertionError:
        return False

    return True

# audio speaker column format checking
def check_speaker_audio(speaker):
    try:
        #currently no comment in audio file for word column, so no check on it
 #        if word.startswith(comment):
	#     assert (speaker == "NA")
	# else:
	    assert(isValid(speaker))
    except AssertionError:
        return False

    return True

# audio timestamp column format checking
def check_timestamp_audio(timestamp):
    underscore_index = timestamp.find("_")

    if underscore_index != -1:
        try:
            for x in range(len(timestamp)):
                if x != underscore_index:
                    assert(timestamp[x].isdigit())
        except AssertionError:
            return False
    else:
        try:
            assert(underscore_index != -1)
        except AssertionError:
            return False

    return True


# audio basic_level column format checking
def check_basic_level_audio(basic_level):
    cap = 0
    try:
        if "TIME" not in basic_level and "FIX ME" not in basic_level and "NA" not in basic_level:
            for char in basic_level:
                assert (char.isalpha() or char == "+" or char == "'" or char == " ")
                if char.isupper():
                    cap += 1
            assert(cap <= 1)
    except AssertionError:
        return False

    return True

# general onset offset checking
def check_onset_offset(onset, offset):
    try:
        assert(x.isdigit() for x in onset)
        assert(x.isdigit() for x in offset)
        onset = int(onset)
        offset = int(offset)
        assert(offset > onset)
    except (AssertionError, ValueError) as e:
        return False

    return True
