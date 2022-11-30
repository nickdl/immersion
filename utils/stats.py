from PIL.ImageStat import Stat
from PIL import Image
import numpy as np

from utils.style import Stylist


def stats():
    stylist = Stylist()
    variance_array = np.zeros((stylist.n_styles, 3))
    mean_array = np.zeros((stylist.n_styles, 3))
    for index, style in enumerate(stylist.get_styles()):
        image = Image.open(style['image'])
        stat = Stat(image)
        variance_array[index] = np.array(stat.stddev)
        mean_array[index] = np.array(stat.mean)
    variance = variance_array.mean(axis=1)
    variance -= variance.min()
    variance /= variance.max()
    brightness = mean_array.mean(axis=1)
    brightness -= brightness.min()
    brightness /= brightness.max()
    tilt = np.abs(mean_array[:, 0] - mean_array[:, 1]) + \
           np.abs(mean_array[:, 0] - mean_array[:, 1]) + \
           np.abs(mean_array[:, 0] - mean_array[:, 1])
    tilt -= tilt.min()
    tilt /= tilt.max()
    neutrality_array = (variance + brightness + tilt) / 3
    indexes = np.argsort(neutrality_array)
    split = {
        'low': list(indexes[:41]),
        'medium': list(indexes[41:41*2]),
        'high': list(indexes[41*2:]),
    }
    print(split)
