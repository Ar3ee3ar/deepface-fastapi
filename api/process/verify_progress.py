from deepface import DeepFace
import os
from os.path import join, dirname
# from .connect_db import mydb
import mysql.connector
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import cv2
from dotenv import dotenv_values,load_dotenv
# import time

def filter(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    print('host: ',os.environ.get('HOST'))
    print('USER: ',os.environ.get('USER'))
    print('PASSWORD: ',os.environ.get('PASSWORD'))
    print('DATABASE: ',os.environ.get('DATABASE'))
    print('PORT: ',os.environ.get('PORT'))
    mydb = mysql.connector.connect(
        # host="host.docker.internal",
        # host="192.168.1.119",
        host = os.environ.get('HOST'),
        user=os.environ.get('USER'),
        password=os.environ.get('PASSWORD'),
        database=os.environ.get('DATABASE'),
        port = os.environ.get('PORT')
    )
    mycursor = mydb.cursor()
    # mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap WHERE create_time BETWEEN '"+start_dt+"' AND '"+end_dt+"' order by create_time")
    mycursor.execute("SELECT ID,PicPath, Dt_create FROM pic WHERE Dt_create BETWEEN '"+start_dt+"' AND '"+end_dt+"'")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult