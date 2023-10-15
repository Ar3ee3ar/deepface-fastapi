from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from deepface import DeepFace

import cv2
import os
from annoy import AnnoyIndex
from tqdm import tqdm

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel

from .process.verify import filter, get_all

u = AnnoyIndex(512, 'angular')

def create_annoy():
    try:
        global u
        embeded_list = []
        pass_list = []
        print('load image...')
        dir_list = get_all()

        for i in tqdm(range(len(dir_list))):
            name_pic_file = dir_list[i][1].split('/')
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

        with open('update_date.txt', 'w') as f:
            f.write(str(dir_list[len(dir_list)-1][2]))
        print('Finish')
        return True
    except:
        return False
create_annoy()

class Req_search(BaseModel):
    file_path: str
    start_datetime: datetime | None
    end_datetime: datetime | None

class Res_search_value(BaseModel):
    id: int
    similarity: float

class Res_search_main(BaseModel):
    value: List[Res_search_value]

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"message":"Face verification api"}


def long_task(all_result: List, db_list:List, search_pic:str):
    for i in range(len(db_list)):
        name_pic_file = db_list[i][1].split('/')
        name_path = '/var/www/html/pic/'+name_pic_file[-1]
        if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
            try:
                result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet512", detector_backend ='opencv')
                if(result['verified'] and result['distance'] < 0.35):
                        json_pic = {
                            "id":db_list[i][0],
                            "similarity": (1-result['distance'])
                        }
                        all_result["value"].append(json_pic)
            except cv2.error as e:
                print("Custom error message: Unable to decode image.")
                pass
    return all_result

@app.get("/create_tree")
def recreate_annoy():
    flag = create_annoy()
    if(flag):
        return {"message": "Finish create data for face verification"}
    else:
        return {"message": "Error"}

def search_tree(all_result: List, db_list:List, search_pic:str):
    embedding_objs = DeepFace.represent(img_path = search_pic, model_name= "Facenet512",enforce_detection=False, detector_backend ='opencv')
    rank = u.get_nns_by_vector(embedding_objs[0]["embedding"], u.get_n_items(), include_distances=True)
    rank_id = rank[0]
    rank_sim = rank[1]
    db_list_id = [i[0] for i in db_list]

    i = 0
    for id,sim in zip(rank_id,rank_sim):
        if(id in db_list_id and 1-((sim**2)/2) > 0.65):
            json_pic = {
                            "id":id,
                            "similarity": 1-((sim**2)/2)
                        }
            all_result["value"].append(json_pic)
        i = i +1
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

    all_result = {"value":[]}
    # search data newer than in (annoy) index data -> deepface
    if(time_start_dt > time_db_dt):
        print('deepface')
        dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
        result = long_task(all_result,db_list = dir_list,search_pic=data.file_path)
    # search data in (annoy) index data with some newer data -> deepface + annoyindex
    elif(time_start_dt < time_db_dt and time_end_dt > time_db_dt):
        print('deepface + annoyindex')
        dir_list = filter(start_dt=str(data.start_datetime),end_dt=str(data.end_datetime))
        db_above = filter(start_dt=str(time_db_dt + timedelta(seconds=1)),end_dt=str(data.end_datetime))
        if(len(db_above) > 0):
            # have more data
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
    embedding_objs = DeepFace.represent(img_path = search_pic, model_name= "Facenet512",enforce_detection=False)
    rank = u.get_nns_by_vector(embedding_objs[0]["embedding"], u.get_n_items(), include_distances=True)
    rank_id = rank[0]
    rank_sim = rank[1]
    db_list_id = [i[0] for i in db_list]

    for id,sim in zip(rank_id,rank_sim):
        if(id in db_list_id and (1-((sim**2)/2)) > 0.65):
            json_pic = {
                            "id":id,
                            "similarity": (1-((sim**2)/2))
                        }
            all_result["value"].append(json_pic)
    
    if(flag_new):
        for i in range(len(db_new)):
            name_pic_file = db_new[i][1].split('/')
            name_path = '/var/www/html/pic/'+name_pic_file[-1]
            if(os.path.exists(name_path) and name_path.find('.jpg') != -1):
                try:
                    result = DeepFace.verify(img1_path = search_pic, img2_path = name_path ,enforce_detection= False, model_name= "Facenet512", detector_backend ='opencv')
                    if(result['verified'] and result['distance'] < 0.35):
                            json_pic = {
                                "id":db_new[i][0],
                                "similarity": (1-result['distance'])
                            }
                            all_result["value"].append(json_pic)
                except cv2.error as e:
                    print("Custom error message: Unable to decode image.")
                    pass
    return all_result
