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
# is Cedrus present?
cedrus = False
# experiment variables:
exp_name = 'meg1'

if cedrus:
    import pyxid
    devices = pyxid.get_xid_devices()
    dev = devices[0]  # get the first device to use
    print(dev)
    dev.reset_base_timer()
    dev.reset_rt_timer()

    if dev.is_response_device():
        while not dev.has_response():
            dev.poll_for_response()

        response = dev.get_next_response()
        print(response)
        dev.clear_response_queue()

    dev.set_pulse_duration(300)

    sleep_flash = .3
    # import time
    for bm in range(0, 16):
        mask = 2 ** bm
        print("activate_line bitmask: ", mask)
        #dev.activate_line(lines=[1,3,5,7,9,11,13,15])
        dev.activate_line(bitmask=mask)

        # time.sleep(sleep_flash)

## Monitor specification with *whole* monitor dimensions:
# ds_mm = 1410
# dr_px = (1920, 1080)  # display resolution in px
# dd_mm = (864, 471.4)
screen_name = 'meg60Hz'
full_screen = True
# Initiating the screen:
background = [-.0, -.0, -.0]  # unless I'm willing  to mess with the stim lum range, keep this gray
window = visual.Window(fullscr=full_screen, monitor=screen_name, color=background, units='deg',
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
center_y_off_px = 25

## Stimulus parameters:
annulus_in_dva = 1
annulus_out_dva = 10
stim_sf_cpd = 1  # cycles per degree
# Initiating the stimulus:
stim = visual.GratingStim(window, size=annulus_out_dva, tex='sin', mask='circle', pos=(0, center_y_off_dva),
                          sf=stim_sf_cpd)
annulus_in_circle = visual.Circle(window, radius=annulus_in_dva/2, pos=(0, center_y_off_dva), fillColor=background,
                                  lineColor=background)

## Fixation cross:
fix_cross_sz_dva = 1  # the diameter of the gross
fix_cross = visual.TextStim(window, text='+', bold='True', pos=[0, center_y_off_dva], color='black',
                            height=fix_cross_sz_dva)

## Light sensor stimulus:
light_sensor_off_x = 505
light_sensor_background = visual.Circle(window, radius=20, pos=(light_sensor_off_x, center_y_off_px),
                                        fillColor='black', lineColor=background, units='pix')
light_sensor_stim = visual.Circle(window, radius=11, pos=(light_sensor_off_x, center_y_off_px), fillColor='white',
                                  lineColor=background, units='pix')  # 11 px ~ 5 mm ~ 0.2015 dva

## Timing variables (note that the number of frames will differ for 60 and 100 Hz refresh rates):
fix_dur_fr = 2  # in frames
prestim_t_min_ms = 300  # in milliseconds
prestim_t_max_ms = 500
poststim_t_ms = 600
poststim_t_fr = int(np.round(frame_rate * poststim_t_ms / 1000))
num_blocks = 6  # the number of blocks for non-training runs
blink_every_x_trials_min = 3
blink_every_x_trials_max = 5

## Getting info on the run through GUI:
exp_info = {u'subj': u'0', u'run': u'0'}  # run==0 is training run
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)  # dialogue box
if not dlg.OK:
    core.quit()  # user pressed cancel
exp_info['time'] = datetime.now().strftime('%Y-%m-%d_%H%M')
run = exp_info['run']

## Assigning conditions:
print('run ' + exp_info['run'])
if run == '0':
    train = True
    num_blocks = 1
else:
    train = False

## Input and output

# Condition file:
exp_conditions = 'cond-files/cond_' + exp_name + '.xlsx'

# Trial handler depending on the measure or experimental stage:
# Note: trials are reset for every block before every trial loop (below)

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
run_dir = subj_dir + os.sep + 'run-%s_%s' % (exp_info['run'], exp_info['time'])
if not os.path.exists(run_dir):
    os.makedirs(run_dir)
out_file_path = run_dir + os.sep + 'beh_out.csv'

# Output matrix:
output_mat = {}

# Handling condition instructions:
instr_text = 'Blink when the cross turns white'
instr_text_stim = visual.TextStim(window, text=instr_text, height=.6, pos=[0, center_y_off_dva])

## Handy routines:

# Timestamp routine
def cur_ts():
    return datetime.now().strftime('%H%M%S%f')

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
    annulus_in_circle.draw()
    fix_cross.draw()
    light_sensor_background.draw()
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
        print('\n==================='
              '\nthe output file is empty')
    else:
        data_columns = ['exp_name', 'frame_rate', 'subj', 'run', 'block', 'trial_id', 'block_trial_id',
                        'trial_beg_ts', 'prestim_t_ms', 'prestim_t_fr', 'blink_trial',  # prestim; "ts"=timestamp
                        'stim_on_ts', 'stim_ori', 'stim_c', 'stim_phase', 'stim_dur_fr', 'stim_off_ts',  # stim info
                        'trial_end_ts']
        pd.DataFrame.from_dict(output_mat, orient='index').to_csv(out_file_path, index=False, columns=data_columns)
        print('\noutput file path is ' + out_file_path)

    # Close the graphics
    window.close()
    core.quit()

## Initiate with the instruction screen:
# instr_text_stim.setText(instr_text)
instr_text_stim.draw()
flip_time = window.flip()
# Wait until a space key event occurs after the instructions are displayed:
event.waitKeys(' ')

## Initiating the trial loop

tot_trials_done = 0
no_blink_trials_count = 0
cur_blink_trial = blink_every_x_trials_min  # at first, the number of no-blink trials is minimal, but random thereafter
blink_trial = False

for block in range(num_blocks):

    # Resetting the trials for every block of trials:
    trials = pd.read_excel(exp_conditions)
    block_trials_done = 0

    while len(trials > 0):

        block_trials_done += 1
        no_blink_trials_count += 1
        tot_trials_done += 1
        print('\n======TRIAL#' + str(tot_trials_done) + '======')

        ## Deciding on the number of no-blink trials for the control task:
        if no_blink_trials_count >= cur_blink_trial:
            blink_trial = True
            no_blink_trials_count = 0
            cur_blink_trial = np.random.randint(low=blink_every_x_trials_min, high=blink_every_x_trials_max)
        else:
            blink_trial = False

        ## Randomly picking the current trial row, assigning it to 'trial' var, and dropping it from 'trials':
        cur_trial_indx = int(np.random.choice(trials.index.values, 1))
        trial = trials.ix[cur_trial_indx].copy()  # an explicit copy() is necessary due to a warning otherwise
        trials = trials.drop([cur_trial_indx])
        drop_trial = False

        ## Stimulus variables:

        # Randomizing whether the stimulus phase:
        stim_phase = np.random.rand(1)[0]  # phase=1 means one whole cycle; random of [0 to 1] is random phase
        stim.phase = stim_phase

        # Stimulus contrast / opacity:
        stim_c = trial['stim_c']  # stimulus contrast
        stim.contrast = stim_c * 0.01

        # Stimulus orientation:
        stim_ori = trial['stim_ori']
        stim.ori = stim_ori_angle(stim_ori)

        # Stimulus duration:
        stim_dur_fr = trial['stim_dur']

        ## Timing variables.

        # Randomizing the onset:
        prestim_t_ms = np.random.randint(low=prestim_t_min_ms, high=prestim_t_max_ms)

        ## Print trial specifics to screen:
        print('ori=' + str(stim_ori) + ' c=' + str(stim_c) + ' dur=' + str(stim_dur_fr) +
              ' phase=' + str(stim_phase) + ' prestim=' + str(prestim_t_ms), ' blink=', str(blink_trial))

        ## Pre-stimulus phase:
        trial_beg_ts = cur_ts()  # time stamp
        prestim_t_fr = int(np.round(frame_rate * prestim_t_ms / 1000))
        if blink_trial:
            fix_cross.color = 'white'
        for cur_frame in range(prestim_t_fr):
            flip_time = frame_routine()

        ## Presentation phase
        stim_on_ts = cur_ts()
        # Iterating through frames:
        for cur_frame in range(stim_dur_fr):
            # Writing out the frame routine here since the fixation stuff needs to appear on top of stim
            flip_time = window.flip()
            # Drawing the stimulus:
            stim.draw()
            # The said fixation stuff:
            annulus_in_circle.draw()
            fix_cross.draw()
            # Visual event marker for Cedrus:
            light_sensor_background.draw()
            light_sensor_stim.draw()

        ## Post-stimulus fixation phase:
        stim_off_ts = cur_ts()
        if blink_trial:
            fix_cross.color = 'black'
        for cur_frame in range(poststim_t_fr):
            flip_time = frame_routine()

        trial_end_ts = cur_ts()  # time stamp

        ## Recording the data
        output_mat[tot_trials_done - 1] = {'exp_name': exp_name, 'datetime': exp_info['time'], 'frame_rate': frame_rate,
                                           'subj': exp_info['subj'], 'run': run, 'block': block+1,
                                           'trial_id': tot_trials_done, 'block_trial_id': block_trials_done,
                                           'trial_beg_ts': trial_beg_ts, 'prestim_t_ms': prestim_t_ms,
                                           'prestim_t_fr': prestim_t_fr, 'blink_trial': int(blink_trial),
                                           'stim_on_ts': stim_on_ts, 'stim_ori': stim_ori,
                                           'stim_c': stim_c, 'stim_phase': stim_phase,
                                           'stim_dur_fr': stim_dur_fr, 'stim_off_ts': stim_off_ts,
                                           'trial_end_ts': trial_end_ts}

# Finishing the experiment
exit_routine()
