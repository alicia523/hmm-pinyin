from __future__ import unicode_literals
import json

elem_list = set(('^', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 
             'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '$'))

# load trans matrix from pinyin list

trans_matrix = {key: {} for key in elem_list}

with open('googlepinyin.txt') as fp:
    for line in fp:
        seg = line.decode('utf-8').split(' ')
        chn_char = seg[0]
        if len(chn_char) > 1:
            
            # finish loop when meets 2-char word
            break
        freq = float(seg[1])
        pinyin = seg[3]
        
        last_char = '^'
        for ch, index in zip(pinyin, range(len(pinyin))):
            ch = '$' if ch == '\n' else ch
            
            # the last char of a line is $ so the last char of pinyin is len(line) - 2
            if index == len(pinyin) - 2:
                ch = ch + "'"
                
                # add the x' element into elem_list
                elem_list.add(ch)
            
            if last_char not in trans_matrix:
                trans_matrix[last_char] = {}
            trans_matrix[last_char][ch] = trans_matrix.get(last_char, {}).get(ch, 0.0) + 1
            last_char = ch


# change the trans_prof of ^ to $
trans_matrix['^']['$'] = 100

for key, value in trans_matrix.items():
    
    # the trans_prob of x' just equal to the trans_prob of ^
    if len(key) == 2: # letter like x'
        trans_matrix[key] = trans_matrix['^']
        value = trans_matrix['^']
        
    count = sum(value.values())
    if count == 0:
        continue
    for sub_key, sub_value in value.items():
        trans_matrix[key][sub_key] /= count

# this is  emit matrix


prob_t_c = 0.8
prob_t_i = (1 - prob_t_c) / 2
prob_d_c = 1 - prob_t_i
prob_d_i = prob_t_i
emit_matrix = {
    '^': {'^': 1.0},
    'a': {'a': prob_d_c, 's': prob_d_i},
    'b': {'b': prob_t_c, 'v': prob_t_i, 'n': prob_t_i},
    'c': {'c': prob_t_c, 'x': prob_t_i, 'v': prob_t_i},
    'd': {'d': prob_t_c, 's': prob_t_i, 'f': prob_t_i},
    'e': {'e': prob_t_c, 'w': prob_t_i, 'r': prob_t_i},
    'f': {'f': prob_t_c, 'd': prob_t_i, 'g': prob_t_i},
    'g': {'g': prob_t_c, 'f': prob_t_i, 'h': prob_t_i},
    'h': {'h': prob_t_c, 'g': prob_t_i, 'j': prob_t_i},
    'i': {'i': prob_t_c, 'u': prob_t_i, 'o': prob_t_i},
    'j': {'j': prob_t_c, 'h': prob_t_i, 'k': prob_t_i},
    'k': {'k': prob_t_c, 'j': prob_t_i, 'l': prob_t_i},
    'l': {'l': prob_d_c, 'k': prob_d_i},
    'm': {'m': prob_d_c, 'n': prob_d_i},
    'n': {'n': prob_t_c, 'b': prob_t_i, 'm': prob_t_i},
    'o': {'o': prob_t_c, 'i': prob_t_i, 'p': prob_t_i},
    'p': {'p': prob_d_c, 'o': prob_d_i},
    'q': {'q': prob_d_c, 'w': prob_d_i},
    'r': {'r': prob_t_c, 'e': prob_t_i, 't': prob_t_i},
    's': {'s': prob_t_c, 'a': prob_t_i, 'd': prob_t_i},
    't': {'t': prob_t_c, 'r': prob_t_i, 'y': prob_t_i},
    'u': {'u': prob_t_c, 'y': prob_t_i, 'i': prob_t_i},
    'v': {'v': prob_t_c, 'c': prob_t_i, 'b': prob_t_i},
    'w': {'w': prob_t_c, 'q': prob_t_i, 'e': prob_t_i},
    'x': {'x': prob_t_c, 'z': prob_t_i, 'c': prob_t_i},
    'y': {'y': prob_t_c, 't': prob_t_i, 'u': prob_t_i},
    'z': {'z': prob_d_c, 'x': prob_d_i},
    '$': {'$': 1.0}
}

# add elements like x' into emit_matrix
for elem in elem_list:
    if len(elem) == 2:
        emit_matrix[elem] = emit_matrix[elem[0]]


def viterbi(seq, prob = None, path = None, n = 3):
    prob = {'^': [1.0]} if prob == None else prob
    path = {'^': [['^']]} if path == None else path
    
    observe_ch = seq[0]
    new_path = {}
    new_prob = {}
    
    def p(last_state, last_state_index, current_state, observe_ch):
        return prob[last_state][last_state_index] * trans_matrix[last_state].get(current_state, 0.0) * emit_matrix[current_state].get(observe_ch, 0.0)
    
    def state_iter(path):
        for state in path.keys():
            for index in range(len(path[state])):
                yield state, index
    
    for state in elem_list:
        prob_list = [(p(st, index, state, observe_ch), st, index)
            for st, index in state_iter(path)]
        prob_list.sort(key = lambda x: x[0], reverse = True)
        top_n_path = prob_list[:n]
        
        if len(top_n_path) == 0:
            continue
        
        if top_n_path[0][0] == 0.0:
            continue
        
        new_prob[state] = []
        new_path[state] = []
        for state_prob, last_state, index in top_n_path:
            new_prob[state].append(state_prob)
            new_path[state].append(path[last_state][index] + [state])

    if observe_ch == '$':
        return new_path['$']
    else:
        #print json.dumps({key: [new_prob[key], new_path[key]] for key in new_prob.keys()})
        return viterbi(seq[1: ], new_prob, new_path)



#print json.dumps(viterbi('wi$'))
#print json.dumps(trans_matrix)