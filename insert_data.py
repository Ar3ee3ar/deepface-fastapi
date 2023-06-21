import mysql.connector
import os
import cv2
import base64
import random
import time

count = 0

def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="test1234",
  database="pic"
)

mycursor = mydb.cursor()

path = "deepface/more_pic/"
dir_list = os.listdir(path)
dir_list = ['emma1.jpg']
# img = open("C:/Users/acer/Desktop/face_api/idinvert_pytorch/examples/000001.png", 'rb')
# with open("yourfile.ext", "rb") as image_file:
for i in range(len(dir_list)):
    name = dir_list[i].split('.')
    # if(name[1] == 'png'):
    with open(path+dir_list[i], "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    sql = "INSERT INTO pic (Name, PhotoB64, Dt_create) VALUES (%s, %s, %s)"
    val = (dir_list[i], encoded_string, random_date("2008-1-1 1:30:00", "2008-2-1 4:50:00", random.random()))
    mycursor.execute(sql, val)
    count = count + 1

mydb.commit()

print(count, "record inserted.")