#/usr/bin/python
# import pika
from os.path import isfile, join
from os import listdir
from celery import Celery
from tasks import preprocess_new_image
from db_tasks import insert_thumb_to_mysql
#    RABBITMQ MESSAGING WORKER QUEUE
# credentials = pika.PlainCredentials('sketchbot_user', 'Bosch2017')
# parameters = pika.ConnectionParameters('localhost', 5672, 'sketchbot_vhost', credentials)
# create connection to rabbitmq
# connection = pika.BlockingConnection(parameters)

# open a channel to postoffice
# channel = connection.channel()
# name the channel
# channel.queue_declare(queue='task_queue', durable=True)

app = Celery('foom',
	    broker='amqp://sketchbot_user:Bosch2017@localhost/sketchbot_vhost')
# create a message to deliver

def get_filenames_from_directory():
    
    """ Get all the emails from a synced directory of new emails and call the preprocess_new_image
    celery workers to work"""
    
    mypath='/home/jpegsnatcher/unprocessed/'
    # Get the filenames in directory unprocessed
    all_filenames_in_dir = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    # For each one strip the image out, thumbnail the image and threshold the thumbnail.
    
    for email in all_filenames_in_dir:
	image_timestamp = preprocess_new_image(email)
        if image_timestamp != -1:
	    outcome = insert_thumb_to_mysql(image_timestamp)
get_filenames_from_directory()
# connection.close()
