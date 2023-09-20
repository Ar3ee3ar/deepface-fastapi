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

def connector():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    mydb = mysql.connector.connect(
        # host="host.docker.internal",
        # host="192.168.1.119",
        host = os.environ.get('HOST_db'),
        user=os.environ.get('USER_db'),
        password=os.environ.get('PASSWORD_db'),
        database=os.environ.get('DATABASE_db'),
        port = os.environ.get('PORT_db')
    )
    # mycursor = mydb.cursor()
    return mydb

def filter(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap WHERE create_time BETWEEN '"+start_dt+"' AND '"+end_dt+"' order by create_time")
    # mycursor.execute("SELECT ID,PicPath, Dt_create FROM pic WHERE Dt_create BETWEEN '"+start_dt+"' AND '"+end_dt+"' ORDER BY Dt_create")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult

def filter_id(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id FROM kiosk_robot_snap WHERE create_time BETWEEN '"+start_dt+"' AND '"+end_dt+"' order by create_time")
    # mycursor.execute("SELECT ID FROM pic WHERE Dt_create BETWEEN '"+start_dt+"' AND '"+end_dt+"' ORDER BY Dt_create")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult

def get_all():
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap order by create_time")
    # mycursor.execute("SELECT ID,PicPath,Dt_create FROM pic ORDER BY Dt_create")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult

def filter_greater_than(store_date):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap WHERE create_time > '"+store_date+"' order by create_time")
    # mycursor.execute("SELECT ID FROM pic WHERE Dt_create > '"+store_date+"' ORDER BY Dt_create")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult