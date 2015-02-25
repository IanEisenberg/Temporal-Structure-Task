"""
runtempStructTask
"""

from psychopy import visual, core, event, logging, data, misc
import os, socket, random
import json
import webbrowser

from temp_struct_task import tempStructTask
from make_config import makeConfigList
import test_bot

#set-up some variables

verbose=True
fullscr=True  # change to True for full screen display
subdata=[]
practice_on = True
test_on = True

# set things up for practice, training and tests
try:
    f = open('IDs.txt','r')
    lines = f.readlines()
    f.close()
    last_id = lines[-1][:-1]
    subject_code = raw_input('Last subject: "%s". Input new subject code: ' % last_id);
except IOError:
    subject_code = raw_input('Input first subject code: ');
f = open('IDs.txt', 'a')
f.write(subject_code + '\n')
f.close()

block_len = 12
train_length = 60 #train_length in minutes
avg_trial_length = 2.75
#Find the minimum even number of blocks to last at least 60 minutes
num_blocks = int(round(train_length*60/(block_len*avg_trial_length)/2)*2)
probs = (.9,.1)
config_file = makeConfigList(iden = subject_code, num_blocks = num_blocks,
                             block_len = block_len, probs1 = probs, probs2 = probs)
bot = test_bot.test_bot(config_file)

practice_file = '../Config_Files/Temp_Struct_Practice_config.yaml'
practice=tempStructTask(practice_file,subject_code, fullscreen = fullscr, bot = None, mode = 'Practice')
task=tempStructTask(config_file,subject_code, fullscreen = fullscr, bot = None)
task.writeToLog(task.toJSON())

#************************************
# Start Practice
#************************************

if practice_on:
    # prepare to start
    practice.setupWindow()
    practice.defineStims()
    task_intro_text = [
        'Welcome\n\nPress 5 to move through instructions',
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
        After you press a key, the shape will disappear
        and you will either gain or lose points.
        
        Your goal is to get as many points as possible.
        Part of your payment will be determined by
        how many points you earn.
        """,
        """
        No key will win or lose all of the time.
        
        However, there are better key(s) to press for
        each shape that will win more often, and your
        job is to learn which they are.
        """,
        """
        The task is hard! Stay motivated and try to learn
        all you can.
        
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
        trial=practice.presentTrial(trial)
    
    # clean up
    practice.closeWindow()

#************************************
# Start training
#************************************

# prepare to start
task.setupWindow()
task.defineStims()
task.presentTextToWindow("""
                        We will now start the experiment.
                        
                        There will be one break half way through. 
                        
                        Please wait for the experimenter.
                        """)
resp,task.startTime=task.waitForKeypress(practice.trigger_key)
task.checkRespForQuitKey(resp)
event.clearEvents()


pause_trial = task.stimulusInfo[len(task.stimulusInfo)/2]
pause_time = 0
for trial in task.stimulusInfo:
    if trial == pause_trial:
        time1 = core.getTime()
        task.presentTextToWindow("Take a break! Press '5' when you're ready to continue.")
        task.waitForKeypress(task.trigger_key)
        task.clearWindow()
        pause_time = core.getTime() - time1
        
    # wait for onset time
    while core.getTime() < trial['onset'] + task.startTime + pause_time:
            key_response=event.getKeys(None,True)
            if len(key_response)==0:
                continue
            for key,response_time in key_response:
                if task.quit_key==key:
                    task.shutDownEarly()
                elif task.trigger_key==key:
                    task.trigger_times.append(response_time-task.startTime)
                    task.waitForKeypress()
                    continue

    trial=task.presentTrial(trial)
    task.writeToLog(json.dumps(trial))
    task.alldata.append(trial)


task.writeToLog(json.dumps({'trigger_times':task.trigger_times}))
task.writeData()
task.presentTextToWindow('Thank you. Please wait for the experimenter.')
task.waitForKeypress(task.quit_key)

# clean up
task.closeWindow()

#************************************
# Start test
#************************************

if test_on:
    
    test_num_blocks = 4
    test_config = makeConfigList(taskname = 'Temp_Struct_noFBTest', iden = subject_code, 
                                 num_blocks = test_num_blocks, block_len = block_len, probs1 = probs,
                                  probs2 = probs, action_keys = task.getActions())
    test=tempStructTask(test_config,subject_code,bot = None, mode = 'noFB')
    test.writeToLog(test.toJSON())
    
    # prepare to start
    test.setupWindow()
    test.defineStims(task.getStims())
    test.presentTextToWindow("""
                        In this next part the feedback will be invisible.
                        
                        Do your best to respond to the shapes as you would have
                        in the last section. 
                        
                        Please wait for the experimenter.
                        """)
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
    
        trial=test.presentTrial(trial)
        test.writeToLog(json.dumps(trial))
        test.alldata.append(trial)
    
    test.writeToLog(json.dumps({'trigger_times':task.trigger_times}))
    test.writeData()
    test.presentTextToWindow('Thank you. Please wait for the experimenter.')
    test.waitForKeypress(task.quit_key)
    
    # clean up
    test.closeWindow()
    

#************************************
# Determine payment
#************************************
points,trials = task.getPoints()
performance = float(points)/(trials*probs[0])
pay_bonus = round(performance*5*2)/2.0
print('Participant ' + subject_code + ' won ' + str(round(performance,2)) + ' points. Bonus: $' + str(pay_bonus))
webbrowser.open_new('https://stanforduniversity.qualtrics.com/SE/?SID=SV_aV1hwNrNXgX5NYN')






