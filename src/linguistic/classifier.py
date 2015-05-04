#!/usr/bin/python
import random, pickle, os
import numpy as np
import time, sys
from collections import defaultdict
import sklearn
from sklearn import svm
from sklearn.metrics import accuracy_score
import nltk, re
from StringIO import StringIO
#from classifier import *
import logging
#from SemEval2013 import *

#logger.setLevel(logging.INFO)
#ch = logging.StreamHandler()
#ch.setLevel(logging.INFO)
#formatter = logging.Formatter("%s(asctime)s - %(message)s")
#ch.setFormatter(formatter)
#logger.addHandler(ch)
log_format = "%(asctime)s %(message)s"
logging.basicConfig(format = log_format, datefmt = '%H:%M:%S  ', level = logging.INFO)


def F1(pred, gold):
	label = [1, -1, 0]
	F = 0
	Fscore = []
	for l in label:
		if list(pred).count(l) == 0:
			p = 0
		else:
			p = sum([1 for i in range(len(gold)) if gold[i] == l and l == pred[i]]) / float(list(pred).count(l))
		if list(gold).count(l) == 0:
			r = 0
		else:
			r = sum([1 for i in range(len(gold)) if gold[i] == l and l == pred[i]]) / float(gold.count(l))
		if (p + r == 0):
			Fscore.append(0)
			continue
		Fscore.append(2 * p * r / (p + r))
	return Fscore 


def eval_classifier(X_train, Y_train, X_test, Y_test, clf):
	clf.fit(X_train, Y_train)
	Y_pred = clf.predict(X_test)
#	print "Y_pred: 1:%d, -1:%d"%(list(Y_pred).count(1), list(Y_pred).count(-1))
	Fs = F1(Y_pred, Y_test)
	return	((Fs[0] + Fs[1]) / 2, Fs, Y_pred)

def classify(data, cv, kernel):
	classifiers = []
	if kernel == "rbf":
		#for i in [10]:
		for i in [0.25 ,0.5, 1, 2, 4, 8, 16]:
			classifiers.append((sklearn.svm.SVC(C = i, kernel  = "rbf"), "rbf", i))
	elif kernel == "linear":
		for i in [0.005, 0.01,0.0625, 0.125, 0.25, 0.5, 1, 2, 4]:
		#for i in [1, 2, 5]:
			classifiers.append((sklearn.svm.SVC(C = i, kernel  = "linear"), "linear", i))

	if cv == 0:
		X = [[], [], []]; Y = [[], [], []]
		for term in data:
			if term['type'] == 'train':
				flag = 0
			elif term['type'] == 'dev':
				flag = 1
			else:
				flag = 2
			X[flag].append(term['vector'])
			Y[flag].append(term['polarity'])
		'''
		print "Y[0] 1:%d 0:%d"%(Y[0].count(1), Y[0].count(-1))
		print "Y[1] 1:%d 0:%d"%(Y[1].count(1), Y[1].count(-1))
		print "Y[2] 1:%d 0:%d"%(Y[2].count(1), Y[2].count(-1))
		'''
		X = np.asarray(X)
		Y = np.asarray(Y)
		ans = []
		for clf, typ, c in classifiers:
			res = eval_classifier(X[0], Y[0], X[1], Y[1], clf)
			res1 = eval_classifier(X[0], Y[0], X[2], Y[2], clf)
			ans.append((res[0], clf))
			logging.info("%s, %s, %f, %f"%(typ, str(c), res[0], res1[0]))
			#try:
			#	if ans[-1][0] < ans[-2][0]:
			#		break
			#except:
			#	continue
		ans = sorted(ans, key = lambda d: d[0], reverse = True)
		result = eval_classifier(X[0], Y[0], X[2], Y[2], ans[0][1])
		logging.info("-"*20)
		logging.info("\t\tPositive\tNegative\tNeural")
		logging.info("Fscore\t%f\t%f\t%f"%(result[1][0], result[1][1], result[1][2]))
		logging.info("-"*30)
		logging.info("Predict\Gold\tPositive\tNegative\tNeural")
		logging.info("Positive\t%d\t\t%d\t\t%d"%(sum([1 for i in range(len(Y[2])) if Y[2][i] == 1 and result[-1][i] == 1]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == -1 and result[-1][i] == 1]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == 0 and result[-1][i] == 1])))
		logging.info("Negative\t%d\t\t%d\t\t%d"%(sum([1 for i in range(len(Y[2])) if Y[2][i] == 1 and result[-1][i] == -1]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == -1 and result[-1][i] == -1]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == 0 and result[-1][i] == -1])))
		logging.info("Neutral\t%d\t\t%d\t\t%d"%(sum([1 for i in range(len(Y[2])) if Y[2][i] == 1 and result[-1][i] == 0]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == -1 and result[-1][i] == 0]),
										 sum([1 for i in range(len(Y[2])) if Y[2][i] == 0 and result[-1][i] == 0])))
		logging.info("-"*20)
		return (result, Y[2], ans[0][1])
	
