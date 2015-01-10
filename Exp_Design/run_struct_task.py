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
practice_on = False

# set things up for practice, training and tests
subject_code = 'newtest'
block_len = random.choice([12,16,20])
block_len=4
num_blocks = 2
probs = (.9,.1)
config_file = makeConfigList(iden = subject_code, num_blocks = num_blocks,
                             block_len = block_len, probs1 = probs, probs2 = probs)
bot = test_bot.test_bot(config_file)

practice_file = '../Config_Files/Temp_Struct_Practice_config.yaml'
practice=psychTask(practice_file,subject_code, fullscreen = fullscr, bot = None)
task=psychTask(config_file,subject_code, fullscreen = fullscr, bot = None)
task.writeToLog(task.toJSON())


#************************************
# Start Practice
#************************************

if practice_on:
    # prepare to start
    practice.setupWindow()
    practice.defineStims()
    task_intro_text = [
        'Welcome\nPress 5 to move through instructions',
        """
        In this experiment, shapes will appear on the screen
        and you will need to learn how to respond to them.
        
        There will only be two shapes, and your responses
        will consist of one of four buttons:
        ('h', 'j', 'k', 'l')
        
        You must respond while the shape is on the screen.
        Please respond as quickly and accurately
        as possible.
        """,
        """
        After you press a key, the shape will dissapear
        and you will receive feedback about whether
        you won or lost.
        
        Your goal is to win as much as possible.
        """,
        """
        No key will win or lose all of the time.
        
        However, there are better key(s) to press for
        each shape that will win more often, and your
        job is to learn which they are.
        """,
        """
        Because each key can win and lose for each shape, 
        be sure to explore all the keys. Your first 
        instinct may not be correct.
        
        We will start with a brief training session. 
        Please wait for the experimenter.
        """
    ]
    
    for line in task_intro_text:
        practice.presentTextToWindow(line)
        resp,practice.startTime=practice.waitForKeypress(practice.trigger_key)
        practice.checkRespForQuitKey(resp)
        event.clearEvents()
    
    for trial in practice.stimulusInfo:
        # wait for onset time
        while core.getTime() < trial['onset'] + practice.startTime:
                key_response=event.getKeys(None,True)
                if len(key_response)==0:
                    continue
                for key,response_time in key_response:
                    if practice.quit_key==key:
                        practice.shutDownEarly()
        trial=practice.presentTrialWithFB(trial)
    
    # clean up
    practice.shutDownAndSave()
    practice.closeWindow()

#************************************
# Start training
#************************************

# prepare to start
task.setupWindow()
task.defineStims()
task.presentTextToWindow('Please wait for the experimenter')
resp,task.startTime=task.waitForKeypress(practice.trigger_key)
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
                    #Use trigger key to turn the bot on and off
                    task.trigger_times.append(response_time-task.startTime)
                    task.bot_on = not task.bot_on
                    continue

    trial=task.presentTrialWithFB(trial)
    task.writeToLog(json.dumps(trial))
    task.alldata.append(trial)
    #End the task if performance reaches some criterion
    if task.getPastAcc(2*block_len) >= 2*block_len*.9:
        print(task.getPastAcc(2*block_len))
        break


task.writeToLog(json.dumps({'trigger_times':task.trigger_times}))
task.writeData()
task.presentTextToWindow('Thank you. Please wait for the experimenter.')
task.waitForKeypress(task.quit_key)

# clean up
task.shutDownAndSave()
task.closeWindow()

#************************************
# Start test
#************************************

test=tempStructTest(config_file,subject_code,bot = None)
test.writeToLog(test.toJSON())

# prepare to start
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


