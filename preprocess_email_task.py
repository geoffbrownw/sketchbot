#/usr/bin/python
# import pika
from os.path import isfile, join
from os import listdir
from celery import Celery
from tasks import preprocess_new_email
# from db_tasks import insert_thumb_to_mysql
#    RABBITMQ MESSAGING WORKER QUEUE
# credentials = pika.PlainCredentials('sketchbot_user', 'Bosch2017')
# parameters = pika.ConnectionParameters('localhost', 5672, 'sketchbot_vhost', credentials)
# create connection to rabbitmq
# connection = pika.BlockingConnection(parameters)

# open a channel to postoffice
# channel = connection.channel()
# name the channel
# channel.queue_declare(queue='task_queue', durable=True)

app = Celery('foom', broker='amqp://sketchbot_user:Bosch2017@localhost')
# create a message to deliver

def get_filenames_from_directory(mypath='/home/jpegsnatcher/unprocessed'):
    
    """ Get all the emails from a synced directory unprocessed  and call the preprocess_new_image
    celery workers to start processes on the images in the email.
    1. Extract image from email
    2. Create thumbnail from image
    3. Threshold the thumbnail
    4. Insert the thumbnail into the mysql/dankbro2_images db at foom.co
    """
   
    # Get the filenames in directory unprocessed
    # need to do lots of preprocessing to make sure filenames are real jpgs and not
    # malicious and that they exist
    all_filenames_in_dir = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    # For each one strip the image out, thumbnail the image and threshold the thumbnail.
    
    for email in all_filenames_in_dir:
	image_timestamp = preprocess_new_email(email)  # calls celery task

if __name__ == '__main__':
    # preprocess_email_tasks gets called from the watching of an email directory
    get_filenames_from_directory()
