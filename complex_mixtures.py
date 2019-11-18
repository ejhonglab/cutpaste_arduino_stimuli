#!/usr/bin/env python3

"""
Generates trial structure for n>2 component mixture experiments.
"""

import pandas as pd

import randomizer


def main():
    df = pd.read_csv('complex_mixtures.csv')

    # TODO update so fly food approx also has real thing and that also goes
    # in hardcoded_pins2odors
    panel = 'fly food approx.'
    assert panel in ('kiwi approx.', 'control mix 2', 'fly food approx.')
    df = df[df['mix'] == panel]
    hardcoded_pins2odors = None
    if panel == 'kiwi approx.':
        real_kiwi = 'd3 kiwi @ 0.0'
        assert (real_kiwi == df.odor_w_conc).any()
        hardcoded_pins2odors = {11: real_kiwi}
        
    
    # TODO maybe implement a True/'last' flag to justs load to most recent one
    # (or last w/in day? some time limit?)
    use_odors2pins_from = None
    #if use_odors2pins_from is None:
    blocks_without_repeats = []
    for gn, gdf in df.groupby('mix'):
        blocks_without_repeats.append(list(gdf.odor_w_conc))
    #else:
    #    blocks_without_repeats = None

    randomizer.print_trial_structure(blocks_without_repeats,
        use_odors2pins_from=use_odors2pins_from,
        # Set this to True to just print the information in the file above,
        # without generating a new trial order.
        keep_saved_order=False,
        save_stimuli_data=True,
        stop_pin=10,
        n_repeats=3,
        hardcoded_pins2odors=hardcoded_pins2odors,
        extra_data={'input_mix_df': df}
    )
        

if __name__ == '__main__':
    main()
