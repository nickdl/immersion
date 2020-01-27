from pathlib import Path
import os
from shutil import copyfile

import settings
from utils.io import get_files


def train_style(style_image):
    script = 'examples/fast_neural_style/neural_style/neural_style.py'
    style_image_path = '/'.join(str(style_image).split('/')[:-1])
    save_model_dir = os.path.join(style_image_path, style_image.name.replace('.png', ''))
    os.mkdir(save_model_dir)
    cmd = 'python "%s" train --dataset "%s" --style-image "%s" --save-model-dir "%s" --epochs 1 --cuda 1'\
          % (script, settings.DIRS['DATASET'], str(style_image), save_model_dir)
    print('cmd', cmd)
    os.system(cmd)
    return save_model_dir


def train_styles():
    style_images = get_files(settings.DIRS['STYLES'], string=False, recursive=False, file_type='.png')
    test_images = get_files(settings.DIRS['TEST_IMAGES'], string=False)
    for style_image in style_images:
        print('training', style_image.name)
        save_model_dir = train_style(style_image)
        model = next(Path(save_model_dir).rglob('*.model'))
        test_dir = os.path.join(save_model_dir, 'test')
        os.mkdir(test_dir)
        for test_image in test_images:
            output_image = os.path.join(test_dir, test_image.name)
            script = 'examples/fast_neural_style/neural_style/neural_style.py'
            cmd = 'python "%s" eval --content-image "%s" --model "%s" --output-image "%s" --cuda 1' \
                  % (script, str(test_image), str(model), str(output_image))
            print('cmd', cmd)
            os.system(cmd)


def restructrure_dirs():
    style_images = get_files(settings.DIRS['STYLES'], string=False, recursive=False, file_type='.png')
    models = sorted(f for f in Path(settings.DIRS['STYLES']).glob('*/*/*.model'))
    for style_image, style_model in zip(style_images, models):
        name = style_image.name.split('.')[0]
        if name not in str(style_model):
            raise Exception('Please reconsider')
        name = style_image.name.split('.')[0]
        new_folder = os.path.join(settings.DIRS['TRAINED_STYLES'], name)
        os.mkdir(new_folder)
        copyfile(str(style_image), os.path.join(new_folder, name + '.png'))
        copyfile(str(style_model), os.path.join(new_folder, name + '.model'))


# train_styles()
# resume from
# style_images = get_files(settings.DIRS['STYLES'], string=False, recursive=False, file_type='.png')
# for i, s in enumerate(style_images):
#     print(i, s)
# restructrure_dirs()


class Stylist:
    def __init__(self):
        self.styles = sorted(f for f in Path(settings.DIRS['TRAINED_STYLES']).glob('*'))
        self.n_styles = len(self.styles)
        self.style_indexes = list(range(self.n_styles))

    def get_style(self, index=0):
        folder = self.styles[index]
        name = str(folder).split('/')[-1]
        return {
            'image': Path(os.path.join(str(folder), name + '.png')),
            'model': Path(os.path.join(str(folder), name + '.model')),
        }

    def get_styles(self):
        return [
            self.get_style(index)
            for index in range(self.n_styles)
        ]

    def apply_style(self, style_index, content_image, output_image):
        model = self.get_style(style_index)['model']
        script = 'examples/fast_neural_style/neural_style/neural_style.py'
        cmd = 'python "%s" eval --content-image "%s" --model "%s" --output-image "%s" --cuda 1' \
              % (script, str(content_image), str(model), str(output_image))
        print('cmd', cmd)
        os.system(cmd)
