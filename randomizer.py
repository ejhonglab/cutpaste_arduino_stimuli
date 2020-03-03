#!/usr/bin/env python3

"""
Generates a list of pins to paste into the Arduino sketch and instructions on
which odors to connect downstream of which pins.
"""

from __future__ import print_function
from __future__ import division

from os.path import abspath
import random
import time
import pickle
import warnings


def trial_structure(blocks_without_repeats=None, use_odors2pins_from=None,
    keep_saved_order=False, save_stimuli_data=True,
    extra_pickle_fname_part=None, n_repeats=3,
    randomize_within='within_repeat', available_pins=None, exclude_pins=(7,),
    start_pin=2, stop_pin=11, hardcoded_pins2odors=None, extra_data=None):
    """
    Args:
    blocks_without_repeats (list of lists): Each contained list is one repeat of
        an unrandomized block. Those lists contain hashable (e.g. str) odor
        descriptions.
        
    keep_saved_order (bool, default=False): Set this to True to just print the
        trial structure saved in use_odors2pins_from, without generating a new
        order.

    randomize_within (str, default='within_repeat'):
        'within_repeat': Within each of the n_repeats.
            An odor will never occur more than twice in succession.
        'across_repeats': n_repeats of each of block are permuted. In this case,
            any odor could ocasionally occur n_repeats times in succession.

    extra_data (dict): extra data to be pickled alongside trial structure.
    """
    if keep_saved_order:
        if blocks_without_repeats is None:
            raise ValueError('must pass blocks_without_repeats if ' +
                'not using saved order')

        if use_odors2pins_from is None:
            raise ValueError('must pass use_odors2pins_from if ' +
                'not using saved order')

    # TODO option to randomize across all repeats and blocks?
    if randomize_within not in {'across_repeats', 'within_repeat'}:
        raise ValueError('invalid value for randomize_within')
    if randomize_within == 'across_repeats':
        print('Shuffling across repeats, but within each block.')
    elif randomize_within == 'within_repeat':
        print('Shuffling within each repeat of each block.')
    
    if use_odors2pins_from is None:
        if available_pins is None:
            available_pins = list(range(start_pin, stop_pin + 1))
            for p in exclude_pins:
                available_pins.remove(p)

        odors = set()
        for block in blocks_without_repeats:
            # TODO test cases:
            # - block = list of str
            # - block = list of lists of str
            for stim in block:
                if type(stim) is list or type(stim) is tuple:
                    for odor in stim:
                        odors.add(odor)
                else:
                    odors.add(stim)
        
        if hardcoded_pins2odors is not None:
            for p, o in hardcoded_pins2odors.items():
                if o in odors:
                    odors.remove(o)
                    
                if p in available_pins:
                    available_pins.remove(p)
            
        odors = list(odors)
    
        if len(odors) > len(available_pins):
            # TODO break into groups less than or equal to # of olfactometer
            # channels (pins)
            raise NotImplementedError
    
        random.shuffle(available_pins)
        random.shuffle(odors)

        pins2odors = dict(zip(available_pins, odors))
        odors2pins = dict(zip(odors, available_pins))
        
        if hardcoded_pins2odors is not None:
            for p, o in hardcoded_pins2odors.items():
                pins2odors[p] = o
                odors2pins[o] = p
                
    else:
        print('Using pin to odor mapping from: {}'.format(
            use_odors2pins_from))
        
        with open(use_odors2pins_from, 'rb') as f:
            old_stim_data = pickle.load(f)

        if blocks_without_repeats is None:
            blocks_without_repeats = old_stim_data['blocks_without_repeats']

        available_pins = old_stim_data['available_pins']
        odors = old_stim_data['odors']        
        pins2odors = old_stim_data['pins2odors']
        odors2pins = old_stim_data['odors2pins']
        
        if keep_saved_order:
            print('Also using saved trial structure.')
            odor_lists = old_stim_data['odor_lists']
            pin_lists = old_stim_data['pin_lists']
            presentations_per_block = old_stim_data['presentations_per_block']
            save_stimuli_data = False
    
    if use_odors2pins_from is None or not keep_saved_order:
        # TODO work in some presentations of paraffin by itself? kwargs?
        odor_lists = []
        for block in blocks_without_repeats:
            if randomize_within == 'across_repeats':
                block_repeats = block * n_repeats
                # TODO this won't mutate original entry in
                # blocks_without_repeats, will it? (after expansion)
                random.shuffle(block_repeats)
                
            elif randomize_within == 'within_repeat':
                block_repeats = []
                for _ in range(n_repeats):
                    block_repeat = list(block)
                    random.shuffle(block_repeat)
                    block_repeats += block_repeat

            odor_lists += block_repeats

        pin_lists = []
        for stim in odor_lists:
            if type(stim) is list or type(stim) is tuple:
                pin_list = [odors2pins[odor] for odor in stim]
            else:
                pin_list = [odors2pins[stim]]
            pin_lists.append(pin_list)

        block_lengths = set([len(block) * n_repeats for block in
            blocks_without_repeats])
        if len(block_lengths) == 1:
            presentations_per_block = block_lengths.pop()
        else:
            presentations_per_block = None

    data = {
         # TODO also store original blocks_without_repeats?
        'pins2odors': pins2odors,
        'odors2pins': odors2pins,
        'odor_lists': odor_lists,
        'pin_lists': pin_lists,
        'available_pins': available_pins,
        'odors': odors,
        'n_repeats': n_repeats,
        # None if uneven length blocks. Includes presentations of all repeats of
        # a block.
        'presentations_per_block': presentations_per_block,
        'randomize_within': randomize_within,
        'blocks_without_repeats': blocks_without_repeats
    }
    if save_stimuli_data:
        pickle_name_parts = [time.strftime('%Y%m%d_%H%M%S')]
        if extra_pickle_fname_part is not None:
            pickle_name_parts.append(extra_pickle_fname_part)
        pickle_name_parts.append('stimuli.p')
        pickle_name = '_'.join(pickle_name_parts)

        # TODO TODO either only save to dropbox / nas or at least copy
        # to one / both of those places
        print('Saving stimulus data to {}\n'.format(abspath(pickle_name)))
        # TODO TODO maybe also include a git version of this code
        # (+ unsaved changes?)
        with open(pickle_name, 'wb') as f:
            for k, v in extra_data.items():
                if k in data:
                    raise ValueError('extra_data can not have key {}'.format(
                        k))
                data[k] = v
            pickle.dump(data, f)
        # TODO upload to database rather / in addition to pickle?
    else:
        warnings.warn('Not saving stimuli! Only use this mode for testing.')

    return data


def print_as_array(pin_list, channel=None, presentations_per_block=None,
    n_repeats=None):

    if channel is not None:
        s = 'const int channel{}[] = '.format(channel)
    else:
        s = ''
    s += '{'
    pin_separator = ','
    block_separator = '\n '

    if n_repeats is not None:
        n_per_single_block = presentations_per_block // n_repeats

    for n, p in enumerate(pin_list):
        if (presentations_per_block is not None and
            n % presentations_per_block == 0):
            s += block_separator

        elif (n_repeats is not None and
            n % n_per_single_block == 0):
            s += ' '

        s += str(p) + pin_separator

    s = s[:-(len(pin_separator))]
    s += '\n};'
    print(s)


def print_trial_structure(blocks_without_repeats, **kwargs):
    print_available_pins = True
    if 'print_available_pins' in kwargs:
        print_available_pins = kwargs.pop('print_available_pins')

    data = trial_structure(blocks_without_repeats, **kwargs)

    available_pins = sorted(data['available_pins'])
    pins2odors = data['pins2odors']
    n_repeats = data['n_repeats']
    presentations_per_block = data['presentations_per_block']
    pin_lists = data['pin_lists']

    pin_list_lengths = set([len(pl) for pl in pin_lists])
    assert len(pin_list_lengths) > 0, 'pin_lists should not be empty'
    assert len(pin_list_lengths) == 1, ('can not assign fixed # channels w/ ' +
        'varying pin list lengths')
    n_channels = pin_list_lengths.pop()

    '''
    before_first_odor_s = 5
    odor_pulse_s = 1
    between_trials_s = 45
    between_blocks_s = 30
    n_blocks = len(df)
    sec_per_trial = odor_pulse_s + between_trials_s
    total_time = before_first_odor_s + (n_blocks - 1) * between_blocks_s +
    
    print('Number of trials: {}'.format(len(pin_lists)))
    print('Will take {} minutes'.format(len(pin_lists) *
        (sec_per_trial / 60.0)))
    #pp(pin_lists)
    '''
    if print_available_pins:
        print('Available pins: {}\n'.format(available_pins))

    print('Pins to odors:')
    for p in sorted(pins2odors.keys()):
        print(' {}: {}'.format(p, pins2odors[p]))

    print('\nCopy to Arduino script, replacing existing:')

    # TODO TODO test the fix doesn't break anything in pairs.py
    # (or less likely complex_mixtures.py)

    # Note that this block num may conflict w/ that implied by
    # "presentations_per_block", but I think it more in line w/ my
    # usual definition of block (i.e. a continuos period of acquisition).
    # I my definitions for this may have changed between the pair and
    # complex_mixture experiments (analysis had to special case block handling
    # for each)
    block_num = n_repeats
    print(f'const int block_num = {block_num};')
    odors_per_block, remainder = divmod(len(pin_lists), block_num)
    assert remainder == 0
    print(f'const int odors_per_block = {odors_per_block};')
    
    '''
    unique_pinlist_lens = {len(pl) for all_channel_pls in pin_lists
        for pl in all_channel_pls
    }
    assert len(unique_pinlist_lens) == 1
    odors_per_block = unique_pinlist_lens.pop()
    print(f'const int odors_per_block = {odors_per_block};')
    '''
        
    for i in range(n_channels):
        channel = chr(ord('A') + i)
        pins = [pl[i] for pl in pin_lists]
        print_as_array(pins, channel=channel, n_repeats=n_repeats,
            presentations_per_block=presentations_per_block
        )

