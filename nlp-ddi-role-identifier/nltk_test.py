"""
Jeremy Jao
08.13.2014

This is supposed to be the NLP project with Pratibha and Yifan

The main goal is to use NLTK and return which word (drug only...) is the
precipitant and which is the object in a DDI sentence from the FDA.
"""

import nltk
import csv
import sys
from nltk.stem.porter import PorterStemmer
import pprint
#from nltk.tag.stanford import POSTagger
#from nltk.corpus import stopwords

stemmer = PorterStemmer()
INPUT = '/media/Backup/NLP-DDI-Sets/DDI-Sets-nonexpert1-csv-07212014.csv'
verbset = set([
		
		stemmer.stem('inhibit'), 
		stemmer.stem('increase'), 
		stemmer.stem('decrease'),
		stemmer.stem('effect'),
		stemmer.stem('affect'),
		stemmer.stem('induce'),
		stemmer.stem('reduce'),
		stemmer.stem('double'),
		stemmer.stem('occur'),
		stemmer.stem('triple')
		
			 ])
seenStcs = {}

def splitCol(string, delim, index):
	"""
	Simply splits columns from a string and returns the specific column
	
	args:
	string -- specific string to be split
	delim -- the delimiter to split the row
	index -- which column to return after the split
	"""
	return string.split(delim)[index]


def getVars(row):
	"""
	takes a pre-splitted row from the csv input and returns these data 
	about each row in this order as multiple variable returns:
		
		sentence, 
		modality, 
		statementType, 
		drugOne, 
		drugOneType, 
		drugOneRole, 
		drugTwo, 
		drugTwoType, 
		drugTwoRole
	
	args:
	row -- list of info stated from above
	"""
	sentence = row[1]
	modality = splitCol(row[2], ':', 1).lower()
	statementType = splitCol(row[3], ':', 1).lower()

	drugOne = row[4]
	drugOneType = splitCol(row[5],'/', 5).lower()
	drugOneRole = splitCol(row[6], ':', 1).lower()
	
	drugTwo = row[7]
	drugTwoType = splitCol(row[8], '/', 5).lower()
	drugTwoRole = splitCol(row[9], ':', 1).lower()
	
	return sentence, modality, statementType, drugOne, drugOneType, drugOneRole, drugTwo, drugTwoType, drugTwoRole
	
	
def workWithCol(row, ql, qn):
	sentence, modality, statementType, drugOne, drugOneType, drugOneRole, drugTwo, drugTwoType, drugTwoRole = getVars(row)

	if statementType == 'qualitative':
		addStc(ql, sentence, modality, statementType, drugOne, drugOneType, drugOneRole, drugTwo, drugTwoType, drugTwoRole)
	elif statementType == 'quantitative':
		addStc(qn, sentence, modality, statementType, drugOne, drugOneType, drugOneRole, drugTwo, drugTwoType, drugTwoRole)
		

def addStc(corpus, sentence, modality, statementType, drugOne, drugOneType, drugOneRole, drugTwo, drugTwoType, drugTwoRole):
	if sentence not in seenStcs:
		corpus.append(
			{
			
			'sentence': sentence,
			'modality': modality,
			'statement type': statementType,
			'drug 1': [{drugOne: {'type': drugOneType, 'role': drugOneRole}}],
			'drug 2': [{drugTwo: {'type': drugTwoType, 'role': drugTwoRole}}],
			'verbs': {},
			'drugs': {}
			
			}
		)
		tempIndex = len(corpus)-1
		seenStcs[sentence] = (corpus[tempIndex], tempIndex)
	else:
		tempIndex = seenStcs[sentence][1]
		corpus[tempIndex]['drug 1'].append({drugOne: {'type': drugOneType, 'role': drugOneRole}})
		corpus[tempIndex]['drug 2'].append({drugTwo: {'type':drugTwoType, 'role': drugTwoRole}})
	
def itRows(csvinp):
	ql = []
	qn = []
	qlindex = 0
	qnindex = 0
	for row in csvinp:
		workWithCol(row, ql, qn)
	return ql, qn
	
def workWithSentenceList(ql, qn):
	drugList = process_drugList()
	ie_process(ql, drugList)
	ie_process(qn, drugList)
	#pprint.pprint(ql[0])
	#pprint.pprint(ql[11])
	#pprint.pprint(ql[2])
	#pprint.pprint(ql[3])
	
	
	
	
def process_drugList():
	with open("drug-rxcui-type.txt", 'r') as fil:
		drugList = {}
		for line in fil:
			drugs = line.strip("\n").split(',')
			if drugs[2] == 'NAN':
				continue
			drugList[drugs[0]] = drugs[2]
		return drugList
	return None
	
def tokStc(stc):
	return nltk.word_tokenize(stc)
	
def ie_process(corpus, drugList):
	stopwords = nltk.corpus.stopwords.words('english')
	stc2 = []
	for data in corpus:
		processOne(data, drugList, stopwords)
		stc2.append(data['new sentence'])

def processOne(data, drugList, stopwords):
	oneStc = []
	index = 0
	for w in tokStc(data['sentence']):
		try:
			word = w
			if word not in stopwords:
				if word.lower() not in drugList:
					word = stemmer.stem(word.lower())
					if word in verbset:
						if word in data['verbs']:
							data['verbs'][word] = [index]
						else:
							data['verbs'][word] = index
				else:
					if word not in data['drugs']:
						data['drugs'][word.lower()] = [index]
					else:
						data['drugs'][word.lower()].append(index)
				oneStc.append(word)
			index += 1
		except UnicodeDecodeError:
			print w
	data['new sentence'] = oneStc
	
	#def testStcs():
		#st = POSTagger()
		#for sentence in seenStcs:
			#st.tag(sentence.split())
			#sys.exit(0)
def main():
	
	with open(INPUT, 'r') as inp:
		csvinp = csv.reader(inp, dialect='excel')
		next(csvinp)

		qualitative, quantitative = itRows(csvinp)
		workWithSentenceList(qualitative, quantitative)
		#testStcs()


if __name__ == '__main__':
	main()
