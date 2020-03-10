#!/usr/bin/env python3

"""
Generates trial structure for control mixture calibration experiments,
with a series of (increasing) concentrations for a set of control mixture
odors.

The goal of these experiments is to be able to pick concentrations for the
control mixture odors that are equally activating to some corresponding
odor from a natural mixture.
"""

import random
from pprint import pprint

import pandas as pd

import randomizer


def main():
    control_mix_num = 1
    start_log10_conc = -5
    stop_log10_conc = -3
    include_landmark_odors = True
    only_dhruvs_landmark_odors = True

    if control_mix_num == 1:
        solvent = 'pfo'
    elif control_mix_num == 2:
        # TODO maybe also use pfo in mix 2 case
        solvent = 'water'
    else:
        raise ValueError

    assert start_log10_conc <= stop_log10_conc
    # (also equals the number of separate recordings that need to be done)
    n_concs = abs(start_log10_conc - stop_log10_conc) + 1

    orig_df = pd.read_csv('control_mixture_odors.csv')
    assert control_mix_num in orig_df.mix
    df = orig_df[orig_df.mix == control_mix_num]

    recording_odor_w_conc_list = []
    odor_w_conc_set = set()
    for i, log10_vv_conc in enumerate(
        range(start_log10_conc, stop_log10_conc + 1)):

        odor_w_conc = [f'{o} @ {log10_vv_conc}' for o in df.odor]
        odor_w_conc.append(f'{solvent} @ 0')
        recording_odor_w_conc_list.append(odor_w_conc)

        for owc in odor_w_conc:
            odor_w_conc_set.add(owc)

    # TODO TODO maybe split up a fixed set of landmark private odors across all
    # three concentration recordings, using up to max number of channels
    # (9 for us now, i think)
    if include_landmark_odors:
        # TODO maybe also add dry/humid air (arm/bean glom) that dhruv mentioned
        # to this?
        mdf = pd.read_csv('glomerulus_landmark_odors.csv', quotechar="'")
        if only_dhruvs_landmark_odors:
            mdf = mdf[mdf.dhruv_has].copy()

        # TODO may want to assert / convert any float representations of conc to
        # int, so string equality check (for set membership) can be used.
        # (though currently, all strings in CSV *do* have the int repr)
        landmarks_already_covered = mdf.odor_w_conc.isin(odor_w_conc_set)
        if landmarks_already_covered.any():
            print(landmarks_already_covered.sum(), 'landmark odor(s) will '
                'already be presented as part of calibration curves.\n'
            )
            mdf = mdf[~ landmarks_already_covered]

        landmark_odor2glomerulus = dict(zip(mdf.odor_w_conc, mdf.glomerulus))

        # If stop_pin stays at 10 and nothing else changes this is true.
        # If I increase stop_pin, this should increase by the same amount.
        n_available_pins = 8

        # + 1 b/c solvent
        # (# remaining in each recording)
        n_remaining_pins = n_available_pins - (len(df.odor) + 1)

        n_landmark_odors = len(mdf.odor_w_conc)
        assert n_landmark_odors <= n_concs * n_remaining_pins, \
            'can not fit all landmark odors in without extra recordings'

        landmark_odors = list(mdf.odor_w_conc)
        random.shuffle(landmark_odors)

        # TODO maybe subset further based on which ones i currently have
        # available too (or just change csv?)

    assert len(recording_odor_w_conc_list) == n_concs

    for i, log10_vv_conc in enumerate(
        range(start_log10_conc, stop_log10_conc + 1)):

        odor_w_conc = recording_odor_w_conc_list[i]

        # May currently fail in case where n_landmark_odors is strictly
        # less than n_concs * n_remaining_pins...
        if include_landmark_odors:
            curr_landmark_odors = landmark_odors[:n_remaining_pins]
            odor_w_conc.extend(curr_landmark_odors)

            specific_odors2glomerulus = {o: landmark_odor2glomerulus[o]
                for o in curr_landmark_odors
            }
            print('Glomerulus specific odors in this recording:')
            pprint(specific_odors2glomerulus)
            print()

            landmark_odors = landmark_odors[n_remaining_pins:]

        blocks_without_repeats = [odor_w_conc]

        randomizer.print_trial_structure(blocks_without_repeats,
            extra_pickle_fname_part=f'vv{log10_vv_conc}',
            stop_pin=10,
            n_repeats=3,
            print_available_pins=True if i == 0 else False,
            extra_data={
                'input_df': orig_df,
                'specific_odors2glomerulus': specific_odors2glomerulus
            }
        )
        print('\n')
        

if __name__ == '__main__':
    main()
