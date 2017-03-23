#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      GeoffB
#
# Created:     31/12/2014
# Copyright:   (c) GeoffB 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import random
from PIL import Image, ImageMath
import math
from preprocess import get_weighted_mavg
from stats import *

def calc_end_coord_of_path(start_coords, radius, angle):

    """Get the end coords of a path given a radius and angle
    think unit circle calculation"""

    k, h = start_coords

    if angle < 0:
        angle -= 360

    if 0 < angle < 90:  # Q1
        xraw = (radius * math.cos(math.radians(angle))) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 90 < angle < 180:  # QII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 180 < angle < 270:  # QIII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 270 < angle < 360:          # QIV
        xraw = k + (radius * math.cos(math.radians(angle)))
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif angle == 90:
        xraw = k
        yraw = h - radius
    elif angle == 180:
        xraw = k - radius
        yraw = h
    elif angle == 270:  # k is x, h is y
        xraw = k
        yraw = h + radius
    elif angle == 0 or angle == 360:
        xraw = k + radius
        yraw = h
    else:
        xraw = k
        yraw = h
    x = int(xraw)
    y = int(yraw)

    end_coords = x, y
    return end_coords


def calc_euclid_dist(a, b, round=0, signed=0):

    """takes two coordinates a and b and gets the distance between
    them using a**2 + b**2 = c**. Rounding is optional set it to 1 to send
    raw distance."""

    x, y = a
    xd, yd = b
    distance_squared = abs(x-xd)**2 + abs(y-yd)**2
    distance = math.sqrt(distance_squared)

    if distance == 0:
        return 0

    if round == 0:
        return int(distance)
    else:
        return distance


def seed_mavg(path_list, pix, length=5):

    """This seeds a moving average with a list. Pulls out the first length
    from the path list and sends it to get weighted avg."""

    seed = []

    for coord in path_list[0:length]:
        xv, yv = coord
        pixval = pix[xv, yv]
        seed.append(pixval)

    avg, seed_list = get_weighted_mavg(seed[0], seed[1:length])

    return avg, seed_list


class moving_average_container():

    def __init__(self, sample_list):
        self.sample_list = sample_list

    def get_moving_average(self, new_value):

        self.new_value = new_value
        self.sample_list.pop(0)
        self.sample_list.append(self.new_value)

        sample_sum = sum(self.sample_list)
        sample_len = len(self.sample_list)
        sample_avg = int(sample_sum/float(sample_len))
        return sample_avg


def add_vector_to_coord(coords, angle, hypotenuse):

    """Add an angle and a magnitude to a coordinate to adjust it. We use this
    to adjust the width of the search area"""

    # a2 * b2 = c2
    # i have angle and hypotenuse sohcahtoa  sin(0) = o/h or h*sin = o
    opposite = math.sin(math.radians(angle)) * hypotenuse #y value  cos = a/h
    adjacent = math.cos(math.radians(angle)) * hypotenuse

    x, y = coords
    x += adjacent
    y += opposite

    return int(x), int(y)


def calc_end_coord_of_path(start_coords, radius, angle):

    """Get the end coords of a path given a radius and angle
    think unit circle calculation"""

    k, h = start_coords

    if angle < 0:
        angle -= 360

    if 0 < angle < 90:  # Q1
        xraw = (radius * math.cos(math.radians(angle))) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 90 < angle < 180:  # QII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 180 < angle < 270:  # QIII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 270 < angle < 360:          # QIV
        xraw = k + (radius * math.cos(math.radians(angle)))
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif angle == 90:
        xraw = k
        yraw = h - radius
    elif angle == 180:
        xraw = k - radius
        yraw = h
    elif angle == 270:  # k is x, h is y
        xraw = k
        yraw = h + radius
    elif angle == 0 or angle == 360:
        xraw = k + radius
        yraw = h
    else:
        xraw = k
        yraw = h
    x = int(xraw)
    y = int(yraw)

    end_coords = x, y
    return end_coords


def calc_end_coord_of_path_svg(start_coords, radius, angle):

    """Get the end coords of a path given a radius and angle
    think unit circle calculation"""

    k, h = start_coords

    if 0 < angle < 90: #Q1
        xraw = (radius * math.cos(math.radians(angle))) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 90 < angle < 180:  # QII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 180 < angle < 270:  # QIII
        xraw = radius * math.cos(math.radians(angle)) + k
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif 270 < angle < 360:          # QIV
        xraw = k + (radius * math.cos(math.radians(angle)))
        yraw = h - (radius * math.sin(math.radians(angle)))
    elif angle == 90:
        xraw = k
        yraw = h + radius
    elif angle == 180:
        xraw = k + radius
        yraw = h
    elif angle == 270:
        xraw = k
        yraw = h + radius
    elif angle == 0 or angle == 360:
        xraw = k + radius
        yraw = h
    else:
        xraw = k
        yraw = h
    x = int(xraw)
    y = int(yraw)

    end_coords = x, y
    return end_coords


def get_pixel_path_from_angle(center_coords, max_radius, angle, maxy, truncate=0):

    """Takes in a center coord, a radius and and angle parameter. Calculates each
    point in a path in the direction of the angle for the distance of the radius
    returns a list of x, y coordinates between the start point and the end point.
        1. Options include: truncate - sometimes you only want a portion of the
        list. truncate removes a percentage of the start and end of the path"""

    k, h = center_coords  # cetner of term coordinate

    path_coords = []
    # the path may need to be shortened from its
    if truncate == 1:
        start_rad = int(max_radius * .17)
        end_rad = int(max_radius * .85)
    elif truncate == 2:
        start_rad = int(max_radius * .25)  #radius say is 100 we go from 22-82%
        end_rad = int(max_radius * .80)
    else:
        start_rad = 0  # zero to max radius get the full path between
        end_rad = int(max_radius)
    
    for radius in range(start_rad, end_rad):

        if 0 < angle < 90: #Q1
            xraw = (radius * math.cos(math.radians(angle))) + k
            yraw = h - (radius * math.sin(math.radians(angle)))
        elif 90 < angle < 180:  # QII
            xraw = radius * math.cos(math.radians(angle)) + k
            yraw = h - (radius * math.sin(math.radians(angle)))
        elif 180 < angle < 270:  # QIII
            xraw = radius * math.cos(math.radians(angle)) + k
            yraw = h - (radius * math.sin(math.radians(angle)))
        elif 270 < angle < 360:          # QIV
            xraw = k + (radius * math.cos(math.radians(angle)))
            yraw = h - (radius * math.sin(math.radians(angle)))
        elif angle == 90:
            xraw = k
            yraw = h - radius
        elif angle == 180:
            xraw = k - radius
            yraw = h
        elif angle == 270:
            xraw = k
            yraw = h + radius
        elif angle == 0 or angle == 360:
            xraw = k + radius
            yraw = h
        else:
            xraw = k
            yraw = h
        x = int(xraw)
        y = int(yraw)

        coords = x, y
        if coords not in path_coords:  #this sends raw data could be out of ran
            path_coords.append(coords)
        else:
            pass
    
    return path_coords
    

def get_polar_angle(point1, point2, suppress_quad=0):

    x, y = point1[0], point1[1]
    xd, yd = point2[0], point2[1]

    xdelta = x - xd
    ydelta = (y - yd) * -1 # convert the delta for rotated x/y axis of image
    
    angle = math.degrees(math.atan2(ydelta, xdelta))
    angle += 180
   
    if suppress_quad == 1:
        return int(angle)
    else:
	if xdelta > 0 and ydelta > 0:
            quad = 3
        elif xdelta < 0 and ydelta > 0:
            quad = 4
        elif xdelta > 0 and ydelta < 0:
            quad = 2
        elif xdelta < 0 and ydelta < 0:
            quad = 1
        return int(angle), quad
        

def get_median_line_width(pix, jump_slice, pixel_test, width, height):

    """reads a single horizontal row, a single vertical column and a digaonal
    path across an image and searches for line crossings or black pixels that
    appear in each path. Measure the width of each of those lines and return
    the width that is in the center of the list"""

    origin = 0, 0

    # get the distance and direction of each path
    diag_dist = int(math.sqrt(width**2 + height**2) * .90)
    vertical_start = int(width/float(2)), 10  # x=width/2, y=0
    horizontal_start = 10, int(height/float(2))  # x=0, y=width/2
    diagonal_angle = get_polar_angle(origin, (width, height), 1)
    
    # create the list of pixels in each row/column/path
    vertical_path = get_pixel_path_from_angle(vertical_start, height - 10, 270, width)
    horizontal_path = get_pixel_path_from_angle(horizontal_start, width - 10, 0, height)
    diag_path = get_pixel_path_from_angle(origin, diag_dist, diagonal_angle, 1, height)
    # print vertical_path[0], vertical_path[-1], 'vertical path start'
    # print horizontal_path[0], horizontal_path[-1], 'horizontal path start'
    
    avg, seed_list = seed_mavg(diag_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = vertical_path[0]
    x, y = first_coord
   
    last_pixval = pix[x, y]
   
    trigger = 0
    temp_line = []
    save_lines = []
    # read each pixel value in a path look for runs of black pixels
    for coords in vertical_path[1:]:
        x, y = coords
        pixval = pix[x, y]  # pixel value
        thresh = pixval - last_pixval  # threshold

        if trigger == 0:  # if no black pixel set the new threshold value
            # if the avg pixel is less than a pre calculated black level
            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 1  # set the threshold value
            # elif pixel_test[0] <= avg <= pixel_test[-1]:
            elif pixel_test[0] <= avg <= pixel_test[1]:
                threshold = jump_slice[1]  # get the middle threshold value
            else:
                threshold = jump_slice[-1] - 1  # get the dark threshold level

        if thresh <= threshold and trigger == 0:  # if the current pixval is less than threshold and no trigger
            trigger = 1  # then set trigger to start saving black pixels

        if trigger == 1: # actually save the black coords
            temp_line.append(coords)

        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    avg, seed_list = seed_mavg(diag_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = diag_path[0]
    x, y = first_coord
    last_pixval = pix[x, y]

    trigger = 0
    temp_line = []

    for coords in diag_path[1:]:
        x, y = coords
        pixval = pix[x, y]
        thresh = pixval - last_pixval

        if trigger == 0:

            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 3
            elif pixel_test[0] <= avg <= pixel_test[-1]:
                threshold = jump_slice[1]
            else:
                threshold = jump_slice[-1] - 1

        if thresh <= threshold and trigger == 0:  # start saving
            trigger = 1

        if trigger == 1:  # actually save the black coords
            temp_line.append(coords)

        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    avg, seed_list = seed_mavg(horizontal_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = horizontal_path[0]
    x, y = first_coord
    last_pixval = pix[x, y]

    trigger = 0
    temp_line = []

    for coords in horizontal_path[1:]:
        x, y = coords
        pixval = pix[x, y]
        thresh = pixval - last_pixval
	
        if trigger == 0:

            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 3
            elif pixel_test[0] <= avg <= pixel_test[-1]:
                threshold = jump_slice[1]
            else:
                threshold = jump_slice[-1] - 1

        if thresh <= threshold and trigger == 0:  # start saving
            trigger = 1

        if trigger == 1:  # actually save the black coords
            temp_line.append(coords)
	
        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    save_line_lens = []
   
    for line in save_lines:

        line_len = len(line)
	
        # if 5 < line_len < 30:
        if 4 < line_len < 30:
            save_line_lens.append(line_len)

    line_sum = sum(save_line_lens)
    num_lines = len(save_line_lens)

    line_avg = int(line_sum/float(num_lines))  # or should we get median?????

    median_line_index = int(num_lines/float(2))
    median_line = save_line_lens[median_line_index]

    return line_avg


def get_median_line_width_thumbnail(pix, jump_slice, pixel_test, width, height):

    """reads a single horizontal row, a single vertical column and a digaonal
    path across an image and searches for line crossings or black pixels that
    appear in each path. Measure the width of each of those lines and return
    the width that is in the center of the list"""

    origin = 0, 0

    # get the distance and direction of each path
    diag_dist = int(math.sqrt(width**2 + height**2) * .90)
    vertical_start = int(width/float(2)), 0  # x=width/2, y=0
    horizontal_start = 0, int(height/float(2))  # x=0, y=width/2
    diagonal_angle = get_polar_angle(origin, (width, height), 1)

    # create the list of pixels in each row/column/path
    vertical_path = get_pixel_path_from_angle(vertical_start, height, 270, width)
    horizontal_path = get_pixel_path_from_angle(horizontal_start, width, 0, height)
    diag_path = get_pixel_path_from_angle(origin, diag_dist, diagonal_angle, 1, height)

    avg, seed_list = seed_mavg(diag_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = vertical_path[0]
    x, y = first_coord
    last_pixval = pix[x, y]

    trigger = 0
    temp_line = []
    save_lines = []

    for coords in vertical_path[1:]:
        x, y = coords
        pixval = pix[x, y]
        thresh = pixval - last_pixval

        if trigger == 0:

            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 1
#            elif pixel_test[0] <= avg <= pixel_test[-1]:
            elif pixel_test[0] <= avg <= pixel_test[1]:
                threshold = jump_slice[1]
            else:
                threshold = jump_slice[-1] - 1

        if thresh <= threshold and trigger == 0:  # start saving
            trigger = 1

        if trigger == 1: # actually save the black coords
            temp_line.append(coords)

        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    avg, seed_list = seed_mavg(diag_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = diag_path[0]
    x, y = first_coord
    last_pixval = pix[x, y]

    trigger = 0
    temp_line = []

    for coords in diag_path[1:]:
        x, y = coords
        pixval = pix[x, y]
        thresh = pixval - last_pixval

        if trigger == 0:

            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 3
            elif pixel_test[0] <= avg <= pixel_test[-1]:
                threshold = jump_slice[1]
            else:
                threshold = jump_slice[-1] - 1

        if thresh <= threshold and trigger == 0:  # start saving
            trigger = 1

        if trigger == 1:  # actually save the black coords
            temp_line.append(coords)

        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    avg, seed_list = seed_mavg(horizontal_path, pix, 7)
    moving_avg = moving_average_container(seed_list)
    avg = moving_avg.get_moving_average(avg)

    # read the pixels in the vertical path and compare them to threshold value
    first_coord = horizontal_path[0]
    x, y = first_coord
    last_pixval = pix[x, y]

    trigger = 0
    temp_line = []

    for coords in horizontal_path[1:]:
        x, y = coords
        pixval = pix[x, y]
        thresh = pixval - last_pixval

        if trigger == 0:

            if avg < pixel_test[0]:
                threshold = jump_slice[0] - 3
            elif pixel_test[0] <= avg <= pixel_test[-1]:
                threshold = jump_slice[1]
            else:
                threshold = jump_slice[-1] - 1

        if thresh <= threshold and trigger == 0:  # start saving
            trigger = 1

        if trigger == 1:  # actually save the black coords
            temp_line.append(coords)

        if trigger == 0 and thresh >= threshold + 8:
            avg = moving_avg.get_moving_average(pixval)

        if pixval >= avg - 10 and trigger == 1 or thresh >= 12 and trigger == 1:
            # if we hit a high one and trigger is one then reset
            trigger = 0
            save_lines.append(temp_line)
            temp_line = []
        last_pixval = pixval

    save_line_lens = []
    for line in save_lines:
        line_len = len(line)

        if 1 <= line_len < 12:
            save_line_lens.append(line_len)

    line_sum = sum(save_line_lens)
    num_lines = len(save_line_lens)
    # print num_lines, 'this is number of lines that we are testing for size'
    if num_lines <= 1:
	line_avg = 3
    else:
        line_avg = int(line_sum/float(num_lines))  # or should we get median?????

    # median_line_index = int(num_lines/float(2))
    # median_line = save_line_lens[median_line_index]

    return line_avg


def read_line_down(pix, IMWIDTH, IMHEIGHT):

    """
    This is the read line down used in detect lined paper
    """

    # initialize the pixelvalue  moving average for line detection
    x = 80
    avg_init = []
    # print 'inseid read line down'
    for yi in range(6):
	print yi, 'this is y i'
        mav_pix = pix[x, yi]
	print 'post pix', mav_pix
        avg_init.append(mav_pix[0])  # check avg red color
	print 'post append red'
    avg_start = sum(avg_init)/float(6)
    print 'avg start', avg_start
    list_of_blue_coords = []
    list_of_blue_colors = []
    print 'pre yval down'
    # a really rough moving average check for line checking
    for yval in range(IMHEIGHT - 10):
        pixval = pix[x, yval]

	# get the first pixel value in the color tuple 'pixval' and see if its in the average range
        red_val, green_val, blue_val = pixval
        if red_val < (blue_val * .90) and green_val < blue_val:  # blue line

        # if avg_start - 20 <= pixval[0] <= avg_start + 20:  # we are looking at red color RGB # 
            # avg_init.pop(0)  # could use deque for better performance
            # avg_init.append(pixval[0])
            # avg_start = sum(avg_init)/float(6)
            # else:  # if the first pixel is not within 20 of blue then save it. this give us a list of adjacent pixels
	    # theoretically this is the space between blue lines of the lined paper
            pair = x, yval
            list_of_blue_coords.append(pair)  # blue coords
            list_of_blue_colors.append(pixval)  # blue colors
    
    # print len(list_of_blue_colors), 'colors'
    dist_between = [(calc_euclid_dist(coord, list_of_blue_coords[ind -1]), coord) for ind, coord in enumerate(list_of_blue_coords)][1:]
    large_gaps_and_coords = [dinga for dinga in dist_between if dinga[0] > 10]
    
    gaps = [dinga[0] for dinga in large_gaps_and_coords]
    # look for rhythm in the gaps
    # print gaps, 'this is the number of gaps'
    # print [abs(dag - gaps[index-1]) for index, dag in enumerate(gaps)][1:]
    # print len(gaps), 'gaps'
    if len(gaps) > 8:  # have to have more than 8 lines
        variance = calc_variance(gaps, 1)
	deviation_in_gaps = get_median_absolute_deviation(gaps)
	# print deviation_in_gaps, 'deviation'	
        if deviation_in_gaps <= 23:
            return True, list_of_blue_colors, large_gaps_and_coords
        else:
 	    # too lumpy of a line distribution to be regular lines
            return False
    else:  # no lines found
        return False


def remove_lines_old(lined_image, IMWIDTH, IMHEIGHT):

    """Remove the lines from an drawing that was drawn on lined paper"""
    # do we want to make a running average??

    for x in range(10, IMWIDTH - 10):
        for y in range(10, IMHEIGHT - 11):
		   
	    local_pixval = lined_image[x, y]
	    red_val, green_val, blue_val = local_pixval
	    # pixel intensity?
	    if x == 2000:
		# print x, y, local_pixval
		pass
	    
	    if red_val <= 55 and green_val <= blue_val:
		
		grey_color = red_val, green_val, red_val
		for item in range(6):
		    lined_image[x, y - 2 + item] = grey_color
		    # pass
		    # span_val = lined_image[x, y-span_adj+span] 
		    # lined_image[x, y-6+span] = span_val
	    
		     
    print 'did this return'
    return lined_image


def diff1(source, color):
    """When source is bigger than color"""
    return (source - color) / (255.0 - color)

def diff2(source, color):
    """When color is bigger than source"""
    return (color - source) / color


def color_to_alpha(image, color=None):
    # convert to rgb color with alpha channel
    print 'inside color to alpha'
    image = image.convert('RGBA')
    print 'convert succeded'
    width, height = image.size  # size
    print width, height, 'inside'
    color = map(float, color)  # map the float color
    print color, 'color'
    img_bands = [band.convert("F") for band in image.split()]
    print img_bands, 'split the image into bands'
    # Find the maximum difference rate between source and color. I had to use two
    # difference functions because ImageMath.eval only evaluates the expression
    # once.
    alpha = ImageMath.eval(
        "float(max(max(max(diff1(red_band, cred_band), diff2(green_band, cgreen_band)), diff1(blue_band, cblue_band)), max(max(diff2(red_band, cred_band),diff2(green_band, cgreen_band)),diff2(blue_band, cblue_band))))",
        diff1=diff1,
        diff2=diff2,
        red_band = img_bands[0], 
        green_band = img_bands[1],
        blue_band = img_bands[2],
        cred_band = color[0],
        cgreen_band = color[1],
        cblue_band = color[2]
    )
    print 'alpha went'
    # Calculate the new image colors after the removal of the selected color
    new_bands = [
        ImageMath.eval(
            "convert((image - color) / alpha + color, 'L')",
            image = img_bands[i],
            color = color[i],
            alpha = alpha
        )
        for i in xrange(3)
    ]
    print 'new bands'
    # Add the new alpha band
    new_bands.append(ImageMath.eval(
        "convert(alpha_band * alpha, 'L')",
        alpha = alpha,
        alpha_band = img_bands[3]
    ))
    print 'new bands appended'

    return Image.merge('RGBA', new_bands)

def remove_lines(image, color_mask):
    
    print 'inside remove lines'
    image = color_to_alpha(image, (220, 100, 140, 255))
    print 'returned image'
    background = Image.new('RGB', image.size, (255, 255, 255))
    background.paste(image.convert('RGB'), mask=image)
    return image

def calc_avg_coord(coord_list):

    average_coords = []

    for coord in coord_list:
        num_coords = len(coord)
        xsum = sum([foo[0] for foo in coord])
        ysum = sum([foo[1] for foo in coord])

        x_avg = int(xsum/float(num_coords))
        y_avg = int(ysum/float(num_coords))
        pair = x_avg, y_avg
        average_coords.append(pair)

    return average_coords


def calc_avg_angle(angle_list):

    """

    :param angle_list:
    :return:
    """

    # get children that have only two intersections
    angle_pairs = [ango for ango in angle_list if len(ango) == 2]

    num_angles = len(angle_pairs)

    sorted_list = []
    for item in angle_pairs:
        a, b = item
        if a > 270:
            a -=360

        if b > 270:
            b -= 360

        pair = sorted([a, b])
        sorted_list.append(pair)

    a_list = [alist[0] for alist in sorted_list]
    b_list = [blist[1] for blist in sorted_list]

    a_avg = sum(a_list)/float(num_angles)
    b_avg = sum(b_list)/float(num_angles)

    avg_pair = a_avg, b_avg

    return avg_pair


def calc_triad(triad_list):

    """
    take three coordinates in a segment
    :param triad_list:
    :return:
    """

    save_deltas = []

    for triad_index in range(-1, 2):
        coord_one = triad_list[triad_index]
        coord_two = triad_list[triad_index + 1]

        point_delta = calc_euclid_dist(coord_one, coord_two)
        save_deltas.append(point_delta)
    # get the index of the larges delta, pull out the first coord of it
    max_delta = max(save_deltas)
    triad_index = save_deltas.index(max_delta)

    if triad_index == 2:
        x_sub_j, y_sub_j = triad_list[1]  # the first two are the longest
        x_sub_i, y_sub_i = triad_list[2]
        x_sub_k, y_sub_k = triad_list[0] # measure perp to this
    elif triad_index == 0:
        x_sub_j, y_sub_j = triad_list[0]
        x_sub_i, y_sub_i = triad_list[2]
        x_sub_k, y_sub_k = triad_list[1]
    else:  #if 1
        x_sub_j, y_sub_j = triad_list[1]
        x_sub_i, y_sub_i = triad_list[2]
        x_sub_k, y_sub_k = triad_list[0]

# ok we need to make the triangle height scale invariant by looking at the ratio
# of base line to delta height
    delta_numerator = ((x_sub_j - x_sub_i) * y_sub_k + (y_sub_i - y_sub_j)
        * x_sub_k + x_sub_i * y_sub_j - x_sub_j * y_sub_i)

    delta_denominator = math.sqrt((x_sub_j - x_sub_i)**2 + (y_sub_j - y_sub_i)**2)

    height = delta_numerator/float(delta_denominator)
    # print round(height, 2), 'height in triad'
    return round(height, 2)


def segment_avg_curvature(nodes_in_segment):

    # chose the start point, and two randos
    # create a triangle from the points
    # choose the longest side
    # calculate height from longest side to vertex above
    # if within threshold height then continue expanding triangle

    number_of_nodes = len(nodes_in_segment)
    skellies = [dank.skeleton_point for dank in number_of_nodes]

    for issue in range(number_of_nodes):
        pass


def check_horizontal_alignment(verticals, noded_lost): # CheckHorizontalAlignment

    """Compare two node lists to see if they are on the same horizontal alignment"""

    save_high = 0
    save_low = 10000
    save_pos = []

    for nitem in noded_lost:
        flats = nitem.flat_children
        try:
            modded = [x % IMWIDTH for x in flats]
            high = modded[-1]
            low = modded[0]
        except:
            modded = flats % IMWIDTH
            high = modded
            low = modded

        if high > save_high:
            save_high = high

        if low < save_low:
            save_low = low

    for possible in verticals:
        pflat = possible.flat_children
        try:
            p = [z % IMWIDTH for z in pflat]
            phigh = p[-1]
            plow = p[0]
        except:
            p = pflat % IMWIDTH
            phigh = p
            plow = p

        if (save_low - 10 <= plow <= save_high + 10 or
            save_low - 10 <= plow <= save_high + 10):
            if possible not in noded_lost:
                save_pos.append(possible)

    return save_pos


def get_level_matches(cluster, lost_range, noded_losts):

    """Find the cluster where the lost cluster belongs by looking at coordinate
    values from the parent cluster and the lost cluster"""

    saved_nodes = []
    ckeys = cluster.keys()

    for cluster_key in ckeys:  # get cluster keys
        branch_keys = cluster[cluster_key].keys()
        # just cruise through all the branches in all the clusters looking for
        # vertical and horizontal matches
        for bkey in branch_keys:
            branch_node = cluster[cluster_key][bkey]  # pull out the branch node list
            within_vertical_range = [x for x in branch_node
                    if lost_range[0] - 12 <= x.line_count <= lost_range[-1] + 12]
            # get all nodes in vertical range of lost range
            within_horizontal_range = (
                check_horizontal_alignment(within_vertical_range, noded_losts))
            if within_horizontal_range:
                for itemw in within_horizontal_range:
                    saved_nodes.append(itemw)
    return saved_nodes


def compare_loose_ends(lost_cluster, possible_fathers):

    """Look at the point in the larger cluster where the lost cluster fits in
    by comparing the horizontal connection points and finding the closest node
    to the lost cluster. Analogy is that of a Puzzle piece - the cluster is the
    whole puzzle and the lost cluster is a single piece that has to fit into
    the larger whole in the correct place and orientation. The place is the
    coordinates and the orientation is the modded horizontal values of
    the closest node. """

    save_closest = 10000
    save_closest_node = []
    save_closest_lost = []

    for lost_c in lost_cluster:
        # scroll through the lost cluster nodes and mod them to get the
        # horizontal alignment of other nodes in range
        p = lost_c.flat_children
        try:
            q = [x % IMWIDTH for x in p]
        except:
            q = p % IMWIDTH

        for dad in possible_fathers:
            # Mod the possible fathers for horizontal alignment with the
            # lost boys

            f = dad.flat_children  # this is the flat
            try:
                pa = [x % IMWIDTH for x in f]
            except:
                pa = f % IMWIDTH

            if type(pa)==list:
                if type(q)==list:   # list vs list
                    dif = [abs(a-b) for a in pa for b in q]
                    # look through the parents children and subtract the
                    # value of the
                    closest = sorted(dif)[0]
                    # get the lowest value difference between modded losts
                    # and parents
                else:  # list vs int
                    dif = [abs(a - q) for a in pa]
                    closest = sorted(dif)[0]
            else:
                if type(q) == list:   # int vs list
                    dif = [abs(b - pa) for b in q]
                    closest = sorted(dif)[0]
                else:   # int vs int
                    closest = abs(q-pa)

            if closest < save_closest:
                # This gets the last one in the list not a specific closest pixel
                # group
                save_closest = closest
                save_closest_node = dad  # parent that's closest
                save_closest_lost = lost_c   # lost node that's closest??

    return save_closest_node, save_closest_lost


if __name__ == '__main__':
    # print 'this is main'
    pass
