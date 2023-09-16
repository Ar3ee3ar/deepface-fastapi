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

from fastapi import FastAPI, File, UploadFile, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time, timedelta
from pydantic import BaseModel

# from .face_aging_standalone import main_mani
# import face_aging_standalone
from .process.verify_progress import filter

class Req_search(BaseModel):
    file_path: str
    start_datetime: datetime | None
    end_datetime: datetime | None

class Res_search_value(BaseModel):
    id: int
    similarity: float

# class Res_search_main(BaseModel):
#     value: List[Res_search_value]

class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = ""
    progress: int = 0
    all_img: int = 0
    result: List[Res_search_value] = [{"id":0,"similarity":0.0}]

app = FastAPI()
jobs: Dict[UUID, Job] = {}  # Dict as job storage
# all_result = {"value":[]}


def long_task(all_result:List, task_id: UUID, db_list:List, search_pic:str):
    # all_result = {"value":[]}
    all_time_verify = 0
    found_pic = []
    for i in range(len(db_list)):
        name_pic_file = db_list[i][1].split('/')
        # file_type = name_pic_file[-1].split('.')
        name_path = '/var/www/html/pic/'+name_pic_file[-1]
        if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
            try:
                result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet", detector_backend ='opencv')
                if(result['verified'] and result['distance'] < 0.3):
                        # all_result.append(dir_list[i][1])
                        # all_time_verify = all_time_verify + int(result["time"])
                        # pic = rect_pic(dir_list[i][2],result['facial_areas']['img2'])
                        # found_pic.append(pic)
                        json_pic = {
                            "id":db_list[i][0],
                            "similarity": (1-result['distance'])
                        }
                        all_result.append(json_pic)
            except cv2.error as e:
                # print("OpenCV Error:", e)
                print("Custom error message: Unable to decode image.")
                pass
            jobs[task_id].progress = i+1
        jobs[task_id].result = all_result
    jobs[task_id].status = "completed"
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


@app.post("/verify", status_code=HTTPStatus.ACCEPTED)
async def task_handler(background_tasks: BackgroundTasks, data: Req_search) -> Job:
    new_task = Job()
    jobs[new_task.uid] = new_task
    dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
    jobs[new_task.uid].all_img = len(dir_list)
    all_result = []
    background_tasks.add_task(long_task,all_result, new_task.uid,db_list = dir_list,search_pic=data.file_path)
    return new_task
    # new_task = Job()
    # jobs[new_task.uid] = new_task
    # background_tasks.add_task(start_new_task, new_task.uid, data)
    # return new_task


@app.get("/task/{uid}/status")
async def status_handler(uid: UUID) -> Job:
    return jobs[uid]