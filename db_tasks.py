from celery import Celery
import mysql.connector
import base64
import copy
from os.path import isfile, join
from os import listdir


def insert_thumb_to_mysql(filename):

    """
        Take the image and insert into a remote foom webfacing mysql db
    """
    image_directory = "/home/jpegsnatcher/processed/thresh_thumbs/"
    path_to_image = image_directory + filename
    # connect to remote mysql db to insert thumbnails
    connection = mysql.connector.connect(user='dankbro2_jpeg', password='Bosch2017!',
                            host='174.127.110.239',
                            database='dankbro2_images')
    re_filename = copy.deepcopy(filename)
    timestamp_split = re_filename.split('.')[0]
    timestamp = int(timestamp_split.split('_')[-1])       
    blob_value = open(path_to_image, 'rb').read()
    sql = "INSERT INTO Thumbnails(Filename, Thumb) VALUES(%s, %s)"
    args = (filename, blob_value)
    cursor = connection.cursor()
    cursor.execute(sql, args)
    cursor.close()
    connection.commit()
    connection.close()

if __name__ == '__main__':
    mypath = '/home/jpegsnatcher/processed/thresh_thumbs/'
    files_in_directory = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for thumbs in files_in_directory:
        insert_thumb_to_mysql(thumbs)    
