import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt
from scipy.signal import stft
import math

import settings


def read_wav(path):
    audio_rate, data = wavfile.read(path)
    if audio_rate != settings.AUDIO['INITIAL_RATE']:
        raise Exception('Please reconsider: rate %s' % audio_rate)
    data = downsample(data, factor=settings.AUDIO['DOWNSAMPLE_FACTOR'])\
        .astype(settings.AUDIO['DTYPE'])
    data /= data.max()
    print('audio samples:', len(data))
    return data


def downsample(x, factor, binary=False):
    if not binary:
        return x[::factor]
    else:
        window = np.ones(factor, dtype=settings.AUDIO['DTYPE'])
        sampled = np.sqrt(np.convolve(x, window, 'same'))[::factor]
        return (sampled > 0).astype(np.int)


def upsample(x, size):
    factor = math.ceil(size / x.shape[0])
    result = np.zeros(size)
    result[::factor] = x
    return result


def rms(x, window_size, exp=False):
    x_squared = np.square(x).sum(axis=1)
    if not exp:
        window = np.ones(window_size, dtype=settings.AUDIO['DTYPE']) / window_size
    else:
        window = np.exp(np.linspace(0, 1, window_size, dtype=settings.AUDIO['DTYPE']))
        window /= window.sum()
    rms = np.sqrt(np.convolve(x_squared, window, 'same'))
    return rms


def spectrogram(t, f, stft_transposed):
    plt.pcolormesh(t, f, stft_transposed.transpose())
    plt.title('STFT Magnitude')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


def get_transients(x, threshold, window, overlap, bipolar=False):
    f, t, transform = stft(x, fs=settings.AUDIO['RATE'], nperseg=window, noverlap=overlap)
    magnitude = np.abs(transform).transpose()
    # spectrogram(t, f, normalized_magnitude)
    summed = magnitude.sum(axis=1)
    pct_change = np.diff(summed) / summed[1:]
    percentile = np.percentile(pct_change, threshold)
    transients_signal = (pct_change > percentile).astype(np.int)
    if bipolar:
        transients_signal |= (pct_change < -percentile).astype(np.int)
    return upsample(transients_signal, x.shape[0])


def get_control_signals(x):
    factor = settings.AUDIO['RATE'] // settings.VIDEO['FRAME_RATE']

    transients_left = get_transients(
        x[:, 0],
        threshold=settings.AUDIO['TRANS_THRESHOLD'],
        window=40*settings.AUDIO['MILLISECOND'],
        overlap=30*settings.AUDIO['MILLISECOND'],
    )
    transients_right = get_transients(
        x[:, 1],
        threshold=settings.AUDIO['TRANS_THRESHOLD'],
        window=40*settings.AUDIO['MILLISECOND'],
        overlap=30*settings.AUDIO['MILLISECOND'],
    )
    transients_left = downsample(transients_left, factor=factor, binary=True)
    transients_right = downsample(transients_right, factor=factor, binary=True)
    transients = transients_left & transients_right

    energy = rms(x, window_size=10*settings.AUDIO['SECOND'])
    energy -= energy.min()
    energy /= energy.max()
    fade_samples = 5*settings.AUDIO['SECOND']
    fade_window = np.linspace(0.0, 1.0, fade_samples)
    if energy[0] != 0:
        energy[:fade_samples] *= fade_window
    elif energy[-1] != 0:
        energy[-fade_samples:] *= np.flip(fade_window)
    energy = downsample(energy, factor=factor)

    stabs_left = get_transients(
        x[:, 0],
        threshold=settings.AUDIO['STAB_THRESHOLD'],
        window=2*settings.AUDIO['SECOND'],
        overlap=1.5*settings.AUDIO['SECOND'],
        bipolar=True,
    )
    stabs_right = get_transients(
        x[:, 1],
        threshold=settings.AUDIO['STAB_THRESHOLD'],
        window=2*settings.AUDIO['SECOND'],
        overlap=1.5*settings.AUDIO['SECOND'],
        bipolar=True,
    )
    stabs_left = downsample(stabs_left, factor=factor, binary=True)
    stabs_right = downsample(stabs_right, factor=factor, binary=True)
    stabs = stabs_left & stabs_right
    print('stabs:', stabs.sum(), 'stabs & transients:', (stabs & transients).sum())

    return transients, energy, stabs


def test():
    # df = read_wav('../wip/Mass Effect.wav')
    df = read_wav('../wip/Decadent.wav')
    transients, energy, stabs = get_control_signals(df)
    print('time: %s sec' % (len(df)//settings.AUDIO['RATE']))
    print('transients:', transients.sum())
    print('stabs:', stabs.sum())
    plt.plot(df)
    plt.plot(upsample(energy, df.shape[0]))
    plt.show()
    start = 110*settings.AUDIO['SECOND']
    end = 111*settings.AUDIO['SECOND']
    plt.plot(df[start:end, 0])
    plt.plot(upsample(transients, df.shape[0])[start:end])
    plt.show()
    plt.plot(df[:, 0])
    plt.plot(upsample(stabs, df.shape[0])[:])
    plt.show()


# test()
