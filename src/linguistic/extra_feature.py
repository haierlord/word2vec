import nltk, sys, collections
import numpy as np


class info():
	def __init__(parsedir):
		self.info = process_data(parsedir)
	
	def process_data(self, parsedir):
		dataparse = open(parsedir).read().strip().split("\n\n")
		for i in range(len(dataparse)):
			if i % 2 == 0:
				tid = line.split('\t')[1]
				continue
			line = line.strip().split('\n')
			self.info[tid] = {}
			for term in line:
				term = term.strip().split('\t')
				self.info[tid][term[0]] = {}
				seq = self.info[tid][term[0]]
				seq['mark'] = term[0]
				seq['word'] = term[1]
				seq['pos'] = term[3]
				seq['cluster'] = term[-2]
		

	def word_ngram(self, n, threshold):
		dic = collections.defaultdict(int)
		for tid in self.info:
			gram = []
			for i in range(len(self.info[tid])):
				gram.append(self.info[tid][str(i + 1)]['word'])
			ngram = nltk.ngrams(gram, n)
			for term in ngram:
				dic[term] += 1
		return [t for t in dic if dic[t] >= threshold]

	def POS(self):
		dic = collections.defaultdict(int)
		for tid in self.info:
			for i in range(len(self.info[tid])):
				dic[self.info[tid][str(i + 1)]['pos']] += 1
		return dic.keys()


	def Cluster(self, n, threshold):
		dic = collections.defaultdict(int)
		for tid in self.info:
			for i in range(len(self.info[tid])):
				dic[self.info[tid][str(i + 1)]['cluster']] += 1
		return dic.keys()
	


#parsedir = sys.argv[1]
#data = info(parsedir)

