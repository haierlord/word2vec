import re, nltk, collections
import numpy as np

emoticons = {}
for line in open('../../data/emoticon'):
	line = line.strip().split('\t')
	emoticons[line[0]] = int(line[1])


negation= {}
for line in open('../../data/negation'):
	negation[line.strip()] = 1

slangs = {}
for line in open("../../data/slangs"):
	line = line.strip().split("  -   ")
	slangs[line[0]] = line[1]

class info():
	def __init__(self, parsedir):
		self.info = self.process_data(parsedir)
	
	def process_data(self, parsedir):
		info = {}
		dataparse = open(parsedir).read().strip().split("\n\n")
		for i in range(len(dataparse)):
			line = dataparse[i]
			if i % 2 == 0:
				tid = line.split('\t')[1]
				continue
			line = line.strip().split('\n')
			info[tid] = {}
			for term in line:
				term = term.strip().split('\t')
				info[tid][term[0]] = {}
				seq = info[tid][term[0]]
				seq['mark'] = term[0]
				seq['word'] = term[1]
				seq['pos'] = term[3]
				seq['cluster'] = term[-2]
			info[tid]['0'] = {}
		return info
	
	def shift_negation(self):
		count = 0
		for tid in self.info:
			words = []
			for i in range(len(self.info[tid]) - 1):
				words.append(self.info[tid][str(i + 1)])
			index_neg = len(self.info[tid])
			index = 0
			while (index != len(self.info[tid]) - 1):
				if self.info[tid][str(index + 1)]['word'] in negation:
					index_neg = index
					break
				index += 1
			if index_neg == len(self.info[tid]):
				continue
			index = index_neg + 1
			index_punc = len(self.info[tid]) - 1
			while (index != len(self.info[tid]) - 1):
				if self.info[tid][str(index + 1)]['pos'] == ',':
					index_punc = index + 1
					break
				index += 1

			for i in range(index_neg + 1,index_punc):
				self.info[tid][str(i + 1)]['word'] += "_NEG"



	def word_ngram(self, n, threshold):
		dic = collections.defaultdict(int)
		for tid in self.info:
			gram = []
			for i in range(len(self.info[tid]) - 1):
				gram.append(self.info[tid][str(i + 1)]['word'].lower())
			ngram = nltk.ngrams(gram, n)
			ngram = nltk.FreqDist(ngram)
			self.info[tid]['0']['w_' + str(n)] = ngram
			self.info[tid]['0']["text"] = gram
			for term in ngram:
				dic[term] += 1
		return [t for t in dic if dic[t] >= threshold]
	

	def char_ngram(self, n, threshold):
		dic = collections.defaultdict(int)
		for tid in self.info:
			gram = []
			for i in range(len(self.info[tid]) - 1):
				for j in range(len(self.info[tid][str(i + 1)]["word"]) - n):
					gram.append(self.info[tid][str(i + 1)]["word"][j: j + n])
			self.info[tid]['0']['c_' + str(n)] = nltk.FreqDist(gram)
			for term in gram:
				dic[term] += 1
		return [t for t in dic if dic[t] >= threshold]

	def POS(self):
		dic = collections.defaultdict(int)
		for tid in self.info:
			pos = []
			for i in range(len(self.info[tid]) - 1):
				pos.append(self.info[tid][str(i + 1)]['pos'])
				dic[self.info[tid][str(i + 1)]['pos']] += 1
			self.info[tid]['0']['pos'] = nltk.FreqDist(pos)
		return dic.keys()
	
	def Emoticon(self):
		dic = collections.defaultdict(int)
		for tid in self.info:
			pol = []
			for i in range(len(self.info[tid]) - 1):
				if self.info[tid][str(i + 1)]['pos'] == 'E':
					word = self.info[tid][str(i + 1)]["word"]
					if self.info[tid][str(i + 1)]["word"].endswith("_NEG"):
						word = word[:-4]
					dic[word] += 1
					pol.append(emoticons[word])
			self.info[tid]['0']['emoticon'] = nltk.FreqDist(pol)
		return dic.keys()


	def Cluster(self):
		dic = collections.defaultdict(int)
		for tid in self.info:
			cluster = []
			for i in range(len(self.info[tid]) - 1):
				dic[self.info[tid][str(i + 1)]['cluster']] += 1
				cluster.append(self.info[tid][str(i + 1)]['cluster'])
			self.info[tid]['0']['cluster'] = nltk.FreqDist(cluster)
		return dic.keys()
	

#info[tid][count]
def word_ngram(n, info, ngram):
	feature = []
	for i in range(len(ngram)):
		feature.append(1 if info['0']['w_' + str(n)][ngram[i]] > 0 else 0)
	return feature

def emoticon(info, ngram):
	feature = []
	for i in [1, -1]:
		feature.append(info["0"]["emoticon"][i])
	return feature

def char_ngram(n, info, ngram):
	feature = []
	for i in range(len(ngram)):
		feature.append(1 if info['0']['c_' + str(n)][ngram[i]] > 0 else 0)
	return feature

def POS(info, pos):
	feature = []
	for i in range(len(pos)):
		feature.append(info['0']['pos'][pos[i]])
	return feature

def Cluster(info, cluster):
	feature = []
	for i in range(len(cluster)):
		feature.append(1 if info['0']['cluster'][cluster[i]] else 0)
	return feature

def Jud_elongated(str):
	match = re.search(r"([A_Za-z])\1{2,}", str)
	try:
		return len(match.groups()) / len(match.groups())
	except:
		return 0  ## 0, 1

def elongated(info):
	feature = []
	count = 0
	for i in range(len(info) - 1):
		count += Jud_elongated(info[str(i + 1)]["word"].lower())
	return [count]

def Jud_allcaps(str):
	return str.isupper() # False, True

def allcaps(info):
	count = 0
	for i in range(len(info) - 1):
		if Jud_allcaps(info[str(i + 1)]["word"]):
			count += 1
	return [count]

def Jud_isExclam(str):
	return 1 if '!' in str else 0

def isExclam(info):
	count = 0
	words = ""
	for i in range(len(info) - 1):
		words += info[str(i + 1)]["word"]
	if words.endswith("!"):
		return [words.count("!"), 1]
	else:
		return [words.count("!"), 0]

def Jud_isQues(str):
	return 1 if "?" in str else 0

def isQues(info):
	count = 0
	words = ""
	for i in range(len(info) - 1):
		words += info[str(i + 1)]["word"]
	if words.endswith("?"):
		return [words.count("?"), 1]
	else:
		return [words.count("?"), 0]

def numPunc(info):
	words = ""
	for i in range(len(info) - 1):
		words += info[str(i + 1)]["word"]
	match = re.search("[!?]{2,}", words)
	try:
		return [len(match.group())]
	except:
		return [0]

	
def Lexicon(Ldir): # word \t pos \t neg
	f = open(Ldir)
	lexi = collections.defaultdict(int)
	for term in f:
		term = term.strip().split("\t")
		try:
			lexi[term[0]] = [float(term[1]), float(term[2])]
		except:
			lexi[term[0]] = [float(term[1]), 0.0]
	return lexi

def Lexicon_2(Ldir): # word \t score
	f = open(Ldir)
	lexi = collections.defaultdict(int)
	for term in f:
		term = term.strip().split('\t')
		lexi[term[0]] = [float(term[1]), 0.0]
	return lexi

def Senti_Man(info, lexi):
	neg = 0
	pos = 0
	for word in info['0']['w_1']:
		neg_falg = 1
		word = word[0].lower().strip("_neg")
		pos += 1 if lexi[word][0] > 0 else 0
		neg += 1 if lexi[word][1] > 0 else 0
	return [neg, pos]


def Senti_PMI(info, lexi, flag):
	neg = []
	pos = []
	for word in info['0'][flag]:
		neg_flag = 1
		if flag == 'w_1':
			word = word[0].lower()
			if word.endswith('_neg'):
				neg_flag = -1
				word = word[:-4]
		elif flag == 'w_2':
			word = word[0].lower() + ' ' + word[1].lower()
			if word[0].endswith('_NEG') or word[2].endswith('_NEG'):
				neg_flag = -1
				word = word[0].lower()[:-4] + ' ' + word[1].lower()[-4]
		try:
			if neg_flag == 1:
				pos.append(lexi[word][0])
				neg.append(lexi[word][1])
			else:
				pos.append(lexi[word][1])
				neg.append(lexi[word][0])
		except:
			continue
	feature = []
	# score > 0
	feature.append(len([i for i in pos if i > 0] + [i for i in neg if i < 0]))
	# score < 0
	feature.append(len([i for i in pos if i < 0]) + len([i for i in neg if i > 0]))
	# sum(score)
	feature.append(sum(pos + [-i for i in neg]))
	# max(score)
	feature.append(max(pos + [-i for i in neg] + [0]))
	# min(score)
	feature.append(min(pos + [-i for i in neg] + [0]))
	# last pos token score
	neg_flag = 1
	if flag == 'w_1':
		word = info[str(len(info) - 1)]['word'].lower()
		if word.endswith('_neg'):
			neg_flag = -1
			word = word[:-4]
	elif flag == 'w_2':
		word1 = info[str(len(info) - 1)]['word'].lower()
		word2 = info[str(len(info) - 2)]['word'].lower()
		if word1.endswith("_neg") or word2.endswith("_neg"):
			neg_flag = -1
			word1 = word1[:-4]; word2 = word2[:-4]
		word = word1 + ' ' + word2
	try:
		if neg_flag == 1:
			feature.append(lexi[word][0])
		else:
			feature.append(lexi[word][1])
	except:
		feature.append(0)
	# last neg token score
	try:
		if neg_flag == 1:
			feature.append(lexi[word][1])
		else:
			feature.append(lexi[word][0])
	except:
		feature.append(0)
	return feature


if __name__ ==  "__main__":
	dataparse = "../../data/SemEval2013Twitter/test1"
	data = info(dataparse)
#	data.shift_negation()
	unigram = data.word_ngram(1, 10)
	bigram = data.word_ngram(2, 9)
	trigram = data.word_ngram(3, 5)
	fourgram = data.word_ngram(4, 3)
#	trichar = data.char_ngram(3, 20)
#	fourchar = data.char_ngram(4, 20)
#	fivechar = data.char_ngram(5, 20)
#	pos = data.POS()
#	emoticon = data.Emoticon()
#	cluster = data.Cluster()
#	Lexiname = ["../../../dataset/Senti_Lexi/Bing Liu/BL.Lexi",
#			"../../../dataset/Senti_Lexi/MPQA/MPQA.lexi", 
#			"../../../dataset/Senti_Lexi/NRCEmotion/NRCEmoti.lexi",
#			"../../../dataset/Senti_Lexi/NRC140/Nunigram.lexi",
#			"../../../dataset/Senti_Lexi/NRCHashtag/Hunigram.lexi",
#			"../../../dataset/Senti_Lexi/NRC140/Nbigram.lexi",
#			"../../../dataset/Senti_Lexi/NRCHashtag/Hunigram.lexi"]
#	lexicon = []
#	for name in Lexiname:
#		lexicon.append(Lexicon(name))
	features = {}
	fout = open("feature_wordNgram.lower()", "w")
	for tid in data.info:
		feature = []
		feature += word_ngram(1, data.info[tid], unigram)
		feature += word_ngram(2, data.info[tid], bigram)
		feature += word_ngram(3, data.info[tid], trigram)
		feature += word_ngram(4, data.info[tid], trigram)

#		feature += char_ngram(3, data.info[tid], trichar)
#		feature += char_ngram(4, data.info[tid], fourchar)
#		feature += char_ngram(5, data.info[tid], fivechar)
#		feature += POS(data.info[tid], pos)
#		feature += Cluster(data.info[tid], cluster)
#		feature += isExclam(data.info[tid])
#		feature += isQues(data.info[tid])
#		feature += numPunc(data.info[tid])
#		feature += allcaps(data.info[tid])
#		feature += elongated(data.info[tid])
#		for i in range(len(lexicon)):
#			flag = 'w_1'
#			if i >= 5:
#				flag = 'w_2'
#			feature += extra_Senti(data.info[tid], lexicon[i], flag)
#		features[tid] = feature
		fout.write(tid + '\t' + ' '.join([str(i) for i in feature]) + '\n')


#parsedir = sys.argv[1]
#data = info(parsedir)

