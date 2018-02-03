# coding=utf-8

import json
import os
import numpy as np
import random
import time


def load_config():
    global config
    file_path = '.\config.json'
    json_file = file(file_path, 'r')
    config = json.load(json_file)
    return config


def screenshot(id):
    os.system('adb shell screencap -p /sdcard/{}.png'.format(id))
    os.system('adb pull /sdcard/{}.png'.format(id))


def jump(distance):
    coefficient = config['coefficient']
    MIN_PRESS_TIME = config['MIN_PRESS_TIME']

    press_time = distance * coefficient
    press_time = max(press_time, MIN_PRESS_TIME)
    rand = random.randint(0, 9) * 10
    swipe_x1 = 320 + rand
    swipe_y1 = 410 + rand
    swipe_x2 = 320 + rand
    swipe_y2 = 410 + rand
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=swipe_x1,
        y1=swipe_y1,
        x2=swipe_x2,
        y2=swipe_y2,
        duration=press_time
    )
    print(cmd)
    os.system(cmd)
    return press_time


def calc_center(img_canny):
    # what is 400?
    y_top = np.nonzero([max(row) for row in img_canny[400:]])[0][0] + 400
    x_top = int(np.mean(np.nonzero(img)))

    y_bottom = y_top + 50
    for row in range(y_bottom, H):
        if img_canny[row, x_top] != 0:
            y_bottom = row
            break

    x_center, y_center = x_top, (y_top + y_bottom) // 2
    return img_canny, x_center, y_center


def main():
    pass


if __name__ == '__main__':
    main()

