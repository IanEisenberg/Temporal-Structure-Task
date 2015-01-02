# -*- coding: utf-8 -*-
"""
Created on Tue Dec  9 14:22:54 2014

@author: admin
"""
#{0: [0.4642857142857143, 0.0, 0.5021645021645021, 0.0], 1: [0.0, 0.4949494949494948, 0.0, 0.46428571428571436]}

import yaml
import numpy as n
import matplotlib.pyplot as plt
from scipy import signal

config_file = '../Data/' + 'Temp_Struct_Alan_log_2014-12-23_15-07-43.log'
'
f=open(config_file)
accuracy_track = 0
init_params = yaml.load(f.readline())
block_len = init_params['block_len']
action_keys = init_params['action_keys']
ts_map= [(0,1), (2,3)]
stim_map = [(0,2), (1,3)]

# Extract relevant trial level data
trials=[]
for line in f:
    trial = yaml.load(line) 
    trials += [trial]
#last line contains trigger times
trigger_times = trials[-1]
trials = trials[:-1]
    
train_len = len(trials)
actions = n.zeros(train_len)
correct_actions = n.zeros(train_len)
stims = n.zeros(train_len)
FBs = n.zeros(train_len)
RTs = n.zeros(train_len)
TSs = n.zeros(train_len)

for index in xrange(train_len):
    trial = trials[index]
    if trial['response'] != 'NA':
        actions[index] = action_keys.index(trial['response'][0])
        correct_actions[index] = action_keys.index(trial['correct_action'][0])
        stims[index] = trial['stim']
        FBs[index] = trial['FB']
        RTs[index] = trial['rt'][0]
        TSs[index] = int(correct_actions[index] in [2,3])

        

#summary datasets
acc = (actions==correct_actions)
errors = n.logical_not(acc)
#check if response is one of the two associated with TS1
conform_context = n.in1d(actions,[2,3]).astype(int)
#check if response is one of the two associated with stim1
conform_stim = n.in1d(actions,[1,3]).astype(int)

#Split trial in half and look at whether actions conformed to context or stim
#class more closely
def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]

#Recode errors by their type. CE = 0, SE = 1, Other = 2
#CE = context error, when error confroms to context (so 0 instead of 1, or 3 instead of 2)
#SE = stim error, when error conforms to stim (0 instead of 2, or 1 instead of 3)
#other is remaining errors (0 instead of 3, 1 instead of 2)
# Thus CE errors = [1,5], SE errors = [2,4], and other = 3

temp = actions[errors]+correct_actions[errors]
error_types = n.in1d(temp,[1,5])*0 + n.in1d(temp,[2,4])*1 + (temp==3)*2
errors_in = n.arange(train_len)[errors]
temp = error_types[errors_in<train_len]
count = [sum(temp==0), sum(temp==1), sum(temp==2)]
print(count)

win_size = block_len*2
cc_corr = n.zeros(train_len-win_size*2)
cs_corr = n.zeros(train_len-win_size*2)

for i in range(train_len-win_size*2):
    if i+win_size > train_len:
        upperbound = train_len
    else:
        upperbound = i+win_size
    action_chunk = actions[i:upperbound]
    cc_chunk = conform_context[i:upperbound]
    cs_chunk = conform_stim[i:upperbound]
    cc_corr[i] = n.corrcoef(action_chunk,cc_chunk)[0,1]
    cs_corr[i] = n.corrcoef(action_chunk,cs_chunk)[0,1]
    
plt.plot(range(len(cs_corr)),cs_corr)
plt.plot(range(len(cc_corr)),cc_corr)


#Compute average accuracy in windows defined by the actual block length
smoothed_acc = n.zeros(len(acc))
for t in xrange(len(acc)):
    if t-block_len/2 < 0:
        l_bound = 0
    else:
        l_bound = t-block_len/2
    if t+block_len/2 > len(acc):
        u_bound = len(acc)
    else:
        u_bound = t+block_len/2
    win_acc = n.mean(acc[l_bound:u_bound])
    smoothed_acc[t] = win_acc

#Plot Accuracy over time
x = range(len(acc))
plt.plot(x,smoothed_acc,'r')
plt.xlabel('Trial')
plt.ylabel('Acc')
for trial in xrange(len(acc)/block_len):
    plt.vlines(trial*block_len,min(smoothed_acc),max(smoothed_acc))
figure = plt.gcf()
figure.set_size_inches(8,6)
plt.savefig('../Plots/test.png', dpi = 100)