#!/usr/bin/env python3

"""
Generates a list of pins to paste into the Arduino sketch and instructions on
which odors to connect downstream of which pins.
"""

from __future__ import print_function
from __future__ import division

import random
import pprint as pp
import time
import pickle
import warnings

import pandas as pd


def main():
    # TODO should i also spit out pins for PID here?
    orig_df = pd.read_csv('natural_odor_pair_panel.csv')

    # TODO first print anything duplicated (the different reasons...)
    df = orig_df.drop_duplicates(subset=['odor_1','odor_2'])

    # TODO probably delete this hack after building in appropriate caching
    # Set to None (not a string) to generate odor to pin mappings.
    use_odors2pins_from = '20190117_104846_stimuli.p'
    save_stimuli_data = True
    
    if use_odors2pins_from is None:
        available_pins = list(range(2, 12))
        available_pins.remove(7)
        print('Available pins: {}\n'.format(available_pins))
        
        # TODO pins 2 Remy's vial position labels / randomize
    
        odors = list(set(df.odor_1) | set(df.odor_2))
    
        # To divide flow when odors are presented individually, so that the
        # components are equally intense in the mixture.
        odors.append('paraffin')
    
        if len(odors) > len(available_pins):
            # TODO break into groups less than or equal to # of olfactometer
            # channels (pins)
            raise NotImplementedError
    
        random.shuffle(available_pins)
        random.shuffle(odors)
    
        # TODO TODO option to cache these, as written several times before...
        pins2odors = dict(zip(available_pins, odors))
        odors2pins = dict(zip(odors, available_pins))
    
    else:
        print('Using pin to odor mapping from: {}'.format(
            use_odors2pins_from))
        
        with open(use_odors2pins_from, 'rb') as f:
            old_stim_data = pickle.load(f)

        available_pins = old_stim_data['available_pins']
        odors = old_stim_data['odors']        
        pins2odors = old_stim_data['pins2odors']
        odors2pins = old_stim_data['odors2pins']

    n_repeats = 3

    # TODO TODO probably work in some presentations of paraffin by itself
    odor_pair_list = []
    for block_num, pair in enumerate(df.sample(frac=1).itertuples()):
        comparison_block_odors = [
            (pair.odor_1, 'paraffin'),
            (pair.odor_2, 'paraffin'),
            (pair.odor_1, pair.odor_2)
        ] * n_repeats

        random.shuffle(comparison_block_odors)
        odor_pair_list += comparison_block_odors
        
    presentations_per_comparison_block = len(comparison_block_odors)

    pin_pair_list = [(odors2pins[o1], odors2pins[o2])
                     for o1, o2 in odor_pair_list]
    
    sec_per_trial = 60.0
    print('Number of trials: {}'.format(len(pin_pair_list)))
    print('Will take {} minutes'.format(len(pin_pair_list) * (sec_per_trial / 60.0)))
    #pp.pprint(pin_pair_list)

    print('\nPins to odors:')
    for p in sorted(pins2odors.keys()):
        print(' {}: {}'.format(p, pins2odors[p]))

    def print_as_array(pin_list):
        # spaces between blocks?
        # break into lines of 80 characters?
        
        s = ' {'
        pin_separator = ','
        block_separator = '\n '
        for n, p in enumerate(pin_list):
            if n % presentations_per_comparison_block == 0:
                s += block_separator
            s += str(p) + pin_separator
        s = s[:-(len(pin_separator))]
        s += '\n};\n'
        print(s)

    channel_a = [a for a, _ in pin_pair_list]
    channel_b = [b for _, b in pin_pair_list]

    # TODO just take variable name as arg and get rid of prints
    print('\nCopy to Arduino script, replacing existing:')
    print('const int channelA[] = ', end='')
    print_as_array(channel_a)
    print('const int channelB[] = ', end='')
    print_as_array(channel_b)
    
    if save_stimuli_data:
        pickle_name = time.strftime('%Y%m%d_%H%M%S') + '_stimuli.p'
        # TODO print full path
        print('\nSaving stimulus data to {}'.format(pickle_name))
        with open(pickle_name, 'wb') as f:
            data = {
                'pins2odors': pins2odors,
                'odors2pins': odors2pins,
                'odor_pair_list': odor_pair_list,
                'pin_pair_list': pin_pair_list,
                'available_pins': available_pins,
                'n_repeats': n_repeats,
                'odors': odors,
                'odor_pair_df': orig_df
            }
            pickle.dump(data, f)
    
        # TODO upload to database rather / in addition to pickle?
        
    else:
        warnings.warn('Not saving stimuli! Only use this mode for testing.')


if __name__ == '__main__':
    main()
