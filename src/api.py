
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths

from fastapi import FastAPI, Request
import uvicorn
import io
import os
from tqdm import tqdm
import cv2
import pycocotools.coco as coco
from opts import opts
from detectors.detector_factory import detector_factory
import msgpack
from PIL import Image
import numpy as np
image_ext = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']

app = FastAPI()

opt = opts().init()
opt.demo=''
opt.debug=0
os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
Detector = detector_factory[opt.task]
detector = Detector(opt)


@app.get('/ping')
def ping():
    return {"message": "ok"}

@app.post('/invocations')
async def api(request: Request):
  raw_binary = await request.body()
  data = msgpack.unpackb(raw_binary, raw=False)
  img = Image.open(io.BytesIO(data["img"]))
  width = img.width
  height = img.height
  img_numpy = np.array(img, dtype=np.uint8)
  #cvimage=img_numpy
  cvimage = cv2.cvtColor(img_numpy, cv2.COLOR_RGB2BGR)
  #print(cvimage)
  image_annos = []
  if not opt.wiz_detect:
    image_anno = []
    ret = detector.run(opt, cvimage, image_anno)
  else:
    ret = detector.run(opt, cvimage)
  center_list=[]
  logi_list=[]
  if "4ps" in ret:
    results=ret["4ps"]
    logi=ret["logi"]
    for j in range(1, 3):
      k = 0
      for m in range(len(results[j])):
        bbox = results[j][m]
        k = k + 1
        if bbox[8] > opt.vis_thresh:
          center_coords=[]
          logi_coords=[]
          for i in range(0,4):
            position_holder = 1
            center_coords.append([float(bbox[2*i]),float(bbox[2*i+1])])
            if not logi is None:
              if len(logi.shape) == 1:
                logi_coords.append(int(logi[i]))
              else:
                logi_coords.append(int(logi[m,:][i]))
          center_list.append(center_coords)
          logi_list.append(logi_coords)
  return {"logi":logi_list,"center":center_list}
if __name__ == "__main__":
  uvicorn.run(
    app,
    host="0.0.0.0",
    port=8080)
