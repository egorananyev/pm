####!/usr/bin/arch -i386 /usr/bin/python # -*- coding: utf-8 -*-
from __future__ import print_function

"""
Investigating facilitative and suppressive interactions between stimuli.
Creator: Egor Ananyev
Original date: 2019-05-07
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, event, gui, sound, monitors
import numpy as np
import os
from psychopy.data import TrialHandler, importConditions
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
# timing variables (note that the number of frames will differ for 60 and 100 Hz refresh rates):
fix_dur = 30  # in frames
if debug:
    stim_dur = 60
else:
    stim_dur = 2
beg_buff = 10  # beginning buffer of fixation
end_buff = beg_buff
wiggle = 10  # additional 'wiggle room' for jittering of stimulus onset
# interval duration includes two stimulus time windows to make the intervals consistent even if SOA=0:
interval_dur = stim_dur * 2 + beg_buff + end_buff + wiggle  # 34 frames, or 340 ms
# trial duration:
trial_dur = fix_dur + interval_dur * 2  # 88 frames

# Reassign stimulus durations for the slower refresh rate:
if shocky:
    fix_dur = fix_dur / 2  # in frames
    stim_dur = stim_dur / 2
    beg_buff = beg_buff / 2  # beginning buffer of fixation
    end_buff = beg_buff
    wiggle = wiggle / 2  # additional 'wiggle room' for jittering of stimulus onset
    interval_dur = stim_dur * 2 + beg_buff + end_buff + wiggle  # 17 frames
    trial_dur = fix_dur + interval_dur * 2  # 44 frames

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
fix_size = 0.8
# stimulus dimensions:

## getting user info about the experiment session:
exp_info = {u'expt': exp_name, u'subj': u'1', u'sess': u'1', u'block': u'0'}  # block==0 is training block
exp_name = exp_info['expt']
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)  # dialogue box
if not dlg.OK:
    core.quit()  # user pressed cancel
exp_info['time'] = datetime.now().strftime('%Y-%m-%d_%H%M')

# Assigning conditions:
train = False
print('Block: ' + exp_info['block'])
if exp_info['block'] == '0':
    train = True

# Handling condition instructions:
if train:
    cond_instr = 'Please do the following:\n' \
                 '(1) ...\n' \
                 '(2) ...\n' \
                 '(3) ...'

## Input and output

# condition file:
if train:
    exp_conditions = importConditions('cond-files/cond_' + exp_name + '_train' + '.xlsx')
else:
    exp_conditions = importConditions('cond-files/cond_' + exp_name + '.xlsx')

# Trial handler depending on the measure or experimental stage:
trials = TrialHandler(exp_conditions, 1, extraInfo=exp_info)

# output file:
exp_dir = '..' + os.sep + 'data' + os.sep + exp_name
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

# output matrix:
output_mat = {}

## Monitor setup
if shocky:
    # window = visual.Window(monitor=screen_name, fullscr=full_screen, screen=1, color=[-.5, -.5, -.5], units='deg')
    window = visual.Window(monitor=screen_name, fullscr=full_screen, screen=1, units='deg')
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
instr_text_stim = visual.TextStim(window, text=instr_text, height=.8)
fix_cross = visual.TextStim(window, text='+', bold='True', pos=[0, 0], rgb=1, height=fix_size)

# target:
# TODO substitute with a Gabor stimulus
stim1 = visual.GratingStim(window, size=stim_diam, tex='sin', mask='gauss', pos=(0, 0), sf=stim_sf)
stim2 = stim1
box = visual.Rect(window, width=5, height=5)

# confidence stimuli:
conf_text = visual.TextStim(window, text='confidence?', height=.4, pos=[0, -1])
box1 = visual.Rect(window, width=.5, height=.2, pos=(-1, -1))
box1_text = visual.TextStim(window, text='1=none')
box2 = visual.Rect(window, width=.5, height=.2, pos=(0, -1))
box2_text = visual.TextStim(window, text='2=some')
box3 = visual.Rect(window, width=.5, height=.2, pos=(1, -1))
box3_text = visual.TextStim(window, text='3=full')

## Handy routines:


# Confidence rendering:
def draw_conf():
    conf_text.draw()
    box1.draw()
    box1_text.draw()
    box2.draw()
    box2_text.draw()
    box3.draw()
    box3_text.draw()


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
    window.flip()

    # Behavioural data output:
    if not output_mat:  # means that the dictionary is empty
        print('\n===================\nthe output file is empty')
    else:
        data_columns = ['exp_name', 'frame_rate', 'stim_dur', 'beg_buff', 'end_buff', 'wiggle',  # experiment specs
                        'subj', 'sess', 'block', 'trial_id',  # log info
                        'soa', 'angle_diff', 'stim1_ori', 'stim2_ori', 'stim1_c', 'stim2_c',  # stim info
                        'stim_interval', 'jitter',  # randomized variables
                        'resp_interval', 'resp_number', 'resp_ori', 'resp_conf']  # subj resp
        pd.DataFrame.from_dict(output_mat, orient='index').to_csv(out_file_path, index=False, columns=data_columns)
        print('output file path is ' + out_file_path)

    # Close the graphics
    window.close()
    core.quit()



## Initiating the trial loop
n_trials_done = 0

for trial in trials:

    ## First trial initiates instructions and sends the expt initiation message to the eye tracker:
    if n_trials_done == 0:
        # - Update the instruction screen text...
        instr_text_stim.setText(instr_text)
        instr_text_stim.draw()
        flip_time = window.flip()

        # wait until a space key event occurs after the instructions are displayed
        event.waitKeys(' ')

    n_trials_done += 1
    print('\n======TRIAL#' + str(n_trials_done) + '======')

    ## Assigning the trial variables:

    # Token variables:
    resp_interval_given = False
    resp_number_given = False
    resp_ori_given = False
    resp_conf_given = False

    # Randomizing whether the stimuli will appear in the first or second interval:
    stim_interval_second = np.random.randint(2)  # 0 if 1st and 1 if 2nd - used in the loop check (BOOL is faster)
    stim_interval = stim_interval_second + 1  # adding 1 to record

    # Timing variables.

    # Stimulus onset asynchrony, in frames: must be greater than stimulus duration:
    if debug:
        soa = stim_dur + 10
    else:
        soa = trial['SOA']
        if shocky:
            soa = soa / 2
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

    # Stimulus contrast:
    stim1_c = trial['stim1_c']  # stimulus contrast, log scaled
    stim1.contrast = 10 ** stim1_c
    stim2_c = trial['stim2_c']
    stim2.contrast = 10 ** stim2_c

    # Stimulus orientation:
    angle_diff = trial['angle_diff']  # difference in orientation between stimuli (binary): 0 if same, 1 if diff
    stim1_tiltR = np.random.randint(2)  # 0 if leftward and 1 if rightward tilted
    if stim1_tiltR:
        stim1_ori = 'R'
    else:
        stim1_ori = 'L'
    stim1.ori = 135 - (90 * stim1_tiltR)  # 135 deg if leftward and 45 deg if rightward; checked 2019-05-15
    if not angle_diff:
        stim2_tiltR = stim1_tiltR
        stim2_ori = stim1_ori
    else:
        stim2_tiltR = 1 - stim1_tiltR
        if stim1_tiltR:
            stim2_ori = 'L'
        else:
            stim2_ori = 'R'
    stim2.ori = 135 - (90 * stim2_tiltR)  # the opposite of the first

    # Print trial specifics to screen:
    print('interval=' + str(stim_interval) + ' soa=' + str(int(soa)) + ' diff=' + str(angle_diff) +
          ' c1=' + str(stim1_c) + ' c2=' + str(stim2_c))

    ## Presentation phase

    # Iterating through the intervals:
    fix_frames = int(fix_dur)
    interval_frames = int(interval_dur)
    for cur_interval in [0, 1]:

        # Fixation:
        for cur_fix_frame in range(fix_frames):
            flip_time = frame_routine()
            fix_cross.draw()
            if debug:
                print('|', end='')

        # Iterating through interval frames:
        for cur_frame in range(interval_frames):
            flip_time = frame_routine()
            box.draw()

            # stimulus presentation
            if cur_interval == stim_interval_second:

                # first stimulus time window:
                if cur_frame in stim1_twin:
                    if debug:
                        print('/', end='')
                    # draw the first stimulus
                    stim1.draw()
                # second stimulus time window (may overlap with the first):
                elif cur_frame in stim2_twin:
                    if debug:
                        print('\\', end='')
                    # draw the second stimulus
                    stim2.draw()
                else:
                    if debug:
                        print('-', end='')
            else:
                if debug:
                    print('-', end='')
        if debug:
            print('\n', end='')

    ## Response phase:

    # Interval response:
    while not resp_interval_given:

        window.flip()
        instr_text_stim.setText('1st or 2nd interval?')
        instr_text_stim.draw()

        ## Monitoring for key presses:
        num_keys = event.getKeys(keyList=['1', '2', 'escape'])
        if len(num_keys) > 0:
            if '1' in num_keys:
                print('interval response: first')
                resp_interval = 1
                resp_interval_given = True
            elif '2' in num_keys:
                print('interval response: second')
                resp_interval = 2
                resp_interval_given = True
            elif 'escape' in num_keys:
                exit_routine()

    # Stimulus number response:
    while not resp_number_given:

        window.flip()
        instr_text_stim.setText('1 or 2 stimuli?')
        instr_text_stim.draw()

        ## Monitoring for key presses:
        num_keys = event.getKeys(keyList=['1', '2', 'escape'])
        if len(num_keys) > 0:
            if '1' in num_keys:
                print('stimulus number response: single')
                resp_number = 1
                resp_number_given = True
            elif '2' in num_keys:
                print('stimulus number response: double')
                resp_number = 2
                resp_number_given = True
            elif 'escape' in num_keys:
                exit_routine()

    # Orientation response:
    while not resp_ori_given:

        window.flip()
        instr_text_stim.setText('Stimulus pattern?\n'
                                'Left = leftward tilt\n'
                                'Right = rightward tilt\n'
                                'Down = both')
        instr_text_stim.draw()

        ## Monitoring for key presses:
        arrow_keys = event.getKeys(keyList=['left', 'right', 'down', 'escape'])
        if len(arrow_keys) > 0:
            if 'left' in arrow_keys:
                print('orientation response: leftward tilt')
                resp_ori = 'L'
                resp_ori_given = True
            elif 'right' in arrow_keys:
                print('orientation response: rightward tilt')
                resp_ori = 'R'
                resp_ori_given = True
            elif 'down' in arrow_keys:
                print('orientation response: plaid')
                resp_ori = 'P'
                resp_ori_given = True
            elif 'escape' in num_keys:
                exit_routine()

    # Confidence response:
    while not resp_conf_given:

        window.flip()
        instr_text_stim.setText('How confident are you\n'
                                'in your responses?\n'
                                '1 = not at all\n'
                                '2 = somewhat\n'
                                '3 = confident')
        instr_text_stim.draw()

        ## Monitoring for key presses:
        num_keys = event.getKeys(keyList=['1', '2', '3', 'escape'])
        if len(num_keys) > 0:
            if '1' in num_keys:
                print('confidence response: 1')
                resp_conf = 1
                resp_conf_given = True
            elif '2' in num_keys:
                print('confidence response: 2')
                resp_conf = 2
                resp_conf_given = True
            elif '3' in num_keys:
                print('confidence response: 3')
                resp_conf = 3
                resp_conf_given = True
            elif 'escape' in num_keys:
                exit_routine()

    ## Trial termination feedback:
    window.flip()
    instr_text_stim.setText('Press the spacebar to continue')
    instr_text_stim.draw()
    window.flip()

    # wait until a space key event occurs after the instructions are displayed
    event.waitKeys(' ')

    flip_time = window.flip()

    ## Recording the data
    output_mat[n_trials_done - 1] = {'exp_name': exp_name, 'frame_rate': frame_rate, 'stim_dur': stim_dur,
                                     'beg_buff': beg_buff, 'end_buff': end_buff, 'wiggle': wiggle,
                                     'subj': exp_info['subj'], 'sess': exp_info['sess'],
                                     'block': exp_info['block'], 'trial_id': n_trials_done,
                                     'soa': soa, 'angle_diff': angle_diff,
                                     'stim1_ori': stim1_ori, 'stim2_ori': stim2_ori,
                                     'stim1_c': stim1_c, 'stim2_c': stim2_c,
                                     'stim_interval': stim_interval, 'jitter': jitter,
                                     'resp_interval': resp_interval, 'resp_number': resp_number, 'resp_ori': resp_ori,
                                     'resp_conf': resp_conf}

# Finishing the experiment
exit_routine()
