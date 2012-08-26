'''
Created on Aug 24, 2012

@author: ling0322
'''

from __future__ import unicode_literals
import hmm_pinyin
import random

count = 0
raw_correct = 0
modified_correct = 0

def incorrect(ch):
    rnd = random.randint(0, 100)
    if ch == '$':
        return ch
    if rnd > 70:
        return hmm_pinyin.emit_matrix[ch].keys()[random.randint(1, len(hmm_pinyin.emit_matrix[ch]) - 1)]
    return ch

count = 0.0
correct_original = 0.0
correct_first = 0.0
correct = 0.0
with open('googlepinyin.txt') as fp:
    for line in fp:
        seg = line.decode('utf-8').split(' ')
        chn_word = seg[0]
        pinyin = [pinyin.strip() for pinyin in seg[3:]]
        original_pinyin = ''.join(pinyin) + '$'
        incorrect_pinyin = ''.join(map(incorrect, original_pinyin))
        corrected_original_pinyin = ''.join(hmm_pinyin.viterbi(original_pinyin)[0])
        corrected_incorrect_pinyin_list = [''.join(corrected)
                                           for corrected in hmm_pinyin.viterbi(incorrect_pinyin)]
        correct_pinyin = '^' + "'".join(pinyin) + "'$"
        
        def print_incorrect():
            print count
            print 'original_pinyin: ' + correct_pinyin
            print 'incorrect_pinyin: ' + incorrect_pinyin
            print 'corrected_original_pinyin: ' + corrected_original_pinyin
            print 'corrected_incorrect_pinyin_list: ' + ' & '.join(corrected_incorrect_pinyin_list)
            print '------------'
            
        count += 1
        if correct_pinyin == corrected_original_pinyin:
            correct_original += 1
        else:
            print_incorrect() 
        if correct_pinyin == corrected_incorrect_pinyin_list[0]:
            correct_first += 1
        else:
            print_incorrect()
        if correct_pinyin in corrected_incorrect_pinyin_list:
            correct += 1
        else:
            print_incorrect()
            

print 'original pinyin correct: ' + str(correct_original / count * 100) + '%'
print 'first correct: ' + str(correct_first / count * 100) + '%'
print 'correct: ' + str(correct / count * 100) + '%'
        
        
        
        
        
        