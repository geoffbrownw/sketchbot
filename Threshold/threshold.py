#-------------------------------------------------------------------------------
# Name:        threshold.py
# Purpose:
#
# Author:      GeoffB
#
# Created:     20/12/2014
# Copyright:   (c) GeoffB 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import math
from attribs.attribs import *
from stats import *

def calibrate_black_threshold(pix, width, height):

    """reads a single horizontal row, a single vertical column and a digaonal
    path across an image and searches for line crossings or black pixels that
    appear in each path. Measure the width of each of those lines and return
    the width that is in the center of the list"""

    save_pixel_values = []
    origin = 0, 0

    # get the distance and direction of each path
    diag_dist = int(math.sqrt(width**2 + height**2) * .90)
    vertical_start = int(width/float(2)), 0  # x=width/2, y=0
    horizontal_start = 0, int(height/float(2))  # x=0, y=width/2
    diagonal_angle = get_polar_angle(origin, (width, height), 1)
    
    # create the list of pixels in each row/column/path
    vertical_path = get_pixel_path_from_angle(vertical_start, height, 270, height)
    horizontal_path = get_pixel_path_from_angle(horizontal_start, width, 0, height)
    diag_path = get_pixel_path_from_angle(origin, diag_dist, diagonal_angle, height)
    combined_paths = vertical_path + horizontal_path + diag_path

    for coords in combined_paths:  # this is a down, across and diaganonl line
        x, y = coords
        pixval = pix[x, y]
        save_pixel_values.append(pixval)
    
    avg_pixel = sum(save_pixel_values)/float(len(save_pixel_values))

    std_pixel_dev = calc_variance(save_pixel_values, 1)
    med_pix_index = int(len(save_pixel_values)/float(2))
    median_black = save_pixel_values[med_pix_index]

    gaps = [(x - save_pixel_values[i - 1]) for i, x in enumerate(save_pixel_values)][1:]

    negs = [gap for gap in gaps if gap < -25]  # need to change this to -6 for non-thumbnail images
    raw_neg_gaps = [gap for gap in gaps if gap < -10]
    # print len(negs), len(std_neg_gaps), 'hhhhhhh'
    # negs = sorted(negs)
    # negs = list(set(negs))
    # negs = negs[1:-2]  # elimnated the top and bottom
    std_neg_gaps = list(set(raw_neg_gaps))
    zoot_ind = int(len(std_neg_gaps)/float(2))  # middle index value
    median_neg = std_neg_gaps[zoot_ind]  # median negative jump

    std_neg_dev = get_median_absolute_deviation(std_neg_gaps) # std dev calc either way of median

    # median_neg is median jump, and dev
    return median_neg, std_neg_dev, avg_pixel, std_pixel_dev



def calc_local_thresh(thresh_map, local_avg):

    """
    The threshold value that is returned is used to reduce or increase the threshold value that is what defines black
     the value returned is a negative number which determines how low the current pixel value being read has to be
     to be considered black
    :param thresh_map:
    :param local_avg:
    :return:
    """

    # if middle pixel value is way less than global average

    pixval_map = [threshing[0] for threshing in thresh_map]
    pixval_map.append(local_avg)
    pixval_map = sorted(pixval_map)
    test_index = pixval_map.index(local_avg)

    if test_index == 0:  # Dark
        dark_std_dev, dark_threshold = thresh_map[0]
        percent_avg = local_avg/float(dark_std_dev)
        if local_avg < 76:  # objective override
            threshold = int(percent_avg * dark_threshold) - 3
        elif percent_avg >= .90:
            threshold = dark_threshold
        else:  # super dark
            threshold = int(percent_avg * dark_threshold)
    elif test_index == 1:  # medium dark

        medium_dark_std_dev, medium_dark_threshold = thresh_map[1]
        percent_avg = local_avg/float(medium_dark_std_dev)
        if percent_avg >= .90:
            threshold = medium_dark_threshold
        else:
            if local_avg > 140:  # objectively light in a medium test
                threshold = int(percent_avg * medium_dark_threshold) + 3
            else:
                threshold = int(percent_avg * medium_dark_threshold)

    elif test_index == 2:  # medium light
        medium_light_std_dev, medium_light_threshold = thresh_map[2]
        percent_avg = local_avg/float(medium_light_std_dev)
        if percent_avg >= .90:
            threshold = medium_light_threshold
        else:
            threshold = percent_avg * medium_light_threshold
    else:
        light_std_dev, light_threshold = thresh_map[2]
        percent_avg = local_avg/float(light_std_dev)
        threshold = percent_avg * light_threshold + 4

    return threshold - 4


def create_threshold_map(jumps, pixel_range, MEDIAN_PIXEL, std_jump_dev):

    """Create a list with mappings of pixel values to standard deviation
    thresholds"""

    lowest_in_range = pixel_range[0]  # dark is relative to MEDIAN_PIXEL
    middle_in_range = pixel_range[1]
    highest_in_range = pixel_range[2]

    # is there a short cut to scan the lines prior to

    if MEDIAN_PIXEL * .93 <= middle_in_range <= MEDIAN_PIXEL * 1.07:
        dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) - 8
        medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) - 5
        light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) - 8

    elif middle_in_range < MEDIAN_PIXEL * .93:  # dark image
        if std_jump_dev > 12:  # very contrasty but darker than average #mornt
            dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) - 16  # vwas 16
            medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) - 11
            light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) + 3

        else:   # lower contrast and dark -> need to make it easier to get in
            dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) + 1  # was -1
            medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) + 3 # was 0
            light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) + 4# was 8

    else:   # lighter than average image
        if 8 > std_jump_dev > 12:  # higher contrast flange2.jpg
            dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) - 14  # was -8
            medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) - 10 # was -6
            light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) - 7  # was 0
        elif 3 <= std_jump_dev <= 8:
            dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) - 3
            medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) - 3
            light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) - 3
        else:  # less contrasty, flangehalf.jpg, lobe.jpg
            dark_thresh_per = int(100 * (jumps[0]/float(lowest_in_range))) - 10   # was 8
            medium_thresh_per = int(100 * (jumps[1]/float(middle_in_range))) - 5  # was 5
            light_thresh_per = int(100 * (jumps[2]/float(highest_in_range))) - 10  # was 8

    threshold_map = []
    threshold_map.append([lowest_in_range, dark_thresh_per])
    threshold_map.append([middle_in_range, medium_thresh_per])
    threshold_map.append([highest_in_range, light_thresh_per])

    return threshold_map


def calculate_threshold_range(median_neg, std_dev, avg_pixval, std_pix_dev):

    """

    :param median_neg:
    :param std_dev:
    :param avg_pixval:
    :param std_pix_dev:
    :return:
    """

    lower_jump = int(median_neg + std_dev)
    if lower_jump > 0:
        lower_jump *= -1
    upper_jump = int(median_neg - std_dev)

    lower_pixval = int(avg_pixval - std_pix_dev)
    upper_pixval = int(avg_pixval + std_pix_dev)

    slice_range = [lower_jump, median_neg, upper_jump]
    slice_range_pixval = [avg_pixval - std_pix_dev, avg_pixval, avg_pixval + std_pix_dev]
    return slice_range, slice_range_pixval


def calibrate_black_threshold_thumb(pix, width, height):

    """reads a single horizontal row, a single vertical column and a digaonal
    path across an image and searches for line crossings or black pixels that
    appear in each path. Measure the width of each of those lines and return
    the width that is in the center of the list"""

    save_pixel_values = []
    origin = 0, 0

    # get the distance and direction of each path
    diag_dist = int(math.sqrt(width**2 + height**2) * .90)
    vertical_start = int(width/float(2)), 0  # x=width/2, y=0
    horizontal_start = 0, int(height/float(2))  # x=0, y=width/2
    diagonal_angle = get_polar_angle(origin, (width, height), 1)

    # create the list of pixels in each row/column/path
    vertical_path = get_pixel_path_from_angle(vertical_start, height, 270, height)
    horizontal_path = get_pixel_path_from_angle(horizontal_start, width, 0, height)

    diag_path = get_pixel_path_from_angle(origin, diag_dist, diagonal_angle, 1, height)
    combined_paths = vertical_path + horizontal_path + diag_path

    for coords in combined_paths:  # this is a down, across and diaganonl line
        x, y = coords
        pixval = pix[x, y]
        save_pixel_values.append(pixval)

    avg_pixel = sum(save_pixel_values)/float(len(save_pixel_values))

    std_pixel_dev = calc_variance(save_pixel_values, 1)
    med_pix_index = int(len(save_pixel_values)/float(2))
    median_black = save_pixel_values[med_pix_index]

    gaps = [(x - save_pixel_values[i - 1]) for i, x in enumerate(save_pixel_values)][1:]

    negs = [gap for gap in gaps if gap < -6]

    negs = sorted(negs)
    negs = list(set(negs))
    negs = negs[1:-2]  # elimnated the top and bottom

    zoot_ind = int(len(negs)/float(2))  # middle index value
    median_neg = negs[zoot_ind]  # median negative jump
    std_neg_dev = calc_variance(negs)  # std dev calc either way of median

    # median_neg is median jump, and dev
    return median_neg, std_neg_dev, avg_pixel, std_pixel_dev


def local_threshold(local_average, pixval_deviation, pixval_key):

    """takes a local non-black pixel average and gets how much more or less the
    local value is compared to a global average as a percentage. Then the
    local threshold is multiplied by a global percent and adjusted by the local
    percentage"""

    # if the local average is greater then pixel key we need to make it
    # harder to get in

    local_percentage = round(local_average/float(pixval_key), 3)  # larger negatives means hard to get in

    if local_percentage > 1.15:  # darker than median
        local_thresh = -(pixval_deviation * local_percentage) - 4  # flange2 = +6, lobe - 8, zig = -19
    elif .92 <= local_percentage <= 1.15:
        local_thresh = -(pixval_deviation * local_percentage)  # flange2 = +4, lobe -4, zig = -16
    else:   # lighter than median
        local_thresh = -(pixval_deviation * local_percentage)

    return local_thresh


def get_local_avg_from_integral(integral_image, coords, trunk, box_size=140): # float()

    y, x = coords  # this only works if backwards for some reason !!!!!!!!!!!!!!

    half_box = box_size/2
    try:
        x_se, y_se = x + half_box, y + half_box
        x_ne, y_ne = x + half_box, y - half_box
        x_sw, y_sw = x - half_box, y + half_box
        x_nw, y_nw = x - half_box, y - half_box
        lower_right = integral_image[x_se, y_se]
        upper_right = integral_image[x_ne, y_ne]
        lower_left = integral_image[x_sw, y_sw]
        upper_left = integral_image[x_nw, y_nw]

    except:
        x_se, y_se = x, y
        x_ne, y_ne = x, y - half_box
        x_sw, y_sw = x - half_box, y
        x_nw, y_nw = x - half_box, y - half_box
        lower_right = integral_image[x_se, y_se]
        upper_right = integral_image[x_ne, y_ne]
        lower_left = integral_image[x_sw, y_sw]
        upper_left = integral_image[x_nw, y_nw]

    area = box_size**2
    pixel_sum = lower_right - upper_right - lower_left + upper_left
    avg_pixval = int(pixel_sum/float(area))

    return avg_pixval
