from PIL import Image, ImageEnhance
import os
import numpy as np
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

import settings
from utils.io import slugify


def convert_to_png(image):
    new_filename = '.'.join(image.filename.split('.')[:-1]) + '.png'
    if not image.filename.endswith('.png'):
        print('converting to png %s' % image.filename)
        old_filename = image.filename
        image.save(new_filename, 'PNG')
        os.remove(old_filename)
    return Image.open(new_filename)


def super_resolution(image):
    # toggle optional check (for fractals)
    if image.width < settings.VIDEO['SIZE'][0] or image.height < settings.VIDEO['SIZE'][1]:
        model = 'examples/super_resolution/model_epoch_500.pth'
        script = 'examples/super_resolution/super_resolve.py'
        split = image.filename.split('.')
        split[-2] += '_tmp'
        tmp = '.'.join(split)
        print('tmp', tmp)
        cmd = 'python "%s" --cuda --model "%s" --input_image "%s"  --output_filename "%s"' \
              % (script, model, image.filename, tmp)
        os.system(cmd)
        im = Image.open(tmp)
        os.remove(tmp)
        return im
    else:
        return image


def downscale(image, size=settings.VIDEO['SIZE']):
    width = size[0]
    height = size[1]
    target_aspect_ratio = width / height
    image_aspect_ratio = image.width / image.height
    if image_aspect_ratio > target_aspect_ratio:
        print('downscale_w', image.filename)
        image = image.resize(
            (int(image_aspect_ratio * height), height),
            resample=Image.LANCZOS
        )
        cut = int((image.width - width)/2)
        image = image.crop((cut, 0, width + cut, height))
    elif image_aspect_ratio < target_aspect_ratio:
        print('downscale_h', image.filename)
        image = image.resize(
            (width, int(width/image_aspect_ratio)),
            resample=Image.LANCZOS
        )
        cut = int((image.height - height) / 2)
        image = image.crop((0, cut, width, height + cut))
    else:
        print('downscale_', image.filename)
        image = image.resize((width, height), resample=Image.LANCZOS)
    return image


def convert(path, size=settings.VIDEO['SIZE'], super_res=False, png=False, scale=False):
    im = Image.open(path)
    new_filename = slugify(im.filename)
    if new_filename != im.filename:
        old_filename = im.filename
        im.save(new_filename)
        os.remove(old_filename)
        im = Image.open(new_filename)
    if png:
        im = convert_to_png(im)
        new_filename = '.'.join(im.filename.split('.')[:-1]) + '.png'
    if super_res:
        im = super_resolution(im)
    if scale:
        im = downscale(im, size=size)
    im.save(new_filename)


def adjust_brightness(image_path, energy):
    image = Image.open(image_path)
    brightness = energy / settings.CORE['ENERGY_THRESHOLD']
    enhancer = ImageEnhance.Brightness(image)
    enhanced = enhancer.enhance(brightness)
    enhanced.save(image_path)


def adjust_transform(image_path, factor=1.0):
    image = Image.open(image_path)
    hsv = rgb_to_hsv(np.array(image))
    hue_factor = factor * settings.VIDEO['MAX_HUE']  # hue (0.0, 0.5)
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_factor) % 1.0
    # sat_factor = 1.0 + (factor * settings.VIDEO['MAX_SAT'])  # sat (1, 1.5]
    # hsv[:, :, 1] = hsv[:, :, 1] * sat_factor
    rgb = hsv_to_rgb(hsv).astype(np.uint8)
    image = Image.fromarray(rgb, 'RGB')
    image.save(image_path)
