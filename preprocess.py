#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      GeoffB
#
# Created:     05/09/2014
# Copyright:   (c) GeoffB 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from collections import deque

def moving_average(iterable, n=3):
    # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
    # http://en.wikipedia.org/wiki/Moving_average
    it = iter(iterable)
    d = deque(itertools.islice(it, n-1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / float(n)


def get_weighted_mavg(new, last_list):

    right_side = [new]  # weight the recent by adding twice
    swath = deque(last_list, maxlen=5)
    swath.popleft()
    swath.extend(right_side)

    avg = sum(swath)/len(swath)
    return avg, list(swath)


def getMAVG(x, y, list_size, pix, imwidth, imheight, over=1):

    """Send in a x, y value a number of values to calculate ahead and the
    pixel view to read it from. Return the average pixel value of the pixels"""
    mavg = []
    for yval in range(list_size):
        if x <= imwidth and y + yval <= imheight:
            pixval = pix[x, y + yval]  # this is diagonal up??
            mavg.append(pixval)
            x -= over
        else:
            # print x, y
	    pass
    avg = sum(mavg)/float(list_size)
    return avg, mavg  # return average and the average list??


def get_nw_bound_of_drawing(piximage, w, h):

    """Find the first instances of black pixels in the nw corner"""

    p = 0
    coord = []
    pair = 0
    low_y = h
    high_y = 0
    for x in range(30, w-5, 4):
        pixcount = 0
        avg, mavg = getMAVG(x, 0, 6, piximage, w, h)
        # a = [x for x in (itertools.permutations(range(z),2)) if x[0]+x[1]==z-1]
        # trick ass diagonal coordinate generator, unfortunately its slow :(
        for y in range(30, h - 5):  # was 40
            if coord and y > low_y:
                high_y = y
                break
            pixval = piximage[x, y]
            if pixval <= avg - avg/float(5) and pixcount >= 6:
                pair = x, y
                coord.append(pair)
                low_y = y
            elif pixval <= avg-avg/float(5):
                pixcount += 1
            else:
                pixcount = 0
                p += 1
                if p == 6:
                    p = 0
            mavg[p] = pixval
            avg = int(sum(mavg)/float(6))
    return coord[0][0], high_y


def get_se_bound_of_drawing(piximage, w, h, west, north):

    """

    :param piximage:
    :param w:
    :param h:
    :param west:
    :param north:
    :return:
    """

    p = 0
    coord = []
    low_y = h
    high_y = 0
    for x in range(w - 1, west - 10, -1):
        pixcount = 0
        avg, mavg = getMAVG(x, 0, 6, piximage, w, h)
        #        a = [x for x in (itertools.permutations(range(z),2)) if x[0]+x[1]==z-1]
        # trick ass diagonal coordinate generator, unfortunately its slow :(
        for y in range(h - 5, north, -1):
            if coord and y < low_y:
                high_y = y
                break
            pixval = piximage[x, y]
            if pixval <= avg - avg/float(5) and pixcount >= 5:
                pair = x, y
                coord.append(pair)
                low_y = y
            elif pixval <= avg - avg/float(5):
                pixcount += 1
            else:
                pixcount = 0
                p += 1
                if p == 6:
                    p = 0
            mavg[p] = pixval
            avg = int(sum(mavg)/float(6))
    return coord[0][0], high_y

