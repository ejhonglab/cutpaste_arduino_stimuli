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

import pandas as pd


def main():
    # TODO should i also spit out pins for PID here?
    orig_df = pd.read_csv('natural_odor_pair_panel.csv')

    # TODO first print anything duplicated (the different reasons...)
    df = orig_df.drop_duplicates(subset=['odor_1','odor_2'])

    available_pins = list(range(2, 11))

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

    pins2odors = dict(zip(available_pins, odors))
    odors2pins = dict(zip(odors, available_pins))

    n_repeats = 3

    odor_pair_list = []
    for block_num, pair in enumerate(df.sample(frac=1).itertuples()):
        comparison_block_odors = [
            (pair.odor_1, 'paraffin'),
            (pair.odor_2, 'paraffin'),
            (pair.odor_1, pair.odor_2)
        ] * n_repeats

        random.shuffle(comparison_block_odors)
        odor_pair_list += comparison_block_odors

    pin_pair_list = [(odors2pins[o1], odors2pins[o2])
                     for o1, o2 in odor_pair_list]
    #pp.pprint(pin_pair_list)

    print('\nPins to odors:')
    for p in sorted(pins2odors.keys()):
        print(' {}: {}'.format(p, pins2odors[p]))

    def print_as_array(pin_list):
        # spaces between blocks?
        # break into lines of 80 characters?
        print('{'+','.join([str(p) for p in pin_list])+'};')

    channel_a = [a for a, _ in pin_pair_list]
    channel_b = [b for _, b in pin_pair_list]

    print('\nCopy to channel A:')
    print_as_array(channel_a)
    print('\nCopy to channel B:')
    print_as_array(channel_b)
    
    pickle_name = time.strftime('%Y%m%d_%H%M%S') + '_stimuli.p'
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


if __name__ == '__main__':
    main()
