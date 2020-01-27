import settings
from utils.image import convert
from utils.io import get_files


images = get_files(settings.DIRS['SEED'])
for image in images:
    convert(image, png=True)


fractals = get_files(settings.DIRS['FRACTALS'])
for fractal in fractals:
    convert(fractal, super_res=True)


images = get_files(settings.DIRS['SEED'])
for image in images:
    convert(image, size=settings.VIDEO['SIZE'], scale=True)


# bef 82783 items, totalling 13,5 GB
# aft 82783 items, totalling 1,2 GB
images = get_files(settings.DIRS['DATASET'])
for image in images:
    convert(image, size=settings.VIDEO['DATASET_SIZE'], scale=True)


styles = get_files(settings.DIRS['STYLES'])
for style in styles:
    convert(style, super_res=True, png=True, scale=True)
