import numpy as np
import cv2
import pickle
import os
from scipy.cluster.vq import vq

sift = cv2.SIFT_create()
k =200
cache_path = './cache'
neigh = pickle.load(open(os.path.join(cache_path,'classifier.pkl'), 'rb'))
stdSlr = pickle.load(open(os.path.join(cache_path,'standard_scaler.pkl'), 'rb'))
le = pickle.load(open(os.path.join(cache_path,'label_encoder.pkl'), 'rb'))
codebook = pickle.load(open(os.path.join(cache_path,'codebook.pkl'), 'rb'))

h = w = 250

def get_threshold(img):
  H,W = img.shape
  h_s = 0
  w_s = 0

  h_e = H
  w_e = W

  for h in range(H):
    for w in range(W):
      if img[h,w] > 0:
        h_s = h
      if h_s!=0: break
    if h_s!=0: break

  for h in reversed(range(H)):
    for w in range(W):
      if img[h,w] > 0:
        h_e = h
      if h_e!=H: break
    if h_e!=H: break

  for w in range(W):
    for h in range(H):
      if img[h,w] > 0:
        w_s = w
      if w_s!=0: break
    if w_s!=0: break
  
  for w in reversed(range(W)):
    for h in range(H):
      if img[h,w] > 0:
        w_e = w
      if w_e!=W: break
    if w_e!=W: break

  return h_s, h_e, w_s, w_e

def preprocess(img):
  h_s, h_e, w_s, w_e = get_threshold(img)
  crop = img[h_s:h_e, w_s:w_e]
  resized = cv2.resize(crop, (500, 500), interpolation = cv2.INTER_AREA)
  equ = cv2.equalizeHist(resized)
  return equ

def extract_feature(grayscale, save = None):
  grayscale = preprocess(grayscale)

  keypoint, des = sift.detectAndCompute(grayscale, None)
  
  if save is not None:
    img_final = cv2.drawKeypoints(grayscale, keypoint, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite(save, img_final)

  im_features = np.zeros((k), "float32")
  words, _ = vq(des,codebook)

  for w in words:
      im_features[w] += 1

  im_features = im_features.reshape(1,-1)
  im_features = stdSlr.transform(im_features)
  return im_features

if __name__ == '__main__':
  print('name')
  #bag of visual words
  #số lượng của keypoint ứng với codebook,
  #đã được normalize