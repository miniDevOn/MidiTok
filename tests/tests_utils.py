""" Test validation methods

"""

from typing import List

from miditok import REMIEncoding
from miditoolkit import Instrument, Note


def valid_track(expected_track: Instrument, produced_track: Instrument):

    return 0


def strict_valid(expected_notes: List[Note], produced_notes: List[Note]):
    for exp_note, prod_note in zip(expected_notes, produced_notes):
        if exp_note.start != prod_note.start:
            return False
        elif exp_note.end != prod_note.end:
            return False
        elif exp_note.pitch != prod_note.pitch:
            return False
        elif exp_note.velocity != prod_note.velocity:
            return False


def save_and_load_params():
    enc = REMIEncoding(beat_res={(0, 3): 5})
    enc.save_params('')

    enc2 = REMIEncoding()
    enc2.load_params('config.txt')