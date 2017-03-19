#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 15:06:40 2017

@author: nileshbhoyar
"""
import numpy as np
import pandas as pd
import nltk
import random
import sys
import itertools
from collections import defaultdict
import pickle

EN_WHITELIST = '0123456789abcdefghijklmnopqrstuvwxyz ' # space is included in whitelist
EN_BLACKLIST = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\''
MAX_REVIEWS = 1000000
FILENAME = '/Users/nileshbhoyar/Documents/W266Project/data/finefoods.txt'

limit = {
        'maxreview' : 100,
        'minreview' : 0,
        'maxsummary' : 30,
        'minsummary' : 3
        }
UNK = 'unk'
VOCAB_SIZE = 20000000
##
def __crawl_review(raw_data_file):
    
        """
        Crawl review
        :return: review [numpy array]
        """
        review_list = []
        print 'Crawling Reviews....'
        num_lines = 0
        with open(raw_data_file) as infile:
            for line in infile:
                if line.startswith('review/text'):
                    if num_lines >= MAX_REVIEWS:
                        break
                    num_lines += 1
                    _,review = line.split('/text: ')
                    review_list.append(review)
        return np.array(review_list)
    
    
def __crawl_summary(raw_data_file):
        """
        Crawl summary
        :return: summary [numpy array]
        """
        summary_list = []
        print 'Crawling Summary....'
        num_lines = 0
        with open(raw_data_file) as infile:
            for line in infile:
                if line.startswith('review/summary'):
                    if num_lines >= MAX_REVIEWS:
                        break
                    num_lines += 1
                    _,summary = line.split('/summary: ')
                    summary_list.append(summary)
        return np.array(summary_list)
    
#tokenize sentenses here both review + summary
def index_(tokenized_sentences, vocab_size):
    # get frequency distribution
        freq_dist = nltk.FreqDist(itertools.chain(*tokenized_sentences))
        # get vocabulary of 'vocab_size' most used words
        vocab = freq_dist.most_common(vocab_size)
        # index2word
        index2word = ['_'] + [UNK] + [ x[0] for x in vocab ]
    # word2index
        word2index = dict([(w,i) for i,w in enumerate(index2word)] )
        return index2word, word2index, freq_dist

def pad_seq(seq, lookup, maxlen):
       indices = []
       for word in seq:
           if word in lookup:
               indices.append(lookup[word])
           else:
               indices.append(lookup[UNK])
       return indices + [0]*(maxlen - len(seq))
#zero pad
def zero_pad(qtokenized, atokenized, w2idx):
    # num of rows
        data_len = len(qtokenized)

    # numpy arrays to store indices
        idx_review = np.zeros([data_len, limit['maxreview']], dtype=np.int32) 
        idx_summary = np.zeros([data_len, limit['maxsummary']], dtype=np.int32)

        for i in range(data_len):
            q_indices = pad_seq(qtokenized[i], w2idx, limit['maxreview'])
            a_indices = pad_seq(atokenized[i], w2idx, limit['maxsummary'])

        #print(len(idx_q[i]), len(q_indices))
        #print(len(idx_a[i]), len(a_indices))
            idx_review[i] = np.array(q_indices)
            idx_summary[i] = np.array(a_indices)

        return idx_review, idx_summary

def filter_data(sequences):
    filtered_q, filtered_a = [], []
    #raw_data_len = len(sequences)//2
    #print raw_data_len  
    print "total records", len(sequences)
    for i in range(0, len(sequences)):
        #qlen, alen = len(sequences[i].split(' ')), len(sequences[i+1].split(' '))
        qlen = len(sequences.iloc[i]['Review'])
        alen = len(sequences.iloc[i]['Summary'])
        #print qlen,alen
        if qlen >= limit['minreview'] and qlen <= limit['maxreview']:
            if alen >= limit['minsummary'] and alen <= limit['maxsummary']:
                filtered_q.append(sequences.iloc[i]['Review'])
                filtered_a.append(sequences.iloc[i]['Summary'])

    # print the fraction of the original data, filtered
    filt_data_len = len(filtered_q)
    #filtered = int((raw_data_len - filt_data_len)*100/raw_data_len)
    #print(str(filtered) + '% filtered from original data')
    print "New length %d",len(filtered_q)

    return filtered_q, filtered_a

def process_data():
    df = pd.DataFrame()
    ndf = pd.DataFrame()
    df['Review'] = __crawl_review(FILENAME)
    df['Summary'] =__crawl_summary(FILENAME)
    qlines, alines = filter_data(df)
    ndf['Review'] = qlines
    ndf['Summary']  = alines
    qtokenized = [ wordlist.split(' ') for wordlist in ndf['Review'] ]
    atokenized = [ wordlist.split(' ') for wordlist in ndf['Summary'] ]
    print('\n >> Index words')
    idx2w, w2idx, freq_dist = index_( qtokenized + atokenized, vocab_size=VOCAB_SIZE)
    print('\n >> Zero Padding')
    idx_q, idx_a = zero_pad(qtokenized, atokenized, w2idx)
    print " Data indexing is done"
    # save them
    np.save('/Users/nileshbhoyar/Documents/W266Project/datasets/idx_review.npy', idx_q)
    np.save('/Users/nileshbhoyar/Documents/W266Project/datasets/idx_summary.npy', idx_a)

    # let us now save the necessary dictionaries
    metadata = {
            'w2idx' : w2idx,
            'idx2w' : idx2w,
            'limit' : limit,
            'freq_dist' : freq_dist
                }

    # write to disk : data control dictionaries
    with open('/Users/nileshbhoyar/Documents/W266Project/datasets/metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    print "Data transformation is finished"
def load_data(PATH=''):
    # read data control dictionaries
    with open(PATH + '/Users/nileshbhoyar/Documents/W266Project/datasets/metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
    # read numpy arrays
    idx_q = np.load(PATH + '/Users/nileshbhoyar/Documents/W266Project/datasets/idx_review.npy')
    idx_a = np.load(PATH + '/Users/nileshbhoyar/Documents/W266Project/datasets/idx_summary.npy')
    return metadata, idx_q, idx_a
if __name__ == '__main__':
    process_data()
    
