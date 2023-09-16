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
    all_result = {
        "value":[]
    }
    all_time_verify = 0
    found_pic = []
    for i in range(len(dir_list)):
        name_pic_file = dir_list[i][1].split('/')
        # file_type = name_pic_file[-1].split('.')
        name_path = '/var/www/html/pic/'+name_pic_file[-1]
        if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
            # print(dir_list[i][1])
            try:
                result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet", detector_backend ='opencv')
                if(result['verified'] and result['distance'] < 0.25):
                        # all_result.append(dir_list[i][1])
                        # all_time_verify = all_time_verify + int(result["time"])
                        # pic = rect_pic(dir_list[i][2],result['facial_areas']['img2'])
                        # found_pic.append(pic)
                        json_pic = {
                            "id":dir_list[i][0],
                            "similarity": (1-result['distance'])
                        }
                        # print(type(pic))
                        # print(type(dir_list[i][3]))
                        all_result["value"].append(json_pic)
            except cv2.error as e:
                # print("OpenCV Error:", e)
                print("Custom error message: Unable to decode image.")
                pass

    # # print(search_pic + " is the same as")
    # for i in range(len(all_result)):
    #     print(str(i) + '. '+all_result[i])

    return (all_result)

def filter(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    mydb = mysql.connector.connect(
        # host="host.docker.internal",
        # host="192.168.1.119",
        host = "192.168.1.119",
        user="exat",
        password="Pwd123456!",
        database="center",
        port = 3306
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap WHERE create_time BETWEEN '"+start_dt+"' AND '"+end_dt+"' order by create_time")
    # mycursor.execute("SELECT name,PhotoB64, Dt_create FROM testDB_verify WHERE Dt_create BETWEEN '"+start_dt+"' AND '"+end_dt+"'")
    myresult = mycursor.fetchall()
    # print(myresult)
    return myresult

def search (start_dt,end_dt,search_pic):
    img_db = filter(start_dt,end_dt)
    # print(img_db)
    all_result = pair_verify(search_pic,img_db) # 0-name, 1-pic path, 2-create_time
    return (all_result)
