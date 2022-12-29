"""
 얼굴 인증 메인 함수
"""
import matplotlib.pyplot as plt
import cv2
import tensorflow as tf
import numpy as np
import glob
import dlib
import os
from face_rec.model.facenet import Facenet
from face_rec.function.crop import crop
from face_rec.function.load_imgs import load_imgs
from face_rec.function.shape import shape
from face_rec.function.rotate import rotate
from pathlib import Path


def main():

    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    tf.compat.v1.disable_eager_execution()
    print('AI Calculate is on')

    ROOT_DIR = Path(__file__).parent.parent
    print(f'root_path is  {ROOT_DIR}')

    profile_images_path = os.path.join(ROOT_DIR, 'face_rec/images/profile')
    selfie_image_path = os.path.join(ROOT_DIR, 'face_rec/images/selfie')
    model_path = os.path.join(ROOT_DIR, 'face_rec/model/20180402-114759.pb')
    predictor_path = os.path.join(ROOT_DIR, 'face_rec/model/shape_predictor_68_face_landmarks.dat')


    input_size = (160, 160)# 모델에 삽입되는 사이즈


    ##-------------------------------------------------Load and crop images --------------------------------------------------------------------##

    profile_imgs = load_imgs(profile_images_path) # 리스트 반환 / 원본 로드
    selfie_img =load_imgs(selfie_image_path)

    predictor = dlib.shape_predictor(predictor_path)
    detector = dlib.get_frontal_face_detector()

    profile_faces=[]
    for img in profile_imgs:
        detected_faces=crop(img,input_size)
        for detected_face in detected_faces:
            profile_faces.append(detected_face) # 얼굴 하나씩 들어 있다.

    selfie_faces=crop(selfie_img[0],input_size) # 한장만


    # shape 리스트 생성


    profile_shapes= shape(profile_imgs, predictor_path)
    selfie_shapes = shape(selfie_img, predictor_path)


    # shape 정보를 바탕으로 회전

    profile_rotated_imgs=rotate(profile_faces,profile_shapes)
    selfie_rotated_imgs=rotate(selfie_faces,selfie_shapes)




    # ##--------------------------------------------------------prediction--------------------------------------------------------------##
    facenet= Facenet(model_path)

    print("profile에서 탐지된 얼굴 수 :", len(profile_faces))
    print("selfie에서 탐지된 얼굴 수 :", len(selfie_faces))

    profile_predictions= facenet.get_embeddings(profile_rotated_imgs)
    selfie_predictions = facenet.get_embeddings(selfie_rotated_imgs)

    profile_predictions=np.reshape(profile_predictions,[-1,1,512])
    selfie_predictions=np.reshape(selfie_predictions,[-1,1,512])


    eucledian_dist = []
    print("벡터 거리 정보/ 0.9 이하는 동일인")
    for i in range(len(profile_predictions)):
        for j in range(len(selfie_predictions)):
            dist=np.linalg.norm(profile_predictions[i]-selfie_predictions[j])
            eucledian_dist.append(dist)
    print(eucledian_dist)



    ## ----------------------------------- 이미지 체크할 때/ loded_imgs에 profile_imgs 나 selfie_imgs 를 써서 크로핑 된 이미지를 확인 가능하다 -------------------------------##
    loaded_imgs = profile_rotated_imgs# select profile_imgs or selfie_imgs


    # for i in loaded_imgs:
    #     a= cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
    #     a=np.array(a)
    #     plt.imshow(a)
    #     plt.show()
    return 'done'


if __name__ == '__main__':
    main()
