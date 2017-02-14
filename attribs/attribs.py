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
import math
from preprocess import get_weighted_mavg
from stats import *


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


def get_polar_angle(point_a, point_b, supress_quad=0):

    """Get angle between two points. Split the points up into x, y
    and xd, yd then get the quadrant of the delta coordinates so we can adjust
    the equation to get the polar angle."""

    quad = 0  # quadrant
    x, y = point_a[0], point_a[1]  # this is done specifically if point a has more info
    xd, yd = point_b[0], point_b[1]
    xdelta = x - xd
    ydelta = y - yd

    # get quadrant based on position
    if xdelta < 0 and ydelta <= 0:
        quad = 2
    elif xdelta < 0 and ydelta > 0:
        quad = 3
    elif xdelta > 0 and ydelta > 0:
        quad = 4
    else:
        if xdelta == 0 and ydelta > 0:
            quad = 1  # 90 degrees
        elif xdelta == 0 and ydelta < 0:
            quad = 4  # 270
        elif xdelta > 0 and ydelta == 0:
            quad = 2  # 180
        else:
            quad = 3

    if xdelta != 0:  # not vertical
        angle = int(math.degrees(math.atan2(ydelta, xdelta)))
        if quad == 4:
            angle = 360 - angle
        elif quad == 3:
            angle = 360 - angle
        elif quad == 2:
            if ydelta == 0:
                pass
            else:
                angle *= -1
        else:
            angle *= -1
    else:
        if y < yd:
            angle = 90
        else:
            angle = 270
    if supress_quad == 0:
        return angle, quad
    else:
        return angle


def get_median_line_width(pix, jump_slice, pixel_test, width, height):

    """reads a single horizontal row, a single vertical column and a digaonal
    path across an image and searches for line crossings or black pixels that
    appear in each path. Measure the width of each of those lines and return
    the width that is in the center of the list"""

    origin = 0, 0

    # get the distance and direction of each path
    diag_dist = int(math.sqrt(width**2 + height**2) * .90)
    vertical_start = int(width/float(2)), 0  # x=width/2, y=0
    horizontal_start = 0, int(height/float(2))  # x=0, y=width/2
    diagonal_angle = get_polar_angle((width, height), origin, 1)

    # create the list of pixels in each row/column/path
    vertical_path = get_pixel_path_from_angle(vertical_start, height, 270, width)
    horizontal_path = get_pixel_path_from_angle(horizontal_start, width, 0, height)
    diag_path = get_pixel_path_from_angle(origin, diag_dist,
                                          diagonal_angle, 1, height)

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

    x = 80
    avg_init = []
    for yi in range(6):
        mav_pix = pix[x, yi]
        avg_init.append(mav_pix[0])
    avg_start = sum(avg_init)/float(6)

    x = 80
    list_of_blue_coords = []
    list_of_blue_colors = []
    for yval in range(IMHEIGHT - 4):
        pixval = pix[x, yval]

        if avg_start - 20 <= pixval[0] <= avg_start + 20:
            del avg_init[0]
            avg_init.append(pixval[0])
            avg_start = sum(avg_init)/float(6)
        else:
            pair = x, yval
            list_of_blue_coords.append(pair)
            list_of_blue_colors.append(pixval)

    distances = [calc_euclid_dist(coord, list_of_blue_coords[ind -1]) for ind, coord in enumerate(list_of_blue_coords)][1:]
    gaps = [dinga for dinga in distances if dinga > 10]
    if gaps > 8:  # have to have more than 8 lines
        variance = calc_variance(gaps, 1)
        if variance < 10:
            return True, list_of_blue_colors
        else:
            return False, []
    else:
        return False, []


def remove_lines(lined_image, line_colors, IMWIDTH, IMHEIGHT):

    """Remove the lines from an drawing that was drawn on lined paper"""

    red_range = list(set([lined[0] for lined in line_colors]))
    green_range = list(set([lined[1] for lined in line_colors]))
    blue_range = list(set([lined[2] for lined in line_colors]))
    sorted_red = sorted(red_range, reverse=True)
    sorted_green = sorted(green_range, reverse=True)
    sorted_blue = sorted(blue_range, reverse=True)

    for ycoord in range(IMHEIGHT):
        for xcoord in range(IMWIDTH):

            local_pixval = lined_image[xcoord, ycoord]
            # lower levels of red means a bluer line
            if (sorted_red[-1] - 8 <= local_pixval[0] <= sorted_red[0] + 8 and
               sorted_green[-1] - 3 <= local_pixval[1] <= sorted_green[0] and
               sorted_blue[-1] - 3 <= local_pixval[2] <= sorted_blue[0]):

                red = random.randint(158, 195)
                green = random.randint(158, 195)
                blue = random.randint(158, 195)
                lined_image[xcoord, ycoord] = (red, green, blue)


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
