import sys
import os
import pathlib
import argparse
sys.path.append(os.path.join(pathlib.Path(__file__).parent.absolute(), '..'))
import numpy as np
import cv2
from tqdm import tqdm
'''
README:
1. 处理的是scannet这个数据集，文件组织遵循point-nerf；
2. warning: 采取的是原数据集中直接删除blur图片的做法！！！！一定请备份数据集
'''
class Options:
    def __init__(self):
        self.opt = None
        self.parse()
    def parse(self):
        parser = argparse.ArgumentParser(description="Demo of argparse")
        parser.add_argument('--data_root',type=str, default='/home/slam/devdata/pointnerf/data_src/scannet/scans',help='root of dataset')
        parser.add_argument('--scan',type=str, default='scene0000_00-T-blur',help='room which to scan')
        parser.add_argument('--auto_or_manual', type=str, default='1', help='0:auto to detect blur;1:manual to detect blur')
        parser.add_argument('--num_of_remove', type=str, default='150', help='set how may blur image to be remove')
        self.opt = parser.parse_args()
        self.opt.dataset_dir = os.path.join(self.opt.data_root,self.opt.scan,'exported')
        # print(self.opt.dataset_dir)
class Dataset:
    def __init__(self,opt):
        self.auto_detect = (opt.auto_or_manual=='0')
        self.dataset_dir = opt.dataset_dir
        self.color_dir = os.path.join(self.dataset_dir,'color')
        self.depth_dir = os.path.join(self.dataset_dir,'depth')
        self.pose_dir = os.path.join(self.dataset_dir,'pose')
        self.num_of_remove = opt.num_of_remove
        self.color_path_list = [os.path.join(self.color_dir,f) for f in os.listdir(self.color_dir)]
        self.blur_id_list  = self.get_blur_id_list()
        print('init down')
    def remove_blur_data(self):
        print('data to remove:\n',self.blur_id_list)
        print('Removing blur data')
        self.blur_color_path_list = []
        self.blur_depth_path_list = []
        self.blur_pose_path_list = []
        for id in tqdm(self.blur_id_list):
            color_path = os.path.join(self.color_dir,'{}.jpg'.format(id))
            depth_path = os.path.join(self.depth_dir, '{}.png'.format(id))
            pose_path = os.path.join(self.pose_dir, '{}.txt'.format(id))
            os.remove(color_path)
            os.remove(depth_path)
            os.remove(pose_path)
        print('Remove blur data down')
    def get_blur_id_list(self):
        blur_id = []
        if(self.auto_detect):
            blur_id  = self.automatic_detect_blur()
        else:
            print(os.path.join(self.dataset_dir,'blur_list.txt'))
            if not os.path.exists(os.path.join(self.dataset_dir,'blur_list.txt')):
                print("Choose Manual,but don't exists blur_list at {}".format(os.path.join(self.dataset_dir,'blur_list.txt')))
                exit()
            else:
                print('Use manual blur_list')
                blur_id = np.loadtxt(os.path.join(self.dataset_dir,'blur_list.txt')).astype(np.int32)
        return blur_id
    def automatic_detect_blur(self):
        assert self.num_of_remove< len(self.color_path_list),'too much images to move! shrink the --num_of_remove'

        print('automatic detect blur image:')
        blur_score = []
        for img_path in tqdm(self.color_path_list):
            img = cv2.imread(img_path)
            gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            var =  cv2.Laplacian(gray_img, cv2.CV_64F).var()
            blur_score.append(var)
        blur_score = np.asarray(blur_score)
        blur_id_list = blur_score.argsort()[:self.num_of_remove] # 认为拉普拉斯算子的方差小的图片为blur图片
        return blur_id_list


def main():
    sparse = Options()
    opt = sparse.opt
    print(opt)
    ds = Dataset(opt)
    ds.remove_blur_data()
if __name__=="__main__":
    main()