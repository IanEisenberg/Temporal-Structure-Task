"""
runPsychTask
"""

import psychopy
from psychopy import visual, core, event, logging, data, misc, sound
import os, socket, random
import json

from temp_struct_task import psychTask
from temp_struct_test_noFB import tempStructTest
from make_config import makeConfigList
import test_bot
#set-up some variables

verbose=True
fullscr=False  # change to True for full screen display
subdata=[]

# set things up for training and tests

subject_code = '000'
block_len = random.choice(range(10,22,2))
probs = (.9,.1)
config_file = make_config.makeConfigList(iden = subject_code, block_len = block_len, 
                             probs1 = probs, probs2 = probs)
bot = test_bot.test_bot(config_file)

#************************************
# Start training
#************************************
task=psychTask(config_file,subject_code, bot = None)
task.writeToLog(task.toJSON())

# prepare to start
task.setupWindow()
task.defineStims()
task.presentTextToWindow('Waiting for key to begin (or press 5)\nPress q to quit')
resp,task.startTime=task.waitForKeypress(task.trigger_key)
task.checkRespForQuitKey(resp)
event.clearEvents()

for trial in task.stimulusInfo:
    # wait for onset time
    while core.getTime() < trial['onset'] + task.startTime:
            key_response=event.getKeys(None,True)
            if len(key_response)==0:
                continue
            for key,response_time in key_response:
                if task.quit_key==key:
                    task.shutDownEarly()
                elif task.trigger_key==key:
                    task.trigger_times.append(response_time-task.startTime)
                    task.bot_on = not task.bot_on
                    print task.tasksets
                    continue

    trial=task.presentTrialWithFB(trial)
    task.writeToLog(json.dumps(trial))
    task.alldata.append(trial)
    #End the task if performance reaches some criterion
    if task.getPastAcc(2*block_len) >= 2*block_len*.9:
        print(task.getPastAcc(2*block_len))
        break


task.writeToLog(json.dumps({'trigger_times':task.trigger_times}))

task.presentTextToWindow('Thank you. Please wait for the experimenter.')
task.waitForKeypress(task.quit_key)

# clean up
task.shutDownAndSave()
task.closeWindow()

#************************************
# Start test
#************************************

# prepare to start
test=tempStructTest(config_file,subject_code,bot = None)
test.writeToLog(test.toJSON())

test.setupWindow()
test.defineStims()
test.presentTextToWindow('Waiting for key to begin (or press 5)\nPress q to quit')
resp,test.startTime=test.waitForKeypress(test.trigger_key)
test.checkRespForQuitKey(resp)
event.clearEvents()

for trial in test.stimulusInfo:
    # wait for onset time
    while core.getTime() < trial['onset'] + test.startTime:
            key_response=event.getKeys(None,True)
            if len(key_response)==0:
                continue
            for key,response_time in key_response:
                if test.quit_key==key:
                    test.shutDownEarly()
                elif test.trigger_key==key:
                    test.trigger_times.append(response_time-test.startTime)
                    continue

    trial=test.presentTextTrialWithFB(trial)
    test.writeToLog(json.dumps(trial))
    test.alldata.append(trial)


