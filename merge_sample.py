import os
import json
import numpy as np
from io import BytesIO
from PIL import Image
import base64
import re
import logging
import urllib
import boto3
import secrets
import msgpack
import json
import pandas as pd
import requests

def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)
def check_iou(a, b,thr=0.6):
    """
    a: [xmin, ymin, xmax, ymax]
    b: [xmin, ymin, xmax, ymax]

    return: array(iou)
    """
    b = np.asarray(b)
    a_area = (a[  2] - a[  0]) * (a[  3] - a[  1])
    b_area = (b[  2] - b[  0]) * (b[  3] - b[  1])
    intersection_xmin = np.maximum(a[0], b[0])
    intersection_ymin = np.maximum(a[1], b[1])
    intersection_xmax = np.minimum(a[2], b[2])
    intersection_ymax = np.minimum(a[3], b[3])
    intersection_w = np.maximum(0, intersection_xmax - intersection_xmin)
    intersection_h = np.maximum(0, intersection_ymax - intersection_ymin)
    intersection_area = intersection_w * intersection_h
    min_area=min(a_area,b_area)
    if intersection_area/min_area>thr:
        return True
    return False

def tdcreate(rpos,cpos,flagmap,text):
    rowsize,colsize=flagmap.shape
    tmpid=flagmap[rpos,cpos]
    deltac=0
    deltar=0
    for ct in range(cpos,colsize):
       if flagmap[rpos,ct]==tmpid:
            deltac+=1
       else:
            break
    for rt in range(rpos,rowsize):
        if flagmap[rt,cpos]==tmpid:
            deltar+=1
        else:
            break
    if deltac==1 and deltar==1:
        return '<td>{}</td>'.format(text)
    else:
        return '<td colspan="{}" rowspan="{}">{}</td>'.format(deltac,deltar,text)

def extractfromocr(coordobj,rectminx,rectminy):
    resobj=[]
    tmpobj=[]
    for obj in coordobj:
        dubflag=False
        xmin = int(obj["xmin"])-int(rectminx)
        ymin = int(obj["ymin"])-int(rectminy)
        xmax = int(obj["xmax"])-int(rectminx)
        ymax = int(obj["ymax"])-int(rectminy)
        if xmin>xmax:
            xmin,xmax=xmax,xmin
        if ymin>ymax:
            ymin,ymax=ymax,ymin
        bbox=[xmin,ymin,xmax,ymax]
        for tmp in tmpobj:
            if check_iou(bbox,tmp,thr=0.95):
                dubflag=True
                break
        if dubflag:
            continue
        tmpobj.append(bbox)
        text=obj["contenttext"]
        resobj.append({"bbox":bbox,"text":text})
    resobj=sorted(resobj, key=lambda x: x['bbox'][1])
    resobj=sorted(resobj, key=lambda x: x['bbox'][0])
    return resobj

def dupmerge(conv_atrobjlist,textbboxlist):
    #まずloreの出力をきれいにする
    newconv_atrobjlist=[]
    used=set()
    for idx1 in range(len(conv_atrobjlist)):
        if idx1 in used:
            continue
        bbox1=conv_atrobjlist[idx1][4]
        lbox1=conv_atrobjlist[idx1][:4]
        for idx2 in range(idx1+1,len(conv_atrobjlist)):
            bbox2=conv_atrobjlist[idx2][4]
            lbox2=conv_atrobjlist[idx2][:4]
            if check_iou(bbox1,bbox2):
                used.add(idx2)
                bbox1=[min(bbox1[0],bbox2[0]),min(bbox1[1],bbox2[1]),max(bbox1[2],bbox2[2]),max(bbox1[3],bbox2[3])]
                lbox1=[min(lbox1[0],lbox2[0]),min(lbox1[1],lbox2[1]),max(lbox1[2],lbox2[2]),max(lbox1[3],lbox2[3])]
        newconv_atrobjlist.append([lbox1,bbox1])
    #textboxとマージする
    reslist=[]
    for idx1 in range(len(newconv_atrobjlist)):
        bbox1=newconv_atrobjlist[idx1][1]
        lbox1=newconv_atrobjlist[idx1][0]
        restext=""
        for textobj in textbboxlist:
            bboxt=textobj["bbox"]
            text=textobj["text"]
            if check_iou(bbox1,bboxt,0.1):
                restext+=text
        lbox1.append(restext)
        reslist.append(lbox1)
    return reslist
def extractfromlore(resultobj,textbboxlist):
    bndobjlist=[]
    atrobjlist=[]
    axis_set_row=set()
    axis_set_col=set()
    for bndobj,logiobj in zip(resultobj["center"],resultobj["logi"]):
        xmin = int(min([bndobj[0][0],bndobj[1][0],bndobj[2][0],bndobj[3][0]]))
        ymin = int(min([bndobj[0][1],bndobj[1][1],bndobj[2][1],bndobj[3][1]]))
        xmax = int(max([bndobj[0][0],bndobj[1][0],bndobj[2][0],bndobj[3][0]]))
        ymax = int(max([bndobj[0][1],bndobj[1][1],bndobj[2][1],bndobj[3][1]]))
        bbox=[xmin,ymin,xmax,ymax]
        bndobjlist.append(bbox)
        rowmin,rowmax,colmin,colmax=None,None,None,None
        rowmin = int(logiobj[0])
        rowmax = int(logiobj[1])
        colmin = int(logiobj[2])
        colmax = int(logiobj[3])
        if rowmin>rowmax:
            rowmin,rowmax=rowmax,rowmin
        if colmin>colmax:
            colmin,colmax=colmax,colmin
        axis_set_row.add(rowmin)
        axis_set_row.add(rowmax)
        axis_set_col.add(colmin)
        axis_set_col.add(colmax)
        atrobjlist.append([rowmin,rowmax,colmin,colmax])
    col2idx={}
    row2idx={}
    for idx,colval in enumerate(sorted(axis_set_col)):
        col2idx[colval]=idx
    for idx,rowval in enumerate(sorted(axis_set_row)):
        row2idx[rowval]=idx
    
    conv_atrobjlist=[]
    
    for idx,(rowmin,rowmax,colmin,colmax) in enumerate(atrobjlist):
        conv_atrobjlist.append([row2idx[rowmin],row2idx[rowmax],col2idx[colmin],col2idx[colmax],bndobjlist[idx]])

    conv_atrobjlist=dupmerge(conv_atrobjlist,textbboxlist)
    sorted_data = sorted(conv_atrobjlist, key=lambda x: (x[0], x[2], x[1], x[3]))
    
    colsize=len(col2idx)
    rowsize = len(row2idx)
    targetcolcnt={}
    for ii in range(rowsize+1):
        targetcolcnt[ii]=colsize
    tablestr='<table  border="1"><tr>'
    currentrow=0
    currentcol=0
    flagmap=np.zeros((rowsize+1,colsize+1))-1
    tmpid2text={}
    for tmpidx, (rowmin, rowmax, colmin, colmax,text) in enumerate(sorted_data):
        for r in range(rowmin,rowmax+1):
            for c in range(colmin,colmax+1):
                flagmap[r,c]=tmpidx
        tmpid2text[tmpidx]=text
    #print(flagmap)
    tmpidxset=set()
    for r in range(rowsize):
        tablestr+="</tr><tr>"
        for c in range(colsize):
            if flagmap[r,c]==-1:
                tablestr += '<td></td>'
            elif flagmap[r,c] in tmpidxset:
                continue
            else:
                tmpidxset.add(flagmap[r,c])
                tablestr += tdcreate(r,c,flagmap,tmpid2text[flagmap[r,c]])
    tablestr+="</tr></table>"
    return tablestr

def lambda_handler(event, _context):
    #print(response.text)
    if "body" in event and type(event["body"]) is str:
        event=json.loads(event['body'])
    width=event["width"]
    height=event["height"]
    coordobj=event["coordjsonstr"]
    textbboxlist=extractfromocr(coordobj,event["minX"],event["minY"])
    dstpath="/tmp/"+secrets.token_urlsafe(16)+".jpg"
    pct="pct:{},{},{},{}".format(round(event["minX"]/width*100, 2),
                                    round(event["minY"]/height*100, 2),
                                    round((event["maxX"]-event["minX"])/width*100, 2),
                                    round((event["maxY"]-event["minY"])/height*100, 2))
    img_url="https://www.dl.ndl.go.jp/api/iiif/{}/R{}/{}/full/0/default.jpg".format(str(event["PID"]),str(event["koma"]).zfill(7),pct)
    download_file(img_url,dstpath)
    data={}
    with open(dstpath, "rb") as fp:
        data["img"] = fp.read()
    payload = msgpack.packb(data, use_bin_type=True)
    response = requests.post("http://127.0.0.1:8080/invocations", 
        data=payload,
        headers={'Content-Type': 'application/x-msgpack'})
    tablestr=extractfromlore(response.json(),textbboxlist)
    dfs=pd.read_html(tablestr)
    df=dfs[0]
    tsv_string = df.to_csv(index=None,header = False,sep="\t")
    return {
        'statusCode': 200,
        'body': json.dumps({"html":tablestr,"tsv":tsv_string}, ensure_ascii=False)
    }

