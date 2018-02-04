# coding=utf-8

import json
import math
import os
import random
import time
import sys

import cv2
import numpy as np


def load_config():
    global config
    file_path = './config.json'
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    # json_file = file(file_path, 'r')
    # config = json.load(json_file)
    return config


def screenshot(pic_name):
    '''screenshot on android device

    :param pic_name: name of screenshot picture
    :return:
    '''
    os.system('adb shell screencap -p /sdcard/{}.png'.format(pic_name))
    os.system('adb pull /sdcard/{}.png'.format(pic_name))


def jump(distance):
    '''convert distance to press time
    :param distance: 
    '''
    coefficient = config['coefficient']
    # MIN_PRESS_TIME = config['MIN_PRESS_TIME']

    press_time = distance * coefficient
    # press_time = max(press_time, MIN_PRESS_TIME)
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
        duration=round(press_time)
    )
    print(cmd)
    os.system(cmd)
    return press_time


def calc_center(img_canny):
    # what is 400?
    y_top = np.nonzero([max(row) for row in img_canny[400:]])[0][0] + 400
    x_top = int(np.mean(np.nonzero(img_canny[y_top])))

    y_bottom = y_top + 50
    for row in range(y_bottom, img_canny.shape[0]):
        if img_canny[row, x_top] != 0:
            y_bottom = row
            break

    x_center, y_center = x_top, (y_top + y_bottom) // 2
    return img_canny, x_center, y_center


def main():
    '''play jump
    '''
    _num = 0
    config = load_config()
    # template of the player
    player_temp = cv2.imread('player.jpg', 0)
    hp, wp = player_temp.shape

    # template of game over hint
    end_temp = cv2.imread('game_end.jpg', 0)

    # template of the white dot
    dot_temp = cv2.imread('white_dot.jpg', 0)
    hd, wd = dot_temp.shape

    jump_count, next_rest, rest_time = (0, random.randrange(2, 9), random.randrange(4, 8))
    while True:
        screenshot(_num)
        img_rgb = cv2.imread('{}.png'.format(_num), 0)

        # quit when game is over
        res_end = cv2.matchTemplate(img_rgb, end_temp, cv2.TM_CCOEFF_NORMED)
        if cv2.minMaxLoc(res_end)[1] > 0.95:
            print('Game Over.')
            break

        # match the player
        match_player = cv2.matchTemplate(img_rgb, player_temp, cv2.TM_CCOEFF_NORMED)
        min_val_player, max_val_player, min_loc_player, max_loc_player = cv2.minMaxLoc(match_player)
        player_center = (max_loc_player[0] + config['offset']['x'], max_loc_player[1] + config['offset']['y'])
        # match the white circle dot
        match_dot = cv2.matchTemplate(img_rgb, dot_temp, cv2.TM_CCOEFF_NORMED)
        min_val_dot, max_val_dot, min_loc_dot, max_loc_dot = cv2.minMaxLoc(match_dot)

        if max_val_dot > 0.95:  # match the white dot
            print('white dot detected!')
            x_center, y_center = max_loc_dot[0] + wd // 2, max_loc_dot[1] + hd // 2
        else:  # then perform edge detection
            img_rgb = cv2.GaussianBlur(img_rgb, (5, 5), 0)
            canny_img = cv2.Canny(img_rgb, 1, 10)
            # H, W = canny_img.shape

            for k in range(max_loc_player[1] - 10, max_loc_player[1] + 189):
                for j in range(max_loc_player[0] - 10, max_loc_player[0] + 189):
                    canny_img[k][j] = 0
            img_rgb, x_center, y_center = calc_center(canny_img)
        # output the image for debug
        img_rgb = cv2.circle(img_rgb, (x_center, y_center), 10, 255, -1)
        cv2.imwrite('last.png', img_rgb)

        distance = math.hypot(player_center[0] - x_center, player_center[1] - y_center)
        jump(distance)
        jump_count += 1
        if jump_count == next_rest:
            print('you have jumped {} times, just rest {} seconds.'.format(jump_count, rest_time))
            time.sleep(rest_time)
            jump_count, next_rest, rest_time = (0, random.randrange(40, 100), random.randrange(10, 40))
        time.sleep(random.uniform(1.0, 1.5))


if __name__ == '__main__':
    main()
