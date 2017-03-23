import os
import imghdr
import sys
import re
import email
from os.path import isfile, join
import errno
import mimetypes
import subprocess
import datetime
from PIL import Image, ExifTags, ImageFilter
import time
from threshold import calibrate_black_threshold_thumb, calculate_threshold_range
from threshold import create_threshold_map, get_median_line_width_thumbnail
from skeletonize import skeletonize_image
from preprocess import get_nw_bound_of_drawing, get_se_bound_of_drawing
from utilities.utilities import populate_array_with_coords, matrixize_coord_points
import numpy as np
from celery import Celery
import mysql.connector
import base64
import copy
import redis

# create the celery app tasker connected to rabbitmq
app = Celery('foom', broker='amqp://sketchbot_user:Bosch2017@localhost')


@app.task
def insert_thumb_to_mysql(filename):

    """
        Take the image and insert into a remote foom webfacing mysql db
    """
    image_directory = "/home/jpegsnatcher/processed/thresh_thumbs/"
    email_directory = "/home/jpegsnatcher/processed/"
    path_to_image = image_directory + filename  # this is a thumbnail name
    path_to_email = email_directory
    
    # process the filename to pull out email and insert to mqsql on foom.co

    email_filename = copy.deepcopy(filename)
    # in this file ending with .ksh is the sender email and the original jpg name
    email_split_on_underscore = email_filename.split('_')[-1]
    filename_split_on_period = email_split_on_underscore.split('.')[0]

    clean_name_containing_email = 'part' + filename_split_on_period + '.ksh'
    clean_email_path = email_directory + clean_name_containing_email

    try:
        with open(clean_email_path) as f:
            data = f.read()
            senders_email = data.split(' ')[0] # pull out the email addy from front
	    original_jpg = data.split(' ')[-1]
    except:
	print 'blew up'

    image_filename = copy.deepcopy(filename)  # thumbnail name
    timestamp_split = image_filename.split('.')[0]
    timestamp = int(timestamp_split.split('_')[-1])
    blob_value = open(path_to_image, 'rb').read()   # binary blob thumbnail

    thumbnail_file = filename.split('_')[-1]  # get the timestamp

    sql = "INSERT INTO Thumbnails(Email, Filename, Thumb, Jpg) VALUES(%s, %s, %s, %s)"
    args = (senders_email, thumbnail_file, blob_value, original_jpg)
    # connect to remote mysql db to insert thumbnails
    connection = mysql.connector.connect(user='dankbro2_jpeg', password='Bosch2017!',
                            host='174.127.110.239',
                            database='dankbro2_images')

    cursor = connection.cursor()
    cursor.execute(sql, args)
    cursor.close()
    connection.commit()
    connection.close()


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

def initialize_user_session(email_address, filename):

    """Create a redis entry to save progress data"""

    r = redis.StrictRedis()
    user_key = 'user:' + email_address + ':filename'
    if r.exists(user_key):
	pass  # trying to add another image before the end
    else:
        r.lpush(user_key, filename)
        r.expire(email_address, 6000)

@app.task
def strip_image_from_email(email_filename):

    """ Receive an email message from unprocessed and parse it for the jpeg and user info
    create a unique filename for task managment"""

    unique_file_id = None
    email_read_location = join("/home/jpegsnatcher/unprocessed/", email_filename)

    with open(email_read_location) as fp:
	# parse the email for user info and timestamp
	msg = email.message_from_file(fp)
	sender = msg['from'].split()[-1]
	address = re.sub(r'[<>]', '', sender)
	subject = msg['subject'].split()
	start_time = msg['date']
	raw_date = msg.get('date')
	parsed_date = email.utils.parsedate(raw_date)
	time_stamp = time.mktime(parsed_date)
	
	mysql_id = ""
	# walk down the message data
	for part in msg.walk():
	    if part.get_content_maintype() == 'multipart':  # if attachment
		continue
	    filename = part.get_filename()

	    if not filename:  # if there is no attachment create a filename to save data
		ext = mimetypes.guess_extension(part.get_content_type())
		if not ext:  # if not an html file or jpg this does not get read unless another attachement
		    ext = '.txt'
		filename = 'part%03d%s' % (time_stamp, ext)
	    else:  # this executes all the time unles something went wrong
		filename = str(time_stamp) + filename  # the timestamp plus the jpeg
	
	    # write a binary mode jpg file
	    with open(os.path.join("/home/jpegsnatcher/processed/", filename), 'wb') as fp:
                
		if 'jpg' in filename or 'png' in filename:
		    fp.write(part.get_payload(decode=True))
		    unique_file_id = filename
		if 'ksh' in filename:
		    address_split = address + ' '
		    fp.write(address_split)
		    mysql_id = filename

    # wait until processing is over then append the new full sized image name into the html file
    if mysql_id:
	unique_filename = str(mysql_id)
	
        with open(os.path.join("/home/jpegsnatcher/processed/", unique_filename ), "a") as myfile:
            myfile.write(str(unique_file_id))
    initialize_user_session(address, unique_file_id)

    # remove the email from unprocessed
    p1 = subprocess.Popen(['rm', email_read_location])
    return unique_file_id  # filename returned is the original attachement name plus the timestamp


@app.task(acks_late=True)
def create_thumbnail_from_jpeg(jpeg_file):

    """Take in a fullsize jpg and create a thumbnail"""

    basewidth = 300
    # for infile in sys.argv[1:]:
    
    infile = '/home/jpegsnatcher/processed/' + jpeg_file
    stripname = jpeg_file.split('.')[0] # just pull the timestamp off
   
    outfile = '/home/jpegsnatcher/processed/' + stripname  + ".thumbnail" + '.jpg'
    if infile != outfile:
        try:
            img = Image.open(infile)  # .convert('L')
	    # this is in case the image is rotated
            # image=Image.open(os.path.join(path, fileName))
	    # if hasattr(im, '_getexif'):
	    #	if im._getexif():
            #        for orientation in ExifTags.TAGS.keys():
            #            if ExifTags.TAGS[orientation]=='Orientation': break 
            #        exif=dict(im._getexif().items())
            #
            #        if exif[orientation] == 3:
            #            im=im.rotate(180, expand=True)
            #        elif exif[orientation] == 6:
            #            im=im.rotate(270, expand=True)
            #        elif exif[orientation] == 8:
            #            im=im.rotate(90, expand=True)

            # im.thumbnail((THUMB_WIDTH , THUMB_HEIGHT), Image.ANTIALIAS)
	    
            # image.save(os.path.join(path,fileName))
            # im.thumbnail(size, Image.ANTIALIAS )

	    # keep the aspect ratio of the thumbnail width == 300
	    wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
	    img = img.resize((basewidth, hsize), Image.ANTIALIAS)

	    img.save(outfile, "JPEG")
	    return stripname + '.thumbnail' + '.jpg'
        except IOError:
            print "cannot create thumbnail for", infile


@app.task
def threshold_thumbnail(filename):
   
    processed_directory = "/home/jpegsnatcher/processed/"
    image_file_location = processed_directory + filename
    
    try:
	
        im_blur = Image.open(image_file_location).convert('L')
	
        # im_blur = im_blur.filter(ImageFilter.GaussianBlur(radius=2))
        pix = im_blur.load()
        IMWIDTH, IMHEIGHT = im_blur.size
        im_array = np.array(im_blur, dtype='int64')  # create numpy array for integral
        integral_image = im_array.cumsum(0).cumsum(1)  # create integral image
	
        # img_as_npa = np.asarray(im_blur)
    except:
	print image_file_location, 'here'
        return -1

    MEDIAN_PIXEL = 127

    threshold_jump, standard_dev, pixval_key, pixval_dev = calibrate_black_threshold_thumb(pix, IMWIDTH, IMHEIGHT)
    jump_slice, pixel_range = calculate_threshold_range(threshold_jump, standard_dev, pixval_key, pixval_dev)

    # median line with needs to better control the read circle and the dimension finding algo
    MEDIAN_LINE_WIDTH = get_median_line_width_thumbnail(pix, jump_slice, pixel_range, IMWIDTH, IMHEIGHT)
    threshold_map = create_threshold_map(jump_slice, pixel_range, MEDIAN_PIXEL, standard_dev)

    # depreciated below alternate method of integral image
    # integral_image = np.cumsum(np.cumsum(im, axis=1), axis=0)

    WEST, NORTH = get_nw_bound_of_drawing(pix, IMWIDTH, IMHEIGHT)
    EAST, SOUTH = get_se_bound_of_drawing(pix, IMWIDTH, IMHEIGHT, WEST, NORTH)
    NW_BOUND = WEST - 2, NORTH - 2
    SE_BOUND = EAST + 2, SOUTH + 2
    
    x_west, y_north = NW_BOUND
    x_east, y_south = SE_BOUND
    # print IMWIDTH, IMHEIGHT, NW_BOUND, SE_BOUND, 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDd'
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
                                    x_west, y_south,
                                    IMWIDTH,
                                    integral_image,
                                    threshold_map)
    try:
        skeleton_dict = matrixize_coord_points(save_coords, IMWIDTH)  # flatten
        matrix2 = build_array_from_grayscale_coords(skeleton_dict, IMWIDTH, IMHEIGHT)
        flat_array = np.asarray(matrix2).astype('uint8')
        im = Image.fromarray(flat_array, 'L')
	# im = im.filter(ImageFilter.BLUR)
        im.load()
        image_to_threshold = 'th_' + filename
        save_file_location = processed_directory + 'thresh_thumbs/' + image_to_threshold
        im.save(save_file_location)
	return image_to_threshold
    except:
	return -1

def preprocess_new_email(filename):
    
    # chain = strip_image_from_email.s(filename) | threshold_image.s()
    # chain = strip_image_from_email.s(filename) | threshold_image.s() | create_thumbnail_from_jpeg.s()
    chain = strip_image_from_email.s(filename) | create_thumbnail_from_jpeg.s() | threshold_thumbnail.s() | insert_thumb_to_mysql.s()
    chain() 

	
if __name__ == '__main__':
    pass
    # thumb_dir = "/home/jpegsnatcher/processed/"
    # files_in_unprocessed_folder = get_filenames_from_directory("/home/jpegsnatcher/unprocessed/")
    # if files_in_unprocessed_folder:
    #	for email_file in files_in_unprocessed_folder:
    # 	    strip_image_from_email(email_file)

