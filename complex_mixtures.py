#!/usr/bin/env python3

"""
Generates trial structure for n>2 component mixture experiments.
"""

import pandas as pd

import randomizer


def main():
    df = pd.read_csv('complex_mixtures.csv')

    use_odors2pins_from = None #'20190503_101913_stimuli.p'
    if use_odors2pins_from is None:
        blocks_without_repeats = []
        for gn, gdf in df.groupby('mix'):
            blocks_without_repeats.append(list(gdf.odor_w_conc))
    else:
        blocks_without_repeats = None

    randomizer.print_trial_structure(blocks_without_repeats,
        use_odors2pins_from=use_odors2pins_from,
        # Set this to True to just print the information in the file above,
        # without generating a new trial order.
        keep_saved_order=False,
        save_stimuli_data=True,
        n_repeats=3,
        extra_data={'input_mix_df': df}
    )
        

if __name__ == '__main__':
    main()
