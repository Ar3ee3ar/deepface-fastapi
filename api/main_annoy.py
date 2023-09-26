import asyncio
from http import HTTPStatus
from typing import Dict, List
from uuid import UUID, uuid4
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from deepface import DeepFace

from starlette.responses import StreamingResponse
import cv2
import io
import numpy as np
import base64
from PIL import Image
import json
import os
from annoy import AnnoyIndex
from tqdm import tqdm
import time

from fastapi import FastAPI, File, UploadFile, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel

# from .face_aging_standalone import main_mani
# import face_aging_standalone
from .process.verify_progress import filter, get_all, filter_id, filter_greater_than,test_filter_deepface
# from .process.annoy_process import u

u = AnnoyIndex(512, 'angular')

def create_annoy():
    # a.unload()
    # try:
    global u
    embeded_list = []
    pass_list = []
    print('load image...')
    dir_list = get_all()

    for i in tqdm(range(len(dir_list))):
        name_pic_file = dir_list[i][1].split('/')
        # file_type = name_pic_file[-1].split('.')
        name_path = '/var/www/html/pic/'+name_pic_file[-1]
        if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
            try:
                embedding_objs = DeepFace.represent(img_path = name_path, model_name= "Facenet512",enforce_detection= False)
                embeded_list.append(embedding_objs[0])
                pass_list.append(dir_list[i][0])
            except cv2.error as e:
                print("Custom error message: Unable to decode image.")
                pass
    f = len(embeded_list[0]["embedding"])  # Length of item vector that will be indexed

    u = AnnoyIndex(f, 'angular')
    u.on_disk_build('db_face.ann')

    print('create index...')
    for i in tqdm(range(len(embeded_list))):
        v = embeded_list[i]["embedding"]
        u.add_item(pass_list[i], v)

    u.build(10) # 10 trees
    # print(dir_list[len(dir_list)-1])
    with open('update_date.txt', 'w') as f:
        f.write(str(dir_list[len(dir_list)-1][2]))
    print('Finish')
    return True
    # except:
    #     return False
create_annoy()
# u.load('db_face.ann') # super fast, will just mmap the file

class Req_search(BaseModel):
    file_path: str
    start_datetime: datetime | None
    end_datetime: datetime | None

class Res_search_value(BaseModel):
    id: int
    similarity: float

class Res_search_main(BaseModel):
    value: List[Res_search_value]

class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = ""
    progress: int = 0
    all_img: int = 0
    result: List[Res_search_value] = [{"id":0,"similarity":0.0}]

app = FastAPI()
jobs: Dict[UUID, Job] = {}  # Dict as job storage
# all_result = {"value":[]}


def long_task(all_result: List, db_list:List, search_pic:str):
    # all_result = {"value":[]}
    all_time_verify = 0
    found_pic = []
    for i in range(len(db_list)):
        name_pic_file = db_list[i][1].split('/')
        # file_type = name_pic_file[-1].split('.')
        name_path = '/var/www/html/pic/'+name_pic_file[-1]
        if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
            try:
                result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet512", detector_backend ='opencv')
                # print(str(result['verified']),' => ',str(result['distance']))
                if(result['verified'] and result['distance'] < 0.35):
                        # all_result.append(dir_list[i][1])
                        # all_time_verify = all_time_verify + int(result["time"])
                        # pic = rect_pic(dir_list[i][2],result['facial_areas']['img2'])
                        # found_pic.append(pic)
                        json_pic = {
                            "id":db_list[i][0],
                            "similarity": (1-result['distance'])
                        }
                        all_result["value"].append(json_pic)
            except cv2.error as e:
                # print("OpenCV Error:", e)
                print("Custom error message: Unable to decode image.")
                pass
    return all_result
    #         jobs[task_id].progress = i+1
    #     jobs[task_id].result = all_result
    # jobs[task_id].status = "completed"
    # for i in range(1, param):  # do work and return our progress
    #     await asyncio.sleep(1)
    #     await queue.put(i)
    # await queue.put(None)


# async def start_new_task(uid: UUID, data: Req_search) -> None:

    

    # queue = asyncio.Queue()
    # task = asyncio.create_task(long_task(queue, start_dt =str(data.start_datetime),end_dt=str(data.end_datetime),search_pic=data.file_path))

    # print(queue.get())
    # while progress := await queue.get():  # monitor task progress
    #     jobs[uid].progress = progress
    # jobs[uid].result = all_result
    # jobs[uid].status = "complete"


# @app.post("/search_deep", status_code=HTTPStatus.ACCEPTED)
# async def task_handler(background_tasks: BackgroundTasks, data: Req_search) -> Job:
#     new_task = Job()
#     jobs[new_task.uid] = new_task
#     dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
#     jobs[new_task.uid].all_img = len(dir_list)
#     jobs[new_task.uid].status = "in_progress"
#     all_result = []
#     background_tasks.add_task(long_task,all_result, new_task.uid,db_list = dir_list,search_pic=data.file_path)
#     return new_task


@app.get("/task/{uid}/status")
async def status_handler(uid: UUID) -> Job:
    return jobs[uid]

@app.get("/create_tree")
def recreate_annoy():
    flag = create_annoy()
    if(flag):
        return {"message": "Finish create data for face verification"}
    else:
        return {"message": "Error"}

# @app.post("/search_tree", status_code=HTTPStatus.ACCEPTED)
# async def task_handler_tree(background_tasks: BackgroundTasks, data: Req_search) -> Job:
#     new_task = Job()
#     jobs[new_task.uid] = new_task
#     dir_list = filter_id(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
#     jobs[new_task.uid].all_img = len(dir_list)
#     jobs[new_task.uid].status = "in_progress"
#     all_result = []
#     background_tasks.add_task(search_tree,all_result, new_task.uid,db_list = dir_list,search_pic=data.file_path)
#     return new_task



def search_tree(all_result: List, db_list:List, search_pic:str):
    # all_result = []
    # dir_list = filter_id(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
    embedding_objs = DeepFace.represent(img_path = search_pic, model_name= "Facenet512",enforce_detection=False, detector_backend ='opencv')
    rank = u.get_nns_by_vector(embedding_objs[0]["embedding"], u.get_n_items(), include_distances=True)
    rank_id = rank[0]
    rank_sim = rank[1]
    db_list_id = [i[0] for i in db_list]
    # print('db_list_id: ',db_list_id)
    # print('tree: ',rank_id)

    i = 0
    for id,sim in zip(rank_id,rank_sim):
        if(id in db_list_id and 1-((sim**2)/2) > 0.65):
            # print('id: ',id,' => sim: ',1-((sim**2)/2))
            json_pic = {
                            "id":id,
                            "similarity": 1-((sim**2)/2)
                        }
            all_result["value"].append(json_pic)
        i = i +1
    #     jobs[task_id].progress = i
    #     jobs[task_id].result = all_result
    # # jobs[task_id].progress = len(db_list_id)
    # jobs[task_id].status = "completed"
    return all_result

@app.post("/verify")
def task_handler_combine(data: Req_search) -> Res_search_main:
    flag_new = False
    f = open("update_date.txt", "r")
    date_db = f.readline()
    f.close() 

    time_db_dt = datetime.strptime(date_db,'%Y-%m-%d %H:%M:%S')
    time_start_dt = datetime.strptime(str(data.start_datetime),'%Y-%m-%d %H:%M:%S')
    time_end_dt = datetime.strptime(str(data.end_datetime),'%Y-%m-%d %H:%M:%S')

    # new_task = Job()
    # jobs[new_task.uid] = new_task
    # jobs[new_task.uid].status = "in_progress"
    all_result = {"value":[]}
    # search data newer than in (annoy) index data -> deepface
    if(time_start_dt > time_db_dt):
        print('deepface')
        dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
        # jobs[new_task.uid].all_img = len(dir_list)
        result = long_task(all_result,db_list = dir_list,search_pic=data.file_path)
    # search data in (annoy) index data with some newer data -> deepface + annoyindex
    elif(time_start_dt < time_db_dt and time_end_dt > time_db_dt):
        print('deepface + annoyindex')
        dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
        db_above = filter(start_dt=str(time_db_dt + timedelta(seconds=1)),end_dt=str(data.end_datetime))
        # jobs[new_task.uid].all_img = len(dir_list)
        if(len(db_above) > 0):
            # print(db_above)
            # print('have more data')
            flag_new = True
        result = combine_process(
                                  all_result,
                                  db_list = dir_list,
                                  search_pic=data.file_path,
                                  flag_new = flag_new,
                                  db_new = db_above)
    # sear data in (annoy) index data -> annoyindex
    elif(time_start_dt <= time_db_dt and time_end_dt <= time_db_dt):
        print('annoyindex')
        dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
        # jobs[new_task.uid].all_img = len(dir_list)
        result = search_tree(all_result, db_list = dir_list,search_pic=data.file_path)
    return result


def combine_process(all_result: List, db_list:List, search_pic:str, flag_new: bool, db_new:List):
    # all_result = []
    # dir_list = filter_id(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
    embedding_objs = DeepFace.represent(img_path = search_pic, model_name= "Facenet512",enforce_detection=False)
    rank = u.get_nns_by_vector(embedding_objs[0]["embedding"], u.get_n_items(), include_distances=True)
    rank_id = rank[0]
    rank_sim = rank[1]
    db_list_id = [i[0] for i in db_list]

    count = 0
    for id,sim in zip(rank_id,rank_sim):
        # print(count)
        if(id in db_list_id and (1-((sim**2)/2)) > 0.65):
            # print('id: ',id,' => sim: ',1-((sim**2)/2))
            json_pic = {
                            "id":id,
                            "similarity": (1-((sim**2)/2))
                        }
            all_result["value"].append(json_pic)
        # count = count +1
        # jobs[task_id].progress = count
        # jobs[task_id].result = all_result
    # count = len(db_list_id)
    # jobs[task_id].progress = len(db_list_id)
    
    if(flag_new):
        for i in range(len(db_new)):
            name_pic_file = db_new[i][1].split('/')
            # print('/var/www/html/pic/'+name_pic_file[-1])
            name_path = '/var/www/html/pic/'+name_pic_file[-1]
            if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
                try:
                    result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet512", detector_backend ='opencv')
                    # print(str(result['verified']),' => ',str(result['distance']))
                    if(result['verified'] and result['distance'] < 0.35):
                            json_pic = {
                                "id":db_new[i][0],
                                "similarity": (1-result['distance'])
                            }
                            all_result["value"].append(json_pic)
                            # print(json_pic)
                except cv2.error as e:
                    # print("OpenCV Error:", e)
                    print("Custom error message: Unable to decode image.")
                    pass
    return all_result
