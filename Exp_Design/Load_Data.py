# -*- coding: utf-8 -*-
"""
Created on Tue Dec  9 14:22:54 2014

@author: admin
"""

import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal

config_file = '../Data/' + 'Pilot000_Temp_Struct_data_2015-01-13_14-57-54.yaml'
f=open(config_file)
loaded_yaml = yaml.load(f)
data = loaded_yaml['taskdata']
taskinfo = loaded_yaml['taskinfo']

#Reflects mapping of action keys to tasksets and stimuli
ts_map= [(0,1), (2,3)]
stim_map = [(0,2), (1,3)]

#Load data into a dataframe
df = pd.DataFrame(data)

# Responses and RT's are stored as lists, though we only care about the first one.
# When converting to list, replace empty RT's wi
rts = np.array([x[0]  for x in df.rt.values])
responses = [x[0] for x in df.response.values]
df.rt[:] = rts
df.response[:] = responses

#Remove missed trials:
df = df[df.response != 'NA']

