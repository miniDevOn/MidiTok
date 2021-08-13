# MidiTok

MidiTok is a package for MIDI encoding / tokenization for deep neural networks. It can process MIDI files and "tokenize" them as for text in the NLP field, to use them with Transformers or RNNs.

MidiTok features most known MIDI encoding strategies, and is built around the idea that they all share common parameters and methods.

## Install

```shell
pip install miditok
```
MidiTok uses MIDIToolkit, which itself uses Mido to read and write MIDI files.

## Encodings

### MIDI-Like

Strategy used in the first symbolic music generative transformers and RNN / LSTM models. It consists of encoding the MIDI messages (Note On, Note Off, Velocity and Time Shift) into tokens as represented in a pure "MIDI way".

![MIDI-Like figure](https://github.com/Natooz/MidiTok/blob/assets/assets/midi_like.png "Three notes played together with different durations")

### REMI

Proposed in the [Pop Music Transformer](https://arxiv.org/abs/2002.00212), it is what we would call a "position-based" representation. The time is represented with "Bar" and "Position" tokens that indicate respectively when a new bar is beginning, and the current position within a bar.

![REMI figure](https://github.com/Natooz/MidiTok/blob/assets/assets/remi.png "Time is tracked with Bar and position tokens")

### Compound Word

Similar to the REMI encoding, the main difference here is that token types of a same "event" are merged together.
A note will be the association of Pitch + Velocity + Duration tokens for instance.

![Compound Word figure](https://github.com/Natooz/MidiTok/blob/assets/assets/cp_word.png "Tokens of the same family are grouped together")

### Structured

Presented with the [Piano Inpainting Application](https://arxiv.org/abs/2107.05944), it is similar to the MIDI-Like encoding but with Duration tokens instead Note-Off.
The main advantage of this encoding is the consistent token type transitions it imposes, which can greatly speed up training. The structure is as: Pitch -> Velocity -> Duration -> Time Shift -> ... (pitch again)

![Structured figure](https://github.com/Natooz/MidiTok/blob/assets/assets/structured.png "The token types always follow the same transition pattern")

### Create your own

You can easily create your own encoding strategy and benefit from the MidiTok framework. Just create a class inheriting from the [MIDITokenizer](miditok/midi_tokenizer_base.py#L34) base class, and override the ```events_to_tokens```, ```tokens_to_event``` and ```create_token_dicts``` methods with your tokenization strategy.

## Features

### Common parameters

Every encoding strategy share some common parameters around which the tokenizers are built:

* **Pitch range:** the MIDI norm can represent pitch values from 0 to 127, but the [GM2 specification](https://www.midi.org/specifications-old/item/general-midi-2) recommend from 21 to 108 for piano, which covers the recommended pitch values for all MIDI program. Notes with pitches under or above this range can be discarded or clipped to the limits.
* **Beat resolution:** is the number of "frames" sampled within a beat. MidiTok handles this with a flexible way: a dictionary of the form ```{(0, 4): 8, (3, 8): 4, ...}```. The keys are tuples indicating a range of beats, ex 0 to 4 for the first bar. The values are the resolutions, in frames per beat, of the given range, here 8 for the first. This way you can create a tokenizer with durations / time shifts of different lengths and resolutions.
* **Number of velocities:** the number of velocity values you want represents. For instance if you set this parameter to 32, the velocities of the notes will be quantized into 32 velocity values from 0 to 127.
* **Additional tokens:** specify which additional tokens bringing information like chords should be included. Note that each encoding is compatible with different additional tokens.

Examples of these parameters can be found in the [constants](miditok/constants.py) file.

### Additional tokens

MidiTok offers the possibility to insert additional tokens in the encodings.
These tokens bring additional information about the structure and content of MIDI tracks to explicitly use them to train a neural network.

TODO chart encoding / token compatibility
TODO Chord detection paragraph

## Examples

### Tokenize a MIDI

```python
from miditok import REMIEncoding
from miditoolkit import MidiFile

# Our parameters
pitch_range = range(21, 109)
beat_res = {(0, 4): 8, (4, 12): 4}
nb_velocities = 32
additional_tokens = {'Chord': True,
                     'Empty': True,
                     'Ignore': False}

# Creates the tokenizer and loads a MIDI
remi_enc = REMIEncoding(pitch_range, beat_res, nb_velocities, additional_tokens)
midi = MidiFile('path/to/your_midi.mid')

# Converts MIDI to tokens
tokens = remi_enc.midi_to_tokens(midi)

# Converts just a selected track
piano_tokens = remi_enc.track_to_tokens(midi.instruments[0], midi.ticks_per_beat)

# And convert it back (the last arg stands for (program number, is drum))
converted_back_track = remi_enc.tokens_to_track(piano_tokens, midi.ticks_per_beat, (0, False))
```

### Tokenize a dataset

MidiTok will save your encoding parameters in a ```config.txt``` file to keep track of how they were converted.

```python
from miditok import REMIEncoding
from pathlib import Path

# Creates the tokenizer and list the file paths
remi_enc = REMIEncoding()  # uses defaults parameters
files_paths = list(Path('path', 'to', 'your', 'dataset').glob('**/*.mid'))

# A validation method to make sure to discard MIDIs we do not want
def midi_valid(midi) -> bool:
    if any(ts.numerator != 4 or ts.denominator !=4 for ts in midi.time_signature_changes):
        return False  # time signature different from 4/4
    if max(note.end for note in midi.instruments[0].notes) < 10 * midi.ticks_per_beat:
        return False  # this MIDI is too short
    return True

# Converts MIDI files to tokens saved as JSON files
remi_enc.tokenize_midi_dataset(files_paths, 'path/to/save', midi_valid)
```

### Write a MIDI file from tokens

```python
from miditok import REMIEncoding
import torch

# Creates the tokenizer and list the file paths
remi_enc = REMIEncoding()  # uses defaults parameters

# The tokens, let's say produced by your Transformer
tokens = torch.rand(4, 500).tolist()  # 4 tracks of 500 tokens
# The instruments, here piano, violin, french horn and drums
programs = [(0, False), (41, False), (61, False), (0, True)]

# Convert to MIDI and save it
generated_midi = remi_enc.tokens_to_midi(tokens, programs)
generated_midi.dump('path/to/save')  # could have been done above by giving the path argument
```

## Contributions

Contributions are gratefully welcomed, feel free to send a PR if you want to add an encoding strategy or speed up the code. Just make sure to pass the [tests](tests/) accordingly to your changes.

## Citations

```bibtex
@inproceedings{remi2020,
    title={Pop Music Transformer: Beat-based modeling and generation of expressive Pop piano compositions},
    author={Huang, Yu-Siang and Yang, Yi-Hsuan},
    booktitle={Proceedings of the 28th ACM International Conference on Multimedia},
    year={2020}
}
```

```bibtex
@inproceedings{cpword2021,
    title={Compound Word Transformer: Learning to Compose Full-Song Music over Dynamic Directed Hypergraphs},
    author={Hsiao, Wen-Yi and Liu, Jen-Yu and Yeh, Yin-Cheng and Yang, Yi-Hsuan},
    booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
    year={2021}
}
```

```bibtex
@article{midilike2018,
    title={This time with feeling: Learning expressive musical performance},
    author={Oore, Sageev and Simon, Ian and Dieleman, Sander and Eck, Douglas and Simonyan, Karen},
    journal={Neural Computing and Applications},
    volume={32},
    number={4},
    pages={955--967},
    year={2018},
    publisher={Springer}
}
```

```bibtex
@misc{structured2021,
    title={The Piano Inpainting Application},
    author={Gaëtan Hadjeres and Léopold Crestel},
    year={2021},
    eprint={2107.05944},
    archivePrefix={arXiv},
    primaryClass={cs.SD}
}
```



## Acknowledgments

We acknowledge [Aubay](https://www.aubay.com/index.php/language/en/home/?lang=en), the [LIP6](https://www.lip6.fr/?LANG=en), [LERIA](http://blog.univ-angers.fr/leria/n) and [ESEO](https://eseo.fr/en) for the financing and support of this project.
