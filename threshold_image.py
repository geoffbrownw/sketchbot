from threshold import calibrate_black_threshold, calculate_threshold_range, create_threshold_map, get_median_line_width
from PIL import Image
from skeletonize import skeletonize_image
import numpy as np
from preprocess import bound_nw_drawing, bound_se_drawing
from utilities.utilities import populate_array_with_coords, matrixize_coord_points


def build_array_from_grayscale_coords(image_dict, width, height):

    coord_keys = image_dict.keys()
    two_d_array = [[255 for i in range(height-1)] for j in range(width-1)]

    sorted_coords = sorted(coord_keys)

    # pull out each column by x value
    for coords in sorted_coords:
        if coords:
            x, y = coords
            two_d_array[x][y] = 0

    return two_d_array

if __name__ == '__main__':

    try:
        im_blur = Image.open("/home/jpegsnatcher/foom/thumby.jpg")  # .convert('L')
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

    threshold_jump, standard_dev, pixval_key, pixval_dev = calibrate_black_threshold(pix, IMWIDTH, IMHEIGHT)
    jump_slice, pixel_range = calculate_threshold_range(threshold_jump, standard_dev, pixval_key, pixval_dev)
    
    # median line with needs to better control the read circle and the dimension finding algo
    MEDIAN_LINE_WIDTH = get_median_line_width(pix, jump_slice, pixel_range, IMWIDTH, IMHEIGHT)
    
    threshold_map = create_threshold_map(jump_slice, pixel_range, MEDIAN_PIXEL, standard_dev)
    
    # depreciated below alternate method of integral image
    # integral_image = np.cumsum(np.cumsum(im, axis=1), axis=0)

    WEST, NORTH = bound_nw_drawing(pix, IMWIDTH, IMHEIGHT)
    EAST, SOUTH = bound_se_drawing(pix, IMWIDTH, IMHEIGHT, WEST, NORTH)
    NW_BOUND = WEST - 2, NORTH - 2
    SE_BOUND = EAST + 2, SOUTH + 2

    x_n, y_n = NW_BOUND
    x_s, y_s = SE_BOUND
    
    # we need to adjust read skeleton radius to account for the line thickness
    # read radius is used several places along with median line width
    # it would be nice to be able to adjust this according to more than just line width, branch length

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
   
    skeleton_dict = matrixize_coord_points(save_coords, IMWIDTH)  # flatten
    # matrix = populate_array_with_coords(skeleton_dict, IMWIDTH, IMHEIGHT)  # populate list of lists
    matrix2 = build_array_from_grayscale_coords(skeleton_dict, IMWIDTH, IMHEIGHT)
    flat_array = np.asarray(matrix2).astype('uint8')

    im = Image.fromarray(flat_array, 'L')
    im.load()
    im.save("/home/jpegsnatcher/processed/your_file.jpeg")

    # write jpeg image from raw data in python without pil
    # def write_png(buf, width, height):
    #     """ buf: must be bytes or a bytearray in Python3.x,
    #         a regular string in Python2.x.
    #     """
    #     import zlib, struct
    #
    #     # reverse the vertical line order and add null bytes at the start
    #     width_byte_4 = width * 4
    #     raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4]
    #                         for span in range((height - 1) * width_byte_4, -1, - width_byte_4))
    #
    #     def png_pack(png_tag, data):
    #         chunk_head = png_tag + data
    #         return (struct.pack("!I", len(data)) +
    #                 chunk_head +
    #                 struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))
    #
    #     return b''.join([
    #         b'\x89PNG\r\n\x1a\n',
    #         png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
    #         png_pack(b'IDAT', zlib.compress(raw_data, 9)),
    #         png_pack(b'IEND', b'')])


