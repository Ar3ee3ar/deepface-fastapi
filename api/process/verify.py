from deepface import DeepFace
import os
# from .connect_db import mydb
import mysql.connector
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import cv2
# import time

def rect_pic(img,position):
    img_pil = Image.open(BytesIO(base64.b64decode(img)))
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_BGR2RGB)
    start_point = (int(position['x']), int(position['y']))
    end_point = (int(position['x'] + position['h']), int(position['y'] + position['w']))
    color = (0, 255, 0)
    thickness = 2
    image = cv2.rectangle(img_cv, start_point, end_point, color, thickness)
    res,img_jpg = cv2.imencode(".jpg",image)
    return (base64.b64encode(img_jpg.tobytes()))

def pair_verify(search_pic,dir_list):
    all_result = []
    all_time_verify = 0
    found_pic = []
    for i in range(len(dir_list)):
        result = DeepFace.verify(img1_path = search_pic, img2_path = "data:image/,"+dir_list[i][2] ,enforce_detection= False, model_name= "Facenet", detector_backend ='opencv')
        if(result['verified']):
            all_result.append(dir_list[i][1])
            all_time_verify = all_time_verify + int(result["time"])
            pic = rect_pic(dir_list[i][2],result['facial_areas']['img2'])
            found_pic.append(pic)

    # print(search_pic + " is the same as")
    for i in range(len(all_result)):
        print(str(i) + '. '+all_result[i])

    return (all_result,all_time_verify,found_pic)

def filter(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = mysql.connector.connect(
        host="host.docker.internal",
        user="root",
        password="test1234",
        database="pic",
        port = 3306
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM pic WHERE Dt_create BETWEEN '"+start_dt+"' AND '"+end_dt+"'")
    myresult = mycursor.fetchall()
    return myresult

def search (start_dt,end_dt,search_pic):
    img_db = filter(start_dt,end_dt)
    found_name, time, found_img = pair_verify(search_pic,img_db) # 0-ID, 1-Name, 2-PhotoB64, 3-Dt_create
    return (found_name, time, found_img)

