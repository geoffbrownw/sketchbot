from Threshold.threshold import calibrate_black_threshold, calculate_threshold_range, create_threshold_map
from attribs.attribs import get_median_line_width
from preprocess import get_nw_bound_of_drawing, get_se_bound_of_drawing
from Skeletonize.skeletonize import skeletonize_image, generate_generic_arc_path
from utilities.utilities import matrixize_coord_points
from PIL import Image
import numpy as np
from graph import Point

def build_array_from_grayscale_coords(image_dict, width, height):

    """take in a dictionary of key=coordinate, value=flattened coordiate pull out each
    coordinate and insert it into a 2d array as a black pixel value of zero. Initialize the 
    2d array with all white value 255"""

    coord_keys = image_dict.keys()
    two_d_array = [[255 for i in range(width-1)] for j in range(height-1)]

    sorted_coords = sorted(coord_keys)

    # pull out each column by x value
    for coords in sorted_coords:
        if coords:
            x, y = coords
            two_d_array[y][x] = 0

    return two_d_array



def threshold_full_size_image():

    """ Take a jpg image and threshold it so all the black pixels can be returned
    as a list to be used in future processes"""

    try:
        im_blur = Image.open("/home/jpegsnatcher/foom/flange.jpg").convert('L')
        # im_blur = im_blur.filter(ImageFilter.GaussianBlur(radius=2))
        pix = im_blur.load()
        IMWIDTH, IMHEIGHT = im_blur.size
        im_array = np.array(im_blur, dtype='int64')  # create numpy array for integral
        integral_image = im_array.cumsum(0).cumsum(1)  # create integral image
        # img_as_npa = np.asarray(im_blur)
    except:
        print 'no file found'
        exit()

    MEDIAN_PIXEL = 127
    processed_directory = '/home/jpegsnatcher/foom/'
    threshold_jump, standard_dev, pixval_key, pixval_dev = calibrate_black_threshold(pix, IMWIDTH, IMHEIGHT)
    jump_slice, pixel_range = calculate_threshold_range(threshold_jump, standard_dev, pixval_key, pixval_dev)

    # median line with needs to better control the read circle and the dimension finding algo
    MEDIAN_LINE_WIDTH = get_median_line_width(pix, jump_slice, pixel_range, IMWIDTH, IMHEIGHT)

    print MEDIAN_LINE_WIDTH, 'this is median line width'
    print jump_slice, pixel_range, 'this is jump slice and pixeltest'

    threshold_map = create_threshold_map(jump_slice, pixel_range, MEDIAN_PIXEL, standard_dev)

    print threshold_map, 'this is the threshold mapping'
    print threshold_jump, standard_dev, pixval_key, pixval_dev, 'jump and jump_dev'

    # depreciated below alternate method of integral image
    # integral_image = np.cumsum(np.cumsum(im, axis=1), axis=0)

    WEST, NORTH = get_nw_bound_of_drawing(pix, IMWIDTH, IMHEIGHT)
    EAST, SOUTH = get_se_bound_of_drawing(pix, IMWIDTH, IMHEIGHT, WEST, NORTH)
    NW_BOUND = WEST - 2, NORTH - 2
    SE_BOUND = EAST + 2, SOUTH + 2

    x_n, y_n = NW_BOUND
    x_s, y_s = SE_BOUND
    print IMWIDTH, IMHEIGHT, NW_BOUND,SE_BOUND, 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDd'
    # we need to adjust read skeleton radius to account for the line thickness
    # read radius is used several places along with median line width
    # it would be nice to be able to adjust this according to more than just line width, branch length
    if MEDIAN_LINE_WIDTH < 7:  # %50 #thin lines mean we can make radius small
        read_radius = 23  # was 22
    elif 7 <= MEDIAN_LINE_WIDTH <= 12:
        read_radius = 34  # as 27
    elif 12 < MEDIAN_LINE_WIDTH <= 15:
        read_radius = 38
    else:
        read_radius = 45 # thick lines means make radius bigger

    center_coords = (0, 0)
    circle_pattern = generate_generic_arc_path(center_coords, read_radius, 359)
    # avg, mavg = getMAVG(SE_BOUND[0], SE_BOUND[1], 6, pix,  IMWIDTH, IMHEIGHT)
    yends = abs(NW_BOUND[0] - SE_BOUND[0]) + abs(SE_BOUND[1] - NW_BOUND[1])
    # print("--- %s seconds --- start skeletonize" % (time.time() - start_time))
    save_coords = skeletonize_image(pix,
                                    MEDIAN_LINE_WIDTH,
                                    NW_BOUND,
                                    SE_BOUND,
                                    IMHEIGHT,
                                    pixval_dev,  # pixel deviation
                                    pixval_key,
                                    x_n, y_n,
                                    IMWIDTH,
                                    integral_image,
                                    threshold_map)

    try:
        skeleton_dict = matrixize_coord_points(save_coords, IMWIDTH)  # flatte
        matrix2 = build_array_from_grayscale_coords(skeleton_dict, IMWIDTH, IMHEIGHT)
        flat_array = np.asarray(matrix2).astype('uint8')
	
        im = Image.fromarray(flat_array, 'L')

        im.load()
	filename = 'flange.jpg'
        image_to_threshold = 'fullth_' + filename
        save_file_location = processed_directory + image_to_threshold
        im.save(save_file_location)
        
    except:
        print 'fail'



    return im_blur, save_coords, IMWIDTH, IMHEIGHT, MEDIAN_LINE_WIDTH, threshold_map, read_radius

def create_matrix_of_black_points(black_pixels, pixel, IMWDITH, IMHEIGHT, threshold_map, read_radius):


    """Take in a dictionary of black pixels including flat values and coordinates
        return a list of diagonally sorted point class pixel representation prepped
	for use in the graph preprep"""
    center_coords = (0,0)
    circle_pattern = generate_generic_arc_path(center_coords, read_radius, 359)
    radial_black_surrounds = read_skeleton_points(save_coords, pix, IMWIDTH, IMHEIGHT, threshold_map, circle_pattern, read_radius)
    # print("--- %s seconds --- end stock read skeleton_points" % (time.time() - start_time))

    skeleton_dict = matrixize_coord_points(save_coords, IMWIDTH)  # flatten
    matrix = populate_array_with_coords(skeleton_dict, IMWIDTH, IMHEIGHT)  # populate
    flat_array = np.array(matrix)  # numpy array
    stripped_groups = sort_coords_diagonally(radial_black_surrounds)

    del radial_black_surrounds  # must not delete if using pickle!!!!!


    Point.width = IMWIDTH  # set the width for all points
    # this is easily parallel -> This is the point class factory

    collect_clustered_lines = cluster_pixel_rows_diagonally(stripped_groups,
                                                            NW_BOUND, SE_BOUND, IMWIDTH, MEDIAN_LINE_WIDTH)
 
    # print("--- %s seconds --- end stock read skeleton_points" % (time.time() - start_time))

    skeleton_dict = matrixize_coord_points(save_coords, IMWIDTH)  # flatten
    matrix = populate_array_with_coords(skeleton_dict, IMWIDTH, IMHEIGHT)  # populate
    flat_array = np.array(matrix)  # numpy array
    stripped_groups = sort_coords_diagonally(radial_black_surrounds)

    # del radial_black_surrounds  # must not delete if using pickle!!!!!

    ###import csv
    ##
    ####with open('terms.csv',"w") as f:
    ####    csv.register_dialect("custom", delimiter=" ", skipinitialspace=True)
    ####    writer = csv.writer(f, dialect="custom")
    ####    for term in sterm_list:   #probably have to change these to skeleton_list
    ####        writer.writerow(term)
    ##
    ###line_list = []
    ####term_list = []
    ####import csv
    ####f = open('terms.csv', 'rt')
    ####
    ####try:
    ####    reader = csv.reader(f, delimiter=' ')
    ####    for row in reader:
    ####        a, b, c = row[0],row[1],row[2:] # changed this from a,b,c = row
    ####        row = int(a), int(b),  list(c)
    ####        term_list.append(row)
    ####finally:
    ####    f.close()
    ##
    ##
    ####sterm_list = sorted(term_list, key = itemgetter(0, 1))
    ##
    ##########################################################################
    # This is the heart of the Graph creation algorithm below.
    # #list of lone points and clusters of points is collect_cluster_lines

    Point.width = IMWIDTH  # set the width for all points
    # this is easily parallel -> This is the point class factory

    collect_clustered_lines = cluster_pixel_rows_diagonally(stripped_groups,
                                                            NW_BOUND, SE_BOUND, IMWIDTH, MEDIAN_LINE_WIDTH)

if __name__ == '__main__':

    
    pixel_img, saved_coords, imwidht, imheight, mlw, threshold_map, read_radius = threshold_full_size_image()
    # create_matrix_of_black_pixel_points(save_coords, pixel_img, imwidth, imheight, threshold_map, read_radius) 
