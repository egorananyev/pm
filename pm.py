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
from subprocess import call  # for running shell commands from within Python
from psychopy.data import TrialHandler, importConditions
import pandas as pd
from datetime import datetime

## Initial variables.
# experiment modes:
shocky = True
# experiment variables:
exp_name = 'pm1'
# timing variables:
fix_dur = 200  # in ms
stim_dur = 20
beg_buff = 100  # beginning buffer of fixation
end_buff = beg_buff
wiggle = 100  # additional 'wiggle room' for jittering of stimulus onset
# interval duration includes two stimulus time windows to make the intervals consistent even if SOA=0:
interval_dur = stim_dur * 2 + beg_buff + end_buff + wiggle
# trial duration:
trial_dur = fix_dur + interval_dur * 2

if shocky:
    ds = 61
    # dd = (17.2, 12.9)  # display dimensions in cm
    dr = (1152, 864)  # display resolution in px
    dd = (34.4, 25.8)  # display dimensions in cm
    windowed = True
else:
    dr = (1152, 864)  # display resolution in px
    ds = 65  # distance to screen in cm
    dd = (40.0, 30.0)  # display dimensions in cm ... 39.0 x 29.5
    windowed = False
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
    mon = monitors.Monitor('Shocky', width=dd[0], distance=ds)
    mon.setSizePix(dr)
    window = visual.Window(dr, monitor=mon, fullscr=False, screen=1, units='deg')
else:
    # TODO make sure that 'station3' monitor profile exists and is properly configured
    mon = monitors.Monitor('station3')
    window = visual.Window(dr, fullscr=True, monitor=mon, color=[-.5, -.5, -.5], units='deg',
                           allowStencil=True, autoLog=False, screen=0, waitBlanking=False)

if shocky:
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
stim1 = visual.Circle(window, radius=stim_diam / 2, edges=32, pos=(10, 0), fillColor='grey')


## Handy routines:

# Frame-skipping check:
def frame_skip_check(elapsed_t, elapsed_frames):
    # The number of elapsed frames should match the time:
    print('time=%.3f  frames=%d  rate=%.4f' % (elapsed_t, elapsed_frames, (elapsed_t / elapsed_frames)))


# This is done at every frame update, regardless of trial phase, so predefining:
def frame_routine():
    flip_time_ = window.flip()
    fix_cross.draw()
    # Checking for quit (the Esc key)
    if event.getKeys(keyList=['escape']):
        exit_routine()
    return flip_time_


# Also no variation across frames, but only available upon call, which is made only in key registering phase.
def exit_routine():

    # Behavioural data output:
    if not output_mat:  # means that the dictionary is empty
        print('the output file is empty')
    else:
        # TODO fill in stim info and subject's response
        data_columns = ['exp_name', 'subj', 'block', 'trial_id']  # log info # stim info # subj resp
        pd.DataFrame.from_dict(output_mat, orient='index').to_csv(out_file_path, index=False, columns=data_columns)
        print('output file path is ' + out_file_path)

    # Say goodbye:
    window.flip()
    instr_text_stim.setText('    Finished!\nRecording data...')
    instr_text_stim.draw()
    window.flip()


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
    print('======TRIAL#' + str(n_trials_done) + '======')

    ## Randomizing variables and assigning the conditions:

    # Randomization:
    stim_interval_second = np.random.randint(2)  # 0 if 1st and 1 if 2nd - used in the loop check (BOOL is faster)
    stim_interval = stim_interval_second + 1  # adding 1 to record
         # timing jitter

    # Timing variables:
    # time for first stimulus onset, in ms;
    jitter = np.floor(0.1 * (np.random.randint(wiggle) + 1)) * 10
    stim1_onset
    stim1_twin  # stimulus time window (evaluated against flip_time to yield stimulus ON frames
    stim2_twin

    # Setting stimulus characteristics:
    stim1_c = trial['stim1_c']  # stimulus contrast
    #...

    ## Presentation phase

    # First interval:
    interval_frames = int(interval_dur * frame_rate)
    for cur_frame in interval_frames:
        flip_time = frame_routine()

        if not stim_interval_second:
            # stimulus presentation

            # first stimulus time window:
            if cur_frame in stim1_twin:
                # draw the first stimulus
                stim1.draw()

            # second stimulus time window (may overlap with the first):
            if cur_frame in stim2_twin:
                # draw the second stimulus
                stim2.draw()

    ## Response phase:

   # The location/blink cue:
    tracker.sendMessage('CUE_ONSET %.2f' % flip_time)
    cue_frames = int(cue_dur * frame_rate)
    for cue_frame in range(cue_frames):
        flip_time = frame_routine()
        if not measure:
            cue_arrow.draw()
        else:
            double_arrow.draw()
        if debug:
            # noinspection PyUnboundLocalVariable
            trial_elapsed_frames += 1

    # Blink latency = the fixation period after the cue:
    tracker.sendMessage('BLINK_LATENCY_ONSET %.2f' % flip_time)
    blink_latency_frames = int(blink_latency * frame_rate)
    for blink_latency_frame in range(blink_latency_frames):
        flip_time = frame_routine()
        if debug:
            # noinspection PyUnboundLocalVariable
            trial_elapsed_frames += 1

    # Real or simulated blink follow the same timeline:
    blink_time_period_frames = int(blink_time_window * frame_rate)
    tracker.sendMessage('BLINK_WINDOW_ONSET %.2f' % flip_time)
    if shutters:
        # noinspection PyUnboundLocalVariable
        shutter_frames = int(shutter_dur * frame_rate)
        tracker.sendMessage('SHUTTER_START %.2f' % flip_time)
        # noinspection PyUnboundLocalVariable
        ser.write('z')
        shutters_shut = True
        print('Closed the goggles.')
    for blink_time_period_frame in range(blink_time_period_frames):
        flip_time = frame_routine()
        if debug:
            # noinspection PyUnboundLocalVariable
            trial_elapsed_frames += 1
        if shutters:
            # noinspection PyUnboundLocalVariable
            if shutters_shut:
                # noinspection PyUnboundLocalVariable
                if blink_time_period_frame > shutter_frames:
                    tracker.sendMessage('SHUTTER_END %.2f' % flip_time)
                    ser.write('c')
                    shutters_shut = False
                    print('Opened the goggles.')

    ## Behavioural response: measuring the reaction time:

    tracker.sendMessage('RESPONSE_ONSET %.2f' % flip_time)
    if not measure:
        # Trial components pertaining to behavioural response:
        targ_resp_given = False
        rt_start = flip_time

        # Displaying the target and measuring the reaction time.
        while not targ_resp_given:

            # Measuring the time it takes for the behavioural response:
            flip_time = frame_routine()

            # Measuring time elapsed since the start of the trial:
            trial_elapsed_t = flip_time - trial_t_start

            # Drawing the target:
            targ.draw()

            if debug:
                # noinspection PyUnboundLocalVariable
                trial_elapsed_frames += 1

            ## Monitoring for key presses:
            arrow_keys = event.getKeys(keyList=['left', 'right'])
            if len(arrow_keys) > 0:
                if 'left' in arrow_keys:
                    print('subject response: Left')
                    beh_resp = -1
                    targ_resp_given = True
                else:
                    print('subject response: Right')
                    beh_resp = 1
                    targ_resp_given = True
                if targ_resp_given:  # this is overwritten every time any key is pressed
                    rt = flip_time - rt_start
                    # noinspection PyUnboundLocalVariable
                    if beh_resp == this_targ_loc:
                        corr_resp = 1  # correct location response
                        accuracy_feedback = 'Correct!'
                    else:
                        corr_resp = 0  # incorrect location response
                        accuracy_feedback = 'INCORRECT!'
                    print('RT=%.2f correct?=%s' % (rt, corr_resp))
                    tracker.sendMessage('TRIAL_RESPONSE %.2f' % flip_time)
                    if debug:  # in debug mode, check if the frame rate looks okay
                        # noinspection PyUnboundLocalVariable
                        frame_skip_check(trial_elapsed_t, trial_elapsed_frames)

    ## Post-trial RT and accuracy
    print('post-trial phase')
    window.flip()
    if not measure:
        # noinspection PyUnboundLocalVariable
        instr_text_stim.setText('Target Location: ' + accuracy_feedback +
                                '\nReaction Time: %.2f' % rt +
                                '\n\nPress the spacebar to continue')
    else:
        instr_text_stim.setText('Press the spacebar to continue')
    instr_text_stim.draw()
    window.flip()

    # wait until a space key event occurs after the instructions are displayed
    event.waitKeys(' ')

    flip_time = window.flip()
    tracker.sendMessage('TRIAL_END %.2f' % flip_time)

    ## Recording the data
    # noinspection PyUnboundLocalVariable
    if not measure:
        # noinspection PyUnboundLocalVariable
        output_mat[n_trials_done - 1] = {'exp_name': exp_name,
                                         'subj': exp_info['subj'],
                                         'cond': exp_info['cond'],
                                         'sess': exp_info['sess'],
                                         'trial_id': n_trials_done,
                                         'cue_delay': cue_delay,
                                         'targ_right': trial['targ_right'],
                                         'cue_valid': trial['cue_valid'],
                                         'blink_latency': blink_latency,
                                         'shutter_dur': shutter_dur,
                                         'trial_start': trial_t_start,
                                         'trial_end': flip_time,
                                         'corr_resp': corr_resp,
                                         'rt': rt}
    else:
        output_mat[n_trials_done - 1] = {'exp_name': exp_name,
                                         'subj': exp_info['subj'],
                                         'cond': exp_info['cond'],
                                         'sess': exp_info['sess'],
                                         'trial_id': n_trials_done,
                                         'cue_delay': cue_delay,
                                         'trial_start': trial_t_start,
                                         'trial_end': flip_time}

    ## Stopping the eye tracking
    # send trial variables for Data Viewer integration
    # [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
    tracker.sendMessage('!V TRIAL_VAR task %s' % cond_str)

    # send a message to mark the end of trial
    # [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
    tracker.sendMessage('TRIAL_RESULT')
    pylink.pumpDelay(100)
    tracker.stopRecording()

# Finishing the experiment
exit_routine()
