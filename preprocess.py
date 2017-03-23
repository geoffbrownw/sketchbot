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

        if 0 <= x <= imwidth - 7 and y + yval <= imheight - 7:
            pixval = pix[x, y + yval]  # this is diagonal up??
            mavg.append(pixval)
            x -= over
        else:
            # print x, y
	    pass
    avg = int(sum(mavg)/float(list_size))
    return avg, mavg  # return average and the average list??


def get_nw_bound_of_drawing(piximage, width, height):

    """Find the first instances of black pixels in the nw corner"""

    p = 0
    coord = []
    pair = 0
    low_y = height
    high_y = 0
    
    for x in range(6, width-8, 1):
        pixcount = 0
        avg, mavg = getMAVG(x, 0, 6, piximage, width, height)
	
        # a = [x for x in (itertools.permutations(range(z),2)) if x[0]+x[1]==z-1]
        # trick ass diagonal coordinate generator, unfortunately its slow :(
        for y in range(1, height - 6):  # was 40
            if coord and y > low_y:
                high_y = y
                break  # as soon as you hit a black pixel stop going up
            pixval = piximage[x, y]
	     
            if pixval <= avg - avg/float(4) and pixcount >= 2:  # was >=6
                pair = x, y
                coord.append(pair)  # this just saves the first occurrence over 3
                low_y = y
            elif pixval <= avg-avg/float(4): # if pixval is 25% lower than avg trigger
                pixcount += 1
            else:
                pixcount = 0
                p += 1
                if p == 5:  # was 6
                    p = 0
            mavg[p] = pixval
            avg = int(sum(mavg)/float(6)) # generate a new moving average

    return coord[0][0], high_y


def get_se_bound_of_drawing(piximage, width, height, west, north):

    """

    :param piximage:
    :param width:
    :param height:
    :param west:
    :param north:
    :return:
    """

    p = 0
    coord = []
    westernmost_xval_in_image = width
    southernmost_yval_in_image = height
    high_y = 0
    
    for x in range(width-7, west - 10, -1):
        pixcount = 0
	# print southernmost_yval_in_image
        avg, mavg = getMAVG(x, 0, 6, piximage, width, height)
	
        # a = [x for x in (itertools.permutations(range(z),2)) if x[0]+x[1]==z-1]
        # trick ass diagonal coordinate generator, unfortunately its slow :(
        for y in range(height - 6, 10, -1):
	    
            pixval = piximage[x, y]  # get pixel value

            if pixval <= avg * .75 and pixcount >= 4:
                pair = x, y
                coord.append(pair)
                southernmost_yval_in_image = y
            elif pixval <= avg * .75:
                pixcount += 1
            else:
                pixcount = 0
                p += 1
                if p == 5:
                    p = 0
            mavg[p] = pixval
            avg = int(sum(mavg)/float(6))
    ycos = max([dank[1] for dank in coord])
    
    return coord[0][0], 285
