import csv
import os
import pandas
import distance
import operator

# spell check given word, return if it matches up with word inside the frequency
# if no matches found, a list of suggesting word would be returned 
def spellcheck(word, freqN = 10000, suggestN = 3):

	wordlist = getList(freqN)

	word = word.lower().replace(" ", "")
	if word in wordlist:
		return True, 0
	else:
		return False, getMatch(word, wordlist, suggestN)

# get word frequency list from the ordered word csv, return a list of top n word
def getList(n):
	this_dir, this_filename = os.path.split(__file__)
	freqFile = os.path.join(this_dir, "word_freq.csv")
	wordlist = []
	with open(freqFile, 'rU') as readfile:
		reader = csv.reader(readfile)
		for row in reader:
			for word in row[0:n]:
				if word.startswith("%com:"):
					continue
				if "+" in word:
					wordlist.extend([s.lower().replace(" ", "") for s in word.split("+")])
				else:
					wordlist.append(word.lower().replace(" ", ""))

	return set(wordlist)

# return a list of word with the closest distance
def getMatch(word, wordlist, suggestN):
	minDis = float("inf")
	disMap = {}

	for item in wordlist:
		dis = distance.levenshtein(word, item)
		disMap[item] = dis

	sorted_list = sorted(disMap.items(), key = operator.itemgetter(1))
	sorted_list = [each[0] for each in sorted_list]


	return sorted_list[:suggestN]
