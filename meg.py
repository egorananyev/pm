####!/usr/bin/arch -i386 /usr/bin/python # -*- coding: utf-8 -*-
from __future__ import print_function

"""
Investigating facilitative and suppressive interactions between stimuli.
Creator: Egor Ananyev
Original date: 2019-05-07
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, event, gui
import numpy as np
import os
import pandas as pd
from datetime import datetime

## Initial variables.
# experiment modes:
shocky = True
debug = False  # sets SOA to stim_dur+10 and lengthens stim_dur
# experiment variables:
exp_name = 'pm1'
# stimulus parameters:
stim_diam = 1.5  # for Shocky's Samsung monitor, a 5 deg stim = 6.3 cm
stim_sf = 4  # cycles per degree (e.g., for a 5 deg stim, there will be 5 cycles)
stim_x_off = stim_diam
# timing variables (note that the number of frames will differ for 60 and 100 Hz refresh rates):
fix_dur = int(60)  # in frames
if debug:
    stim_dur = 60
else:
    stim_dur = 2
beg_buff = 10  # beginning buffer prior to stimulus onset
end_buff = beg_buff * 10
wiggle = 10  # additional 'wiggle room' for jittering of stimulus onset
# interval duration includes two stimulus time windows to make the intervals consistent even if SOA=0:
interval_dur = int(stim_dur * 2 + beg_buff + end_buff + wiggle)  # 34 frames, or 340 ms
# trial duration:
resp_feedback_wait = 0.2

# Reassign stimulus durations for the slower refresh rate:
if shocky:
    fix_dur = int(fix_dur / 2)  # in frames
    stim_dur = stim_dur / 2  # 30 in debug
    beg_buff = beg_buff / 2  # beginning buffer prior to stimulus onset
    end_buff = beg_buff
    wiggle = wiggle / 2  # additional 'wiggle room' for jittering of stimulus onset
    # noinspection PyRedeclaration
    interval_dur = int(stim_dur * 2 + beg_buff + end_buff + wiggle)  # 17 frames, or 75 in debug

if shocky:
    ## These are here just for the record -- monitor dimensions are stored in PsychoPy monitor center
    # ds = 72
    # dr = (1920, 1080)  # display resolution in px
    # dd = (51.6, 29.2)  # office Samsung monitor
    screen_name = 'samsung'
    full_screen = True
else:
    ## These are here just for the record -- monitor dimensions are stored in PsychoPy monitor center
    # ds = 65  # distance to screen in cm
    # dr = (1152, 864)  # display resolution in px
    # dd = (40.0, 30.0)  # display dimensions in cm ... 39.0 x 29.5
    screen_name = 'station3'
    full_screen = True
# fixation cross:
fix_size = 0.2
# stimulus dimensions:

## getting user info about the experiment session:
exp_info = {u'expt': exp_name, u'subj': u'1', u'block': u'0', u'para': u'int'}  # block==0 is training block
exp_name = exp_info['expt']
para = exp_info['para']
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)  # dialogue box
if not dlg.OK:
    core.quit()  # user pressed cancel
exp_info['time'] = datetime.now().strftime('%Y-%m-%d_%H%M')

# Assigning conditions:
print('Block: ' + exp_info['block'])
if exp_info['block'] == '0':
    train = True
else:
    train = False

# Handling condition instructions:
if para == 'loc':
    cond_instr = 'Please do the following:\n' \
                 '- look at the fixation cross at all times\n' \
                 '- your targets are tilted gratings\n' \
                 '- they may appear either on the left or right of the fixation\n' \
                 '- there may be two, one, or *no* targets in a trial\n' \
                 '- they might appear simultaneously or in sequence\n' \
                 '- after each trial, indicate the location of the target(s):\n' \
                 '    - left arrow\n' \
                 '    - right arrow\n' \
                 '- please guess if you are unsure'
else:
    cond_instr = 'Please do the following:\n' \
                 '- look at the fixation cross at all times\n' \
                 '- your targets are tilted gratings\n' \
                 '- they may appear either in the first or second interval\n' \
                 '- there may be two, one, or *no* targets in a trial\n' \
                 '- the two targets might appear simultaneously or in sequence\n' \
                 '- after each trial, indicate the interval with target(s):\n' \
                 '    - left arrow = 1st interval\n' \
                 '    - right arrow = 2nd interval\n' \
                 '- please guess if you are unsure'

## Input and output

# Condition file:
if train:
    exp_conditions = 'cond-files/cond_' + exp_name + '_train' + '.xlsx'
else:
    exp_conditions = 'cond-files/cond_' + exp_name + '.xlsx'

# Trial handler depending on the measure or experimental stage:
# trials = pd.read_excel('C:\Users\egora\Dropbox\Projects\pm\pm\cond-files\cond_pm1_train.xlsx')
trials = pd.read_excel(exp_conditions)
trials['drops'] = 0

# Output file:
exp_dir = '..' + os.sep + 'data' + os.sep + exp_name + '_' + para
if not os.path.exists(exp_dir):
    print('experiment directory does not exist')
    os.makedirs(exp_dir)
else:
    print('experiment directory exists')
subj_dir = exp_dir + os.sep + 'subj-%02d' % int(exp_info['subj'])
if not os.path.exists(subj_dir):
    os.makedirs(subj_dir)
block_dir = subj_dir + os.sep + 'block-%s_%s' % (exp_info['block'], exp_info['time'])
if not os.path.exists(block_dir):
    os.makedirs(block_dir)
out_file_path = block_dir + os.sep + 'beh_out.csv'

# Output matrix:
output_mat = {}

## Monitor setup:
if shocky:
    window = visual.Window(monitor=screen_name, fullscr=full_screen, screen=0, units='deg')
else:
    # TODO make sure that 'station3' monitor profile exists and is properly configured
    window = visual.Window(fullscr=full_screen, monitor=screen_name, color=[-.5, -.5, -.5], units='deg',
                           allowStencil=True, autoLog=False, screen=0, waitBlanking=False)

if shocky:
    if debug:
        frame_rate = window.getActualFrameRate()
        print('frame rate: ' + str(frame_rate))
    else:
        frame_rate = 60
else:
    frame_rate = window.getActualFrameRate()
    print('frame rate: ' + str(frame_rate))
    if frame_rate < 100:
        print('WARNING! The measured frame rate is lower than expected')

## Initialize the stimuli and instructions
space_text = "\n\nPress the spacebar to start"
instr_text = cond_instr + space_text
instr_text_stim = visual.TextStim(window, text=instr_text, height=.6, pos=[0, 1])
fix_cross = visual.TextStim(window, text='+', bold='True', pos=[0, 0], rgb=1, height=fix_size)

# Target:
stim1 = visual.GratingStim(window, size=stim_diam, tex='sin', mask='gauss', pos=(0, 0), sf=stim_sf)
stim2 = visual.GratingStim(window, size=stim_diam, tex='sin', mask='gauss', pos=(0, 0), sf=stim_sf)
box = visual.Rect(window, width=5, height=5, lineColor='white')

# Response buttons & text:
text_size = .6

# Button dimensions and positions:
button_dim = [3, 1.2]
button_off = [3.2, 0]
button1_pos = (-button_off[0], button_off[1])
button2_pos = (0, button_off[1])
button3_pos = (button_off[0], button_off[1])

# Arrow text:
arrow_y_off = .3
arrow1_pos = (-button_off[0], button_off[1]+arrow_y_off+.1)
arrow2_pos = (0, button_off[1]+arrow_y_off+.1)
arrow3_pos = (button_off[0], button_off[1]+arrow_y_off+.1)
button1_arrow = visual.TextStim(window, text=u'\u2190', height=text_size, pos=arrow1_pos)
button2_arrow = visual.TextStim(window, text=u'\u2193', height=text_size, pos=arrow2_pos)
button3_arrow = visual.TextStim(window, text=u'\u2192', height=text_size, pos=arrow3_pos)

# Text positions:
text1_pos = (-button_off[0], button_off[1]-arrow_y_off+.1)
text2_pos = (0, button_off[1]-arrow_y_off+.1)
text3_pos = (button_off[0], button_off[1]-arrow_y_off+.1)

# Interval:
if para == 'int':
    resp_loc_text = visual.TextStim(window, text='interval?', height=text_size, pos=[0, 1.2])
    # For simplicity, I will refer to interval judgment as that of (temporal) location.
    button_text_left = 'first'
    button_text_right = 'second'
# Location:
elif para == 'loc':
    resp_loc_text = visual.TextStim(window, text='location?', height=text_size, pos=[0, 1.2])
    button_text_left = 'left'
    button_text_right = 'right'
else:
    button_text_left = ''
    button_text_right = ''
    print('ERROR: Paradigm string not recognized!')
resp_loc_button1 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button1_pos)
resp_loc_button1_text = visual.TextStim(window, text=button_text_left, height=text_size, pos=text1_pos)
resp_loc_button2 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button3_pos)
resp_loc_button2_text = visual.TextStim(window, text=button_text_right, height=text_size, pos=text3_pos)

# Number:
resp_num_text = visual.TextStim(window, text='number of targets?', height=text_size, pos=[0, 1.2])
resp_num_button1 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button1_pos)
resp_num_button1_text = visual.TextStim(window, text='none', height=text_size, pos=text1_pos)
resp_num_button2 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button2_pos)
resp_num_button2_text = visual.TextStim(window, text='one', height=text_size, pos=text2_pos)
resp_num_button3 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button3_pos)
resp_num_button3_text = visual.TextStim(window, text='two', height=text_size, pos=text3_pos)

# Orientation:
resp_ori_text = visual.TextStim(window, text='pattern?', height=text_size, pos=[0, 1.2])
resp_ori_button1 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button1_pos)
resp_ori_button1_text = visual.TextStim(window, text='left tilt', height=text_size, pos=text1_pos)
resp_ori_button2 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button2_pos)
resp_ori_button2_text = visual.TextStim(window, text='both tilts', height=text_size, pos=text2_pos)
resp_ori_button3 = visual.Rect(window, width=button_dim[0], height=button_dim[1], pos=button3_pos)
resp_ori_button3_text = visual.TextStim(window, text='right tilt', height=text_size, pos=text3_pos)

# The response buttons will remain in place: I won't make them toglable at this stage, but they won't render during
# trials if they are not required.

## Number of stimuli response buttons:
def resp_num_draw():
    # Confidence rendering:
    resp_num_text.draw()
    resp_num_button1.draw()
    button1_arrow.draw()
    resp_num_button1_text.draw()
    resp_num_button2.draw()
    button2_arrow.draw()
    resp_num_button2_text.draw()
    resp_num_button3.draw()
    button3_arrow.draw()
    resp_num_button3_text.draw()

def resp_num_monitor():
    # Monitoring for key presses:
    arrow_keys_ = event.getKeys(keyList=['left', 'right', 'down', 'space', 'escape'])
    if len(arrow_keys_) > 0:
        if 'left' in arrow_keys_:
            print('number response: 0', end='   ')
            resp_num_ = 0
            resp_num_button1.lineColor = 'red'
            resp_num_button1.draw()
        elif 'down' in arrow_keys_:
            print('number response: 1', end='   ')
            resp_num_ = 1
            resp_num_button2.lineColor = 'red'
            resp_num_button2.draw()
        elif 'right' in arrow_keys_:
            print('number response: 2', end='   ')
            resp_num_ = 2
            resp_num_button3.lineColor = 'red'
            resp_num_button3.draw()
        elif 'space' in arrow_keys_:
            resp_num_ = 'X'
        elif 'escape' in arrow_keys_:
            exit_routine()
        # noinspection PyUnboundLocalVariable
        return resp_num_
    else:
        return 'N'

# Resetting the number response buttons:
def resp_num_reset():
    resp_num_button1.lineColor = 'white'
    resp_num_button2.lineColor = 'white'
    resp_num_button3.lineColor = 'white'

## Location response buttons:
def resp_loc_draw():
    # Confidence rendering:
    resp_loc_text.draw()
    resp_loc_button1.draw()
    button1_arrow.draw()
    resp_loc_button1_text.draw()
    resp_loc_button2.draw()
    button3_arrow.draw()
    resp_loc_button2_text.draw()

def resp_loc_monitor():
    # Monitoring for key presses:
    arrow_keys_ = event.getKeys(keyList=['left', 'right', 'space', 'escape'])
    if len(arrow_keys_) > 0:
        if 'left' in arrow_keys_:
            print('location response: Left', end='   ')
            resp_loc_ = 'L'
            resp_loc_button1.lineColor = 'blue'
            resp_loc_button1.draw()
        elif 'right' in arrow_keys_:
            print('location response: Right', end='   ')
            resp_loc_ = 'R'
            resp_loc_button2.lineColor = 'red'
            resp_loc_button2.draw()
        elif 'space' in arrow_keys_:
            resp_loc_ = 'X'
        elif 'escape' in arrow_keys_:
            exit_routine()
        # noinspection PyUnboundLocalVariable
        return resp_loc_
    else:
        return 'N'

# Resetting the response buttons:
def resp_loc_reset():
    resp_loc_button1.lineColor = 'white'
    resp_loc_button2.lineColor = 'white'

## Orientation response buttons:
def resp_ori_draw(resp_num_):
    # Button rendering:
    resp_ori_text.draw()
    resp_ori_button1.draw()
    button1_arrow.draw()
    resp_ori_button1_text.draw()
    if resp_num_ == 2:
        resp_ori_button2.draw()
        button2_arrow.draw()
        resp_ori_button2_text.draw()
    resp_ori_button3.draw()
    button3_arrow.draw()
    resp_ori_button3_text.draw()

def resp_ori_monitor(resp_num_):
    # Monitoring for key presses:
    arrow_keys_ = event.getKeys(keyList=['left', 'down', 'right', 'space', 'escape'])
    if len(arrow_keys_) > 0:
        if 'left' in arrow_keys_:
            print('orientation response: Left', end='   ')
            resp_ori_ = 'L'
            resp_ori_button1.lineColor = 'red'
            resp_ori_button1.draw()
        elif 'down' in arrow_keys_ and resp_num_ == 2:
            print('orientation response: Both', end='   ')
            resp_ori_ = 'B'
            resp_ori_button2.lineColor = 'red'
            resp_ori_button2.draw()
        elif 'down' in arrow_keys_ and not resp_num_ == 2:
            print('improper response: dropping trial')
            resp_ori_ = 'X'
        elif 'right' in arrow_keys_:
            print('orientation response: Right', end='   ')
            resp_ori_ = 'R'
            resp_ori_button3.lineColor = 'red'
            resp_ori_button3.draw()
        elif 'space' in arrow_keys_:
            resp_ori_ = 'X'
        elif 'escape' in arrow_keys_:
            exit_routine()
        # noinspection PyUnboundLocalVariable
        return resp_ori_
    else:
        return 'N'

def resp_ori_reset(resp_num_):
    resp_ori_button1.lineColor = 'white'
    if resp_num_ == 2:
        resp_ori_button2.lineColor = 'white'
    resp_ori_button3.lineColor = 'white'

## Handy routines:
# Return the angle of the orientation
def stim_ori_angle(stim_ori_):
    if stim_ori_ == 'L':
        return 135
    elif stim_ori_ == 'R':
        return 45
    else:
        exit_routine()
        return 0

# This is done at every frame update, regardless of trial phase, so predefining:
def frame_routine():
    flip_time_ = window.flip()
    # Checking for quit (the Esc key)
    if event.getKeys(keyList=['escape']):
        exit_routine()
    return flip_time_

# Also no variation across frames, but only available upon call, which is made only in key registering phase.
def exit_routine():
    # Say goodbye:
    window.flip()
    instr_text_stim.setText('    Finished!\nRecording data...')
    instr_text_stim.draw()
    core.wait(.7)
    window.flip()

    # Behavioural data output:
    if not output_mat:  # means that the dictionary is empty
        print('\n===================\nthe output file is empty')
    else:
        data_columns = ['exp_name', 'frame_rate', 'stim_dur', 'beg_buff', 'end_buff', 'wiggle',  # experiment specs
                        'subj', 'block', 'trial_id',  # log info
                        'soa', 'stim1_ori', 'stim2_ori', 'stim1_c', 'stim2_c',  # stim info
                        'stim_loc', 'jitter',  # randomized variables
                        'resp_num', 'resp_loc', 'resp_ori', 'drops']  # subj resp
        pd.DataFrame.from_dict(output_mat, orient='index').to_csv(out_file_path, index=False, columns=data_columns)
        print('\noutput file path is ' + out_file_path)

    # Close the graphics
    window.close()
    core.quit()


## Initiating the trial loop
n_trials_done = 0
while len(trials > 0):

    ## First trial initiates instructions and sends the expt initiation message to the eye tracker:
    if n_trials_done == 0:
        # Update the instruction screen text:
        instr_text_stim.setText(instr_text)
        instr_text_stim.draw()
        flip_time = window.flip()
        # Wait until a space key event occurs after the instructions are displayed:
        event.waitKeys(' ')

    ## Randomly picking the current trial row, assigning it to 'trial' var, and dropping it from 'trials':
    cur_trial_indx = int(np.random.choice(trials.index.values, 1))
    trial = trials.ix[cur_trial_indx].copy()  # an explicit copy() is necessary due to a warning otherwise
    trials = trials.drop([cur_trial_indx])
    drop_trial = False
    # print(trial)

    n_trials_done += 1
    print('\n======TRIAL#' + str(n_trials_done) + '======')

    ## Assigning the trial variables:

    # Token variables:
    resp_loc_given = False
    resp_num_given = False
    resp_ori_given = False

    # Randomizing whether the stimuli will appear on the left or right:
    stim_loc_R2 = np.random.randint(2)  # 0 if Left and 1 if Right - used in the loop check (BOOL is faster)
    if para == 'loc':
        if stim_loc_R2:
            stim_loc = 'R'
        else:
            stim_loc = 'L'
        stim_pos = (-stim_x_off + stim_x_off * stim_loc_R2 * 2, 0)
        stim1.pos = stim_pos
        stim2.pos = stim_pos
    else:
        if stim_loc_R2:
            stim_loc = '2nd'
        else:
            stim_loc = '1st'

    # Timing variables.

    # Stimulus onset asynchrony, in frames: must be greater than stimulus duration:
    soa = trial['SOA']
    if shocky:
        soa = soa / 2
    if debug:
        if soa > 0:
            soa = soa + stim_dur
    # Jittering the onset timing for the first or only stimulus, in frames:
    jitter = np.random.randint(wiggle+1)  # the jitter could be zero
    if debug:
        print('jitter=' + str(jitter))
    # Onsets and frames of the stimuli:
    stim1_onset = beg_buff + jitter  # time for first stimulus onsets, in frames, from the onset of the interval
    stim1_twin = np.add(stim1_onset, range(int(stim_dur)))  # stimulus time window, i.e., the frames in which it appears
    # print('stim1 time window:')
    # print(stim1_twin)
    stim2_onset = stim1_onset + soa
    stim2_twin = np.add(stim2_onset, range(int(stim_dur)))
    # print('stim2 time window:')
    # print(stim2_twin)

    # Stimulus contrast / opacity:
    stim1_c = trial['stim1_c']  # stimulus contrast, log scaled
    stim1.contrast = 10 ** stim1_c
    stim2_c = trial['stim2_c']
    stim2.contrast = 10 ** stim2_c

    # Stimulus orientation:
    stim1_ori = trial['stim1_ori']
    stim1.ori = stim_ori_angle(stim1_ori)
    stim2_ori = trial['stim2_ori']
    stim2.ori = stim_ori_angle(stim2_ori)

    # Print trial specifics to screen:
    print('loc=' + str(stim_loc) + ' soa=' + str(int(soa)) + ' ori1=' + str(stim1_ori) + ' ori2=' + str(stim2_ori) +
          ' c1=' + str(stim1_c) + ' c2=' + str(stim2_c))

    ## Pre-trial fixation phase:
    for cur_frame in range(fix_dur):
        flip_time = frame_routine()
        fix_cross.draw()

    ## The number of if intervals is 2 for interval-based paradigms:
    if para == 'loc':
        int_num = 0  # only a single interval for the location-based paradigm
        stim_loc_R2 = 0  # I promise I'll be careful
    elif para == 'int':
        int_num = [0, 1]
    else:
        print('ERROR: Paradigm string not recognized!')

    ## Presentation phase
    # Iterating through intervals:
    for cur_int in [0, 1]:
        if cur_int == 0:
            box.lineColor = 'blue'
        else:
            box.lineColor = 'red'
        for cur_frame in range(interval_dur):
            # Fixation presentation & frame routine:
            flip_time = frame_routine()
            if para == 'loc':
                fix_cross.draw()
            box.draw()

            # Stimulus presentation:
            if cur_int == stim_loc_R2:
                # first stimulus time window:
                if cur_frame in stim1_twin:
                    if debug:
                        print('/', end='')
                    # draw the first stimulus
                    stim1.draw()
                # second stimulus time window (may overlap with the first):
                if cur_frame in stim2_twin:
                    if debug:
                        print('\\', end='')
                    # draw the second stimulus
                    stim2.draw()
                if debug:
                    if cur_frame not in stim1_twin and cur_frame not in stim2_twin:
                        print('-', end='')
            else:
                if debug and para == 'int':
                    print('-', end='')
        if debug:
            print('\n', end='')

        ## Post-trial fixation phase:
        box.lineColor = 'white'
        for cur_frame in range(fix_dur):
            flip_time = frame_routine()
            if para == 'loc':
                fix_cross.draw()
            box.draw()

    ## Response phase:
    event.clearEvents()

    # Stimulus number response:
    resp_num = 'N'
    if exp_name == 'pm2':
        while not resp_num_given:

            window.flip()

            # Stimulus number response:
            resp_num_draw()
            if not resp_num_given:
                if resp_num == 'N':
                    resp_num = resp_num_monitor()
                else:
                    if resp_num == 'X':
                        drop_trial = True
                    resp_num_given = True
                    event.clearEvents()

        resp_num_reset()
        window.flip()
        core.wait(resp_feedback_wait)
        event.clearEvents()

    # Location response:
    resp_loc = 'N'
    if exp_name == 'pm1':
        while not resp_loc_given:

            window.flip()

            # Interval response:
            resp_loc_draw()
            if not resp_loc_given:
                if resp_loc == 'N':
                    resp_loc = resp_loc_monitor()
                else:
                    if resp_loc == 'X':
                        drop_trial = True
                    resp_loc_given = True
                    event.clearEvents()

        resp_loc_reset()
        window.flip()
        core.wait(resp_feedback_wait)
        event.clearEvents()

    # Orientation response:
    resp_ori = 'N'
    if exp_name == 'pm2' and resp_num > 0 and not drop_trial:
        while not resp_ori_given:

            window.flip()

            # Stimulus number response:
            resp_ori_draw(resp_num)
            if not resp_ori_given:
                if resp_ori == 'N':
                    resp_ori = resp_ori_monitor(resp_num)
                else:
                    if resp_ori == 'X':
                        drop_trial = True
                    resp_ori_given = True
                    event.clearEvents()

        resp_ori_reset(resp_num)
        window.flip()
        core.wait(resp_feedback_wait)
        event.clearEvents()

    ## Trial termination feedback:
    if drop_trial:
        trial_drops = trial['drops'] + 1
        trial['drops'] = trial_drops
        trials = trials.append(trial)
    else:
        trial_drops = trial['drops']
    instr_text_stim.setText('press spacebar to continue')
    instr_text_stim.draw()
    fix_cross.draw()
    window.flip()

    # wait until a space key event occurs after the instructions are displayed
    event.waitKeys(' ')

    flip_time = window.flip()

    ## Recording the data
    if not drop_trial:
        output_mat[n_trials_done - 1] = {'exp_name': exp_name, 'frame_rate': frame_rate, 'stim_dur': stim_dur,
                                         'beg_buff': beg_buff, 'end_buff': end_buff, 'wiggle': wiggle,
                                         'subj': exp_info['subj'], 'block': exp_info['block'],
                                         'trial_id': n_trials_done, 'soa': soa,
                                         'stim1_ori': stim1_ori, 'stim2_ori': stim2_ori,
                                         'stim1_c': stim1_c, 'stim2_c': stim2_c,
                                         'stim_loc': stim_loc, 'jitter': jitter,
                                         'resp_num': resp_num, 'resp_loc': resp_loc, 'resp_ori': resp_ori,
                                         'drops': trial_drops}

# Finishing the experiment
exit_routine()
