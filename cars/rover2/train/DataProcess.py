import os
import torch
import pandas as pd
from skimage import io
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

class ImagesDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.imgs_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform
    
    def __len__(self):
        return len(self.imgs_frame)
    
    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.imgs_frame.iloc[idx,0])
        image = io.imread(img_name).astype(np.float32)
        label = self.imgs_frame.iloc[idx,0][11:-5].split('_')
        label = np.array(list(map(float, label))).astype(np.float32)
        sample = {'image': image, 'label': label}
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample

class Normalize(object):
    """image and label are both nparrays"""
    def __call__(self, sample):
        image, label = sample['image'], sample['label']
        label[0] /= 32767
        label[1] /= 2
        return  {'image': image, 'label': label}

class Denormalize(object):
    """take pytorch tensor label, denormalize, then transform to nparray"""
    def __call__(self, labels):
        label_list = list()
        for label in labels:
            label = label.numpy()
            label[0] *= 32767
            label[1] *= 2
            label_list.append(label)
        return np.array(label_list)

class ToTensor(object):
    """take nparray image and label, transpose, then transform to pytorch tensor"""
    def __call__(self, sample):
        image, label = sample['image'], sample['label']
        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        image = image.transpose((2,0,1))
        return {'image': torch.from_numpy(image),
                       'label': torch.from_numpy(label)}