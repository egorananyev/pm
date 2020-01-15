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
debug = True
# experiment variables:
exp_name = 'meg1'

## Monitor specification with *whole* monitor dimensions:
# ds_mm = 1410
# dr_px = (1920, 1080)  # display resolution in px
# dd_mm = (864, 471.4)  # office Samsung monitor
screen_name = 'meg60Hz'
full_screen = True
# Initiating the screen:
window = visual.Window(fullscr=full_screen, monitor=screen_name, color=[-.5, -.5, -.5], units='deg',
                       allowStencil=True, autoLog=False, screen=0, waitBlanking=False)
if debug:
    frame_rate = window.getActualFrameRate()
else:
    frame_rate = 60
print('frame rate: ' + str(frame_rate))

## Visible area description:
# visible_px = (1000, 630)
# visible_mm = (450, 275)
# visible_dva = (18.133, 11.1395)
# viewing_distance_mm = 1410
center_y_off_dva = -0.4571  # 25 px
# Stimulus:
box = visual.Rect(window, width=5, height=5, lineColor='white')

## Stimulus parameters:
annulus_in_dva = 1
annulus_out_dva = 10
stim_sf_cpd = 1  # cycles per degree
# Initiating the stimulus:
stim = visual.GratingStim(window, size=annulus_out_dva, tex='sin', mask='gauss', pos=(0, center_y_off_dva),
                          sf=stim_sf_cpd)

## Fixation cross:
fix_cross_sz_dva = 0.5  # the diameter of the gross
fix_cross = visual.TextStim(window, text='+', bold='True', pos=[0, 0], rgb=1, height=fix_cross_sz_dva)

## Timing variables (note that the number of frames will differ for 60 and 100 Hz refresh rates):
fix_dur_fr = 2  # in frames
prestim_t_min_s = .300  # in seconds
prestim_t_max_s = .500
poststim_t_s = .600
stim_dur_fr = 1


## Getting info on the run through GUI:
exp_info = {u'subj': u'0000', u'block': u'0'}  # block==0 is training block
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)  # dialogue box
if not dlg.OK:
    core.quit()  # user pressed cancel
exp_info['time'] = datetime.now().strftime('%Y-%m-%d_%H%M')

## Assigning conditions:
print('Block: ' + exp_info['block'])
if exp_info['block'] == '0':
    train = True
else:
    train = False

## Input and output

# Condition file:
exp_conditions = 'cond-files/cond_' + exp_name + '.xlsx'

# Trial handler depending on the measure or experimental stage:
# trials = pd.read_excel('C:\Users\egora\Dropbox\Projects\pm\pm\cond-files\cond_pm1_train.xlsx')
trials = pd.read_excel(exp_conditions)

# Output file:
exp_dir = '..' + os.sep + 'data' + os.sep + exp_name
if not os.path.exists(exp_dir):
    print('experiment directory does not exist - making')
    os.makedirs(exp_dir)
else:
    print('experiment directory exists')
subj_dir = exp_dir + os.sep + 'subj-%04d' % int(exp_info['subj'])
if not os.path.exists(subj_dir):
    os.makedirs(subj_dir)
block_dir = subj_dir + os.sep + 'block-%s_%s' % (exp_info['block'], exp_info['time'])
if not os.path.exists(block_dir):
    os.makedirs(block_dir)
out_file_path = block_dir + os.sep + 'beh_out.csv'

# Output matrix:
output_mat = {}

# Handling condition instructions:
instr_text = 'Please blink when you see a cross in the middle.'
instr_text_stim = visual.TextStim(window, text=instr_text, height=.6, pos=[0, 0])

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
