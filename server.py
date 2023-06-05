from fastapi import FastAPI, File, UploadFile, Request
import os
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2
from utils import extract_feature, cache_path
from tqdm import tqdm
import json
from sklearn.metrics.pairwise import euclidean_distances

IMAGEDIR = "media/"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")

database = []

def init():
    global database
    path = '/home/baocongidol/Workspace/PTIT/HCSDL_DaPhuongTien/data/v0'
    db_path = os.path.join(cache_path,'databale.json')
    if not os.path.exists(db_path):
        for (root, dirs, file) in os.walk(path):
            label = root.split('/')[-1]
            for f in tqdm(file, desc=f"{label}"):
                if '.png' in f:
                    img_dir = f'{root}/{f}'
                    image = cv2.imread(img_dir,cv2.IMREAD_GRAYSCALE)

                    img_processed = f"{IMAGEDIR}{f}"
                    img_feature = extract_feature(image, save=img_processed)[0]

                    database.append(
                        {
                            'img_dir': img_processed,
                            'img_url': f"/{IMAGEDIR}{f}",
                            'label': label,
                            'img_feature': img_feature.tolist()
                        }
                    )

        json.dump(database, open(db_path, 'w'), ensure_ascii=False, indent= 4)
    else:
        database = json.load(open(db_path, 'r'))

def knn(query_feature, k):

    items = []

    for item in database:
        item = item.copy()
        img_feature = item["img_feature"]
        img_feature = np.array(img_feature).reshape(1,-1)

        dist = euclidean_distances(query_feature, img_feature)

        item['dist'] = dist[0][0]
        item.pop('img_feature')

        items.append(item)
    
    items = sorted(items, key=lambda x: x['dist'])[:k]

    analysis = {}
    for item in items:
        label = item['label']
        dist = item['dist']

        if label in analysis:
            tmp = analysis[label]
            analysis[label] = {
                'num': tmp['num'] + 1,
                'dist': tmp['dist'] + dist
            }
        else:
            analysis[label] = {
                'num': 1,
                'dist': dist
            }

    scores = sorted(analysis.items(), key=lambda x:(-x[1]['num'], x[1]['dist']/x[1]['num']))

    return items, scores[0]

init()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/images/")
async def create_upload_file(file: UploadFile = File(...)):

    contents = await file.read()

    nparr = np.fromstring(contents, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    grayscale = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    im_feature = extract_feature(grayscale, save=f"{IMAGEDIR}{file.filename}")

    items, (label, score) = knn(im_feature, 5)

    json_compatible_item_data = jsonable_encoder(
        {
            'processed': f"/{IMAGEDIR}{file.filename}",
            'label': label,
            'nearest': items,
            'score': score
        })

    return JSONResponse(content=json_compatible_item_data)