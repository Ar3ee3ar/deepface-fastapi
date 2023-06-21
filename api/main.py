# run api : uvicorn test-api:app --reload
from typing import List, Annotated
from starlette.responses import StreamingResponse
import cv2
import io
import numpy as np
import base64
from PIL import Image

from fastapi import FastAPI, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time, timedelta

# from .face_aging_standalone import main_mani
# import face_aging_standalone
from process.verify import search

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500"
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

@app.get("/test")
async def hello():
    return {"message":"OK"}

@app.post("/files")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile,
                             start_datetime: Annotated[datetime | None, Body()] = None,
                             end_datetime: Annotated[datetime | None, Body()] = None,):
    # print(file.filename)
    contents = await file.read()
    image_np = np.frombuffer(contents, np.uint8)
    img_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR) 
    print(str(start_datetime))
    print(str(end_datetime))
    found_name, time, found_img = search(start_dt = str(start_datetime),end_dt=str(end_datetime),search_pic=img_np)
    return {"name_img":found_name,"time": time, "img":found_img}
    # return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")

@app.post("/uploadfiles")
async def create_upload_file(files: List[UploadFile]):
    # print(len(file))
    pic_list =[]
    name_list = []
    pic_in=[]
    name_in=[]
    for file in files:
        contents = await file.read()
        image_np = np.frombuffer(contents, np.uint8)
        img_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR) 
        img_pil = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        # print(type(img_np))
        pic_in.append(Image.fromarray(img_pil))
        name_img_list  = file.filename.split('.')
        name_img = name_img_list[0]
        name_in.append(name_img)
        # gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        # # img = cv2.imread(img_np) 
        # res, im_png = cv2.imencode(".png", gray)
        # name_img_list  = file.filename.split('.')
        # name_img = name_img_list[0]+'_gray'+'.png'
        # name_list.append(name_img)
        # pic_list.append(base64.b64encode(im_png.tobytes()))
    # pic_list,name_list = face_aging_standalone.main_mani(pic_in,name_in)
    return {"name":name_list,"pic": pic_list}