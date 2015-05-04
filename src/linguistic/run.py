#!/usr/bin/env python
# -*- coding: utf-8 -*-
# haierlord@gmail.com 2015-05-02 22:41:17


from classifier import *

if __name__ == "__main__":
	data_fe = open("feature_wordNgram.lower()")
	feature = {}
	for line in data_fe:
		line = line.strip().split('\t')
		feature[line[0]] = {"vector": [float(t) for t in line[1].split(' ')]}
	data = open("../../data/SemEval2013Twitter/SemEval2013_3class")
	for line in data:
		line = line.split(' ')
		feature[line[1]]['type'] = line[0].lower()
		if line[2] == "positive":
			pol = 1
		elif line[2] == "negative":
			pol = -1
		else:
			pol = 0
		feature[line[1]]['polarity'] = pol

	for kernel in ["linear", "rbf"]:
		ans = classify(feature.values(), 0, kernel)
