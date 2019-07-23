#!/usr/bin/env python3

"""
Generate trial structure for pair experiments.
"""

import pandas as pd

import randomizer


def main():
    orig_df = pd.read_csv('natural_odor_pair_panel.csv')
    # TODO first print anything duplicated (the different reasons...)
    df = orig_df.drop_duplicates(subset=['odor_1','odor_2'])

    use_odors2pins_from = None #'20190503_101913_stimuli.p'
    if use_odors2pins_from is None:
        # TODO TODO TODO 
        # TODO why did i do sample(frac=1) again? just to support case where i
        # have more pairs than i can present in one go? delete?
        blocks_without_repeats = []
        for pair in df.sample(frac=1).itertuples():
            blocks_without_repeats.append([
                (pair.odor_1, 'paraffin'),
                (pair.odor_2, 'paraffin'),
                (pair.odor_1, pair.odor_2)
            ])
    else:
        blocks_without_repeats = None

    randomizer.print_trial_structure(blocks_without_repeats,
        use_odors2pins_from=use_odors2pins_from,
        # Set this to True to just print the information in the file above,
        # without generating a new trial order.
        keep_saved_order=False,
        save_stimuli_data=True,
        n_repeats=3,
        extra_data={'odor_pair_df': orig_df}
    )
        

if __name__ == '__main__':
    main()
