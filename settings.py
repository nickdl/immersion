import os
import numpy as np


_DATA_DIR = 'data'
_SEED_DIR = os.path.join(_DATA_DIR, 'seed_pics')


DIRS = {
    'DATA': _DATA_DIR,
    'SEED': _SEED_DIR,
    'FRACTALS': os.path.join(_SEED_DIR, 'fractals'),
    'PHOTOS': os.path.join(_SEED_DIR, 'photos'),
    'STILLS': os.path.join(_DATA_DIR, 'stills'),
    'DATASET': os.path.join(_DATA_DIR, 'dataset'),
    'STYLES': os.path.join(_DATA_DIR, 'styles_v2'),
    'TRAINED_STYLES': os.path.join(_DATA_DIR, 'styles'),
    'TEST_IMAGES': os.path.join(_DATA_DIR, 'test_images'),
    'WIP': 'wip',
}

VIDEO = {
    'FRAME_RATE': 30,
    'SIZE': (960, 720),
    'DATASET_SIZE': (256, 256),
    'MAX_HUE': .5,
    # 'MAX_SAT': .1,
    'TRANSFORM': .5,
}

_AUDIO_INITIAL_RATE = 44100
_AUDIO_DOWNSAMPLE_FACTOR = 2
_AUDIO_RATE = _AUDIO_INITIAL_RATE//_AUDIO_DOWNSAMPLE_FACTOR

AUDIO = {
    'INITIAL_RATE': _AUDIO_INITIAL_RATE,
    'RATE': _AUDIO_RATE,
    'DTYPE': np.float32,
    'DOWNSAMPLE_FACTOR': _AUDIO_DOWNSAMPLE_FACTOR,
    'MILLISECOND': _AUDIO_RATE//1000,
    'SECOND': _AUDIO_RATE,
    'TRANS_THRESHOLD': 90,
    'STAB_THRESHOLD': 95,
}

CORE = {
    'DISTANCE_MIN': 30,
    'DISTANCE_MAX': 90,
    'INCEPTION': .5,
    'ENERGY_THRESHOLD': .3,
    'REAL': .8,
}
