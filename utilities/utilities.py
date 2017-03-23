#-------------------------------------------------------------------------------
# Name:        utilities
# Manifest:
#    sortDict - Sorts dictionary keys, specifically the anlge:coord dictionary
#    getCenter - used in the readCircle
#    getSlope - used several places
#    getQuad - gets the quadrant
#    addAngles - Used to generate the number pairs on either side of line
#    getAngle -
#    checkWithin - determines if two numbers are n apart or less
#    cullDups  - gets rid of duplicates in a list of coordinates
#
#-------------------------------------------------------------------------------
import math

def flatten_coords(coords, imwidth):

    xcoord, ycoord = coords
    number_to_the_start_of_row = ycoord * imwidth
    flat_value = number_to_the_start_of_row + xcoord
    return flat_value


def matrixize(coord_points_list):

    flat_list = []
    for coord_tup in coord_points_list:
        matrix_flat = flatten_coords(coord_tup)
        combine = matrix_flat, coord_tup[2]
        flat_list.append(combine)
    return flat_list


def calc_euclid_dist(a, b, round=0, signed=0):

    """takes two coordinates a and b and gets the distance between
    them using a**2 + b**2 = c**. Rounding is optional set it to 1 to send
    raw distance."""

    x, y = a
    xd, yd = b
    if a == b:
        return 1
    else:
        distance_squared = abs(x-xd)**2 + abs(y-yd)**2
        distance = math.sqrt(distance_squared)

    if round == 0:
        return int(distance)
    else:
        return distance


def sort_branches(graph, cluster_id, branch_ids):

    line_list = []
    for item in branch_ids:

        branch = graph.get_branch_list(cluster_id, item)
        start = branch[0].line_count
        pair = start, item
        line_list.append(pair)

    sorted_list = sorted(line_list)
    strip_sorted = [slist[1] for slist in sorted_list]
    return strip_sorted


def populate_array_with_coords(coo_flat_dict, IMWIDTH, IMHEIGHT):

    """Take a dictionary with key as the x,y coordinates and the value as
    the flat value and put it in a matrix data structure """

    matrix   = []
    #create rows of lists populating the coordinate locations with the flat
    # values and filling in empty coords with zero
    for row in range(IMWIDTH):

        temp_array_list = []

        #if the coord is in the flat_dictionary key then fill it
        # with that coordinate with the flat value otherise enter zero

        for column in range(IMHEIGHT):
            flat_coords = row, column
            if flat_coords in coo_flat_dict:
                flats = flatten_coords(flat_coords, IMWIDTH)
                temp_array_list.append(flats)  # was flats switch to 255
            else:
                temp_array_list.append(0)   #otherwise enter zero

        matrix.append(temp_array_list)
        #append the list to the matrix list so we have list of rows which will
        #go into an numpy array

    return matrix


def matrixize_coord_points(coord_points_list, IMWIDTH):

    """Take a tuple list of x, y coordinates and flattens the coord into an
    integer representing their matrix location and creates a dictionary
    of {flat_value:coords}"""

    flat_dict = {}

    for coord in coord_points_list:
        pair, z = coord
        flatval = flatten_coords(pair, IMWIDTH)
        flat_dict[pair] = flatval
    return flat_dict


def sortKeys(x,y):  # Sort dictionary pairs

    """Utility function to return the lower value"""

    return cmp(x[0],y[0])


def getSlope(x, y, xd, yd):

    """Divides the deltas"""

    if xd == x and yd < y:
        slope = 0
    elif xd == x and yd > y:
        slope = 270
    else:
        slope = (yd - y)/float(abs(xd - x))

    return int(slope)


def getQuad(x, y, xcenter, ycenter):

    """ get_quadrant takes the center point of a circle (x, y) and a point on
    circumfrence and returns which quadrant the point on the circle is
    found. """

    if x > xcenter and y <= ycenter:
        q = 1
    elif x <= xcenter and y < ycenter:
        q = 2
    elif y >= ycenter and x < xcenter:
        q = 3
    elif y > ycenter and x >= xcenter:
        q = 4

    return q


def addAngles(arc1, arc2, ycenter):

    """ add_2_Angles takes the center point of a circle (x, y) and two points
    on a circumfrence of the circle and returns the sum of the angles"""

    qa = get_quadrant(x,y,xcenter,ycenter)
    qb = get_quadrant(xnew, ynew, xcenter, ycenter)

    anga = get_angle(x,y,xcenter,ycenter,qa)
    angb = get_angle(xnew,ynew,xcenter,ycenter,qb)
    aplusb = abs(angb - anga)
    return aplusb


def getAngle(x,y,xd,yd, q):

    """ ret_angle takes a coordinate point on a circle and returns
    the angle between them. x,y is the center of the circle, xd, yd
    is the point on the circumfrence and the q is the quadrant"""

    if xd == x and yd < y:  # if straight up angle is 90
        ang = 90
    elif xd == x and yd > y:  # if straight down angle is 270
        ang = 270
    else:
        slope = (yd - y)/float(abs(xd - x))
        ang = int(math.degrees(math.atan(slope)))

        if q == 1:
            ang = abs(ang)
        elif q == 2:
            ang = ang + 180
        elif q ==3:
            ang = ang + 180
        elif q == 4:
            ang = 360 - ang

    return ang

def getAngleFromSlope(x, y, xd, yd):

    if x > xd and y > yd:
        quad = 2
    elif x < xd and y < yd:
        quad = 4
    elif x < xd and y > yd:
        quad = 1
    else:
        quad = 3

    if xd == x and yd < y:  # if straight up angle is 90
        ang = 90
    elif xd == x and yd > y:  # if straight down angle is 270
        ang = 270
    else:
        slope = (yd - y)/float(abs(xd - x))
        ang = int(math.degrees(math.atan(slope)))

    return ang


def get_SlopeFromAngle(angle, radius):

    """This gets the slope of an angle give a circle diameter"""
    if angle < 270:
        angle = angle - 90
    else:
        angle = angle - 180 - 34
    adjacent = math.cos(math.radians(angle))*radius
    opposite = math.tan(math.radians(angle))*adjacent
    return adjacent, opposite
