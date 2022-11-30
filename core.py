import os
import numpy as np
from shutil import copyfile, rmtree

import settings
from utils.audio import read_wav, get_control_signals
from utils.io import get_files
from utils.style import Stylist
from utils.image import adjust_brightness, adjust_transform


class StateMachine:
    def __init__(self, wav):
        self.wav = wav
        self.states = {}
        self.frame_pattern = 'frame_%05d.png'
        self.stylist = Stylist()
        self.fractals = get_files(os.path.join(settings.DIRS['FRACTALS'], 'other'))
        self.photos = get_files(os.path.join(settings.DIRS['PHOTOS'], 'athina')) + \
                      get_files(os.path.join(settings.DIRS['PHOTOS'], 'athina1')) + \
                      get_files(os.path.join(settings.DIRS['PHOTOS'], 'athina_laptop')) + \
                      get_files(os.path.join(settings.DIRS['PHOTOS'], 'pictures'))
        self.stab_pictures = get_files(os.path.join(settings.DIRS['FRACTALS'], 'stabs'))
        self.timelapse_index = np.random.randint(0, len(self.photos))
        self.name = self.wav.replace('.wav', '')
        self.transients, self.energy, self.stabs = None, None, None
        self.wip_path, self.wav_path, self.frames_path, self.output_path = None, None, None, None

    def states_index_to_array(self):
        return np.array(sorted(list(self.states.keys())))

    frames = property(states_index_to_array)

    @staticmethod
    def max_factor(distance):
        if distance > settings.CORE['DISTANCE_MIN'] \
                and np.random.random() < settings.VIDEO['TRANSFORM']:
            return np.random.random() * distance / settings.CORE['DISTANCE_MAX']
        else:
            return 0.0

    def prepare(self):
        self.wip_path = os.path.join(settings.DIRS['WIP'], self.name)
        os.mkdir(self.wip_path)
        self.wav_path = os.path.join(settings.DIRS['WIP'], self.wav)
        audio_data = read_wav(self.wav_path)
        self.transients, self.energy, self.stabs = get_control_signals(audio_data)
        self.frames_path = os.path.join(self.wip_path, 'frames')
        os.mkdir(self.frames_path)
        self.output_path = os.path.join(self.wip_path, self.name + '.mp4')

    def get_picture(self, stab=False):
        if not stab:
            if np.random.random() < settings.CORE['REAL']:
                picture = self.photos[self.timelapse_index]
                self.timelapse_index += 1
                self.timelapse_index %= len(self.photos)
            else:
                picture = np.random.choice(self.fractals)
        else:
            picture = np.random.choice(self.stab_pictures)
        return picture

    def get_style(self):
        return np.random.choice(self.stylist.style_indexes)

    def calculate_states(self):
        energized = (self.energy > settings.CORE['ENERGY_THRESHOLD']).astype(np.int)
        transients = np.where(self.transients == 1)[0]

        self.states[0] = {
            'picture': self.get_picture(stab=True),
            'style': self.get_style(),
            'transform': 'start',
            'energy': None,
        }

        # transients
        last_picture_change = None
        for transient_index in transients:
            if transient_index not in self.states:
                last_state = self.frames[np.where(self.frames < transient_index)[0][-1]]
                if self.stabs[transient_index]:
                    picture = self.get_picture(stab=True)
                    last_picture_change = transient_index
                elif transient_index - last_state < settings.CORE['DISTANCE_MIN'] \
                        and last_picture_change \
                        and transient_index - last_picture_change < settings.CORE['DISTANCE_MIN']:
                    picture = None
                else:
                    picture = 'get'
                    last_picture_change = transient_index
                self.states[transient_index] = {
                    'picture': picture,
                    'style': self.get_style(),
                    'transform': 'start',
                    'energy': None,
                }

        # transient transforms
        for state_key in self.frames:
            if self.states[state_key]['transform'] == 'start':
                self.states[state_key]['transform'] = 0.0
                next_state_index = np.where(self.frames > state_key)[0]
                if next_state_index.shape[0]:
                    next_state = self.frames[next_state_index[0]]
                else:
                    next_state = self.energy.shape[0]
                distance = min(next_state - state_key, settings.CORE['DISTANCE_MIN'])
                max_factor = self.max_factor(distance=distance)
                for index in range(1, distance):
                    factor = max_factor * index / distance
                    self.states[state_key + index] = {
                        'picture': None,
                        'style': None,
                        'transform': factor,
                        'energy': None,
                    }

        # fill empty frames
        empty_frames = np.setdiff1d(np.arange(self.energy.shape[0]), self.frames)
        slots = np.split(empty_frames, np.where(np.diff(empty_frames) != 1)[0]+1)
        for slot in slots:
            for sub_slot in np.split(slot, slot[::settings.CORE['DISTANCE_MAX']][:-1]):
                if sub_slot.shape[0]:
                    state_key = sub_slot[0]
                    self.states[state_key] = {
                        'picture': 'get',
                        'style': self.get_style(),
                        'transform': 0.0,
                        'energy': None,
                    }
                    distance = sub_slot.shape[0]
                    max_factor = self.max_factor(distance=distance)
                    for index in range(1, distance):
                        factor = max_factor * index / distance
                        self.states[state_key + index] = {
                            'picture': None,
                            'style': None,
                            'transform': factor,
                            'energy': None,
                        }

        # picture timelapse & brightness
        not_energized = 1 - energized
        for state_index, state in self.states.items():
            if state['picture'] == 'get':
                state['picture'] = self.get_picture()
            if not_energized[state_index]:
                state['energy'] = self.energy[state_index]

    def render_states(self):
        last_content_image = None
        for index in self.frames:
            state = self.states[index]
            frame = os.path.join(self.frames_path, self.frame_pattern % (index + 1))
            print(frame)
            previous_frame = os.path.join(self.frames_path, self.frame_pattern % index)
            if state['picture']:
                self.stylist.apply_style(
                    style_index=state['style'],
                    content_image=state['picture'],
                    output_image=frame,
                )
                last_content_image = state['picture']
            elif state['style']:
                if np.random.random() < settings.CORE['INCEPTION']:
                    content_image = previous_frame
                else:
                    content_image = last_content_image
                self.stylist.apply_style(
                    style_index=state['style'],
                    content_image=content_image,
                    output_image=frame,
                )
            else:
                copyfile(previous_frame, frame)
        for index in self.frames:
            state = self.states[index]
            frame = os.path.join(self.frames_path, self.frame_pattern % (index + 1))
            print('transform', frame)
            if state['transform']:
                adjust_transform(image_path=frame, factor=state['transform'])
            if state['energy'] is not None and state['energy'] < settings.CORE['ENERGY_THRESHOLD']:
                adjust_brightness(image_path=frame, energy=state['energy'])

    def frames_to_video(self):
        frames = os.path.join(self.frames_path, self.frame_pattern)
        youtube_settings = '-preset slow -profile:v high -crf 18 -coder 1 -pix_fmt yuv420p -movflags +faststart -g 15 -bf 2'
        cmd = 'ffmpeg -framerate "%s" -i "%s" -i "%s" -vf "pad=1280:720:160:0:black" -c:v libx264 %s -c:a aac -b:a 384k -shortest "%s"' \
              % (settings.VIDEO['FRAME_RATE'], frames, self.wav_path, youtube_settings, self.output_path)
        print('cmd', cmd)
        os.system(cmd)
        rmtree(self.frames_path)

    def run(self):
        self.prepare()
        self.calculate_states()
        self.render_states()
        self.frames_to_video()


# class StillMachine:
#     def __init__(self):
#         self.stylist = Stylist()
#         self.stills = get_files(settings.DIRS['STILLS'], string=False)
#         self.wip_path = os.path.join(settings.DIRS['WIP'], 'stills')
#         # os.mkdir(self.wip_path)
#
#     def run(self):
#         for still in self.stills:
#             for style_index in self.stylist.style_indexes:
#                 name = ''.join(still.name.split('.')[:-1]) + '_%s.png' % style_index
#                 output_image = os.path.join(self.wip_path, name)
#                 self.stylist.apply_style(
#                     style_index=style_index,
#                     content_image=str(still),
#                     output_image=output_image,
#                 )
#
#
# still_machine = StillMachine()
# still_machine.run()

# state_machine = StateMachine(wav='Decadent.wav')
# state_machine.run()

for wav in get_files('wip', string=False, file_type='.wav'):
    state_machine = StateMachine(wav=wav.name)
    state_machine.run()
