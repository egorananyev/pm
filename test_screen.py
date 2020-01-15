####!/usr/bin/arch -i386 /usr/bin/python # -*- coding: utf-8 -*-
from __future__ import print_function

"""
Investigating facilitative and suppressive interactions between stimuli.
Creator: Egor Ananyev
Original date: 2019-05-07
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, event, gui

window = visual.Window(fullscr=True, monitor='station3', color=[-.5, -.5, -.5], units='pix',
                       allowStencil=True, autoLog=False, screen=0, waitBlanking=False)

# box = visual.Rect(window, width=5, height=5, lineColor='white')
wid_val = 1000
hei_val = 800
pos_val = [0, -110]
box = visual.Rect(window, width=wid_val, height=hei_val, lineColor='white', fillColor='gray', units='pix',
                  pos=pos_val)
box_text = visual.TextStim(window, units='pix', pos=pos_val, text=str(wid_val) + ' x ' + str(hei_val))

wid_val2 = 1000
hei_val2 = 630
pos_val2 = [0, -25]
box2 = visual.Rect(window, width=wid_val2, height=hei_val2, lineColor='white', fillColor='black', units='pix',
                  pos=pos_val2, opacity=0.3)
box_text2 = visual.TextStim(window, units='pix', pos=pos_val2, text=str(wid_val2) + ' x ' + str(hei_val2),
                            color='grey')

while 1:
    # Monitoring for key presses:
    arrow_keys_ = event.getKeys(keyList=['escape'])

    if len(arrow_keys_) > 0:
        if 'escape' in arrow_keys_:
            window.close()
            core.quit()

    window.flip()
    box.draw()
    box2.draw()
    box_text.draw()
    box_text2.draw()
