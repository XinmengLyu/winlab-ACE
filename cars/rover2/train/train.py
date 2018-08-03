import os
import torch
import torch.nn as nn

from Model import Net
from DataProcess import ImagesDataset, Normalize, Denormalize, ToTensor

def init_weights(m):
    """Helper function for initialize weights"""
    if type(m) == nn.Linear:
        nn.init.xavier_uniform_(m.weight.data, gain = nn.init.calculate_gain('linear'))
    if type(m) == nn.Conv2d:
        nn.init.xavier_uniform_(m.weight.data, gain = nn.init.calculate_gain('conv2d'))

"""
Initialize network and relevant variables
"""
root_dir = r'data/'

num_epoch = 2

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('Using device:', device)

net = Net().to(device)
net.apply(init_weights)

"""
Load training data
"""
from torch.utils.data import DataLoader
from torchvision import transforms

composed = transforms.Compose([Normalize(), ToTensor()])

trainset = ImagesDataset(csv_file = root_dir + 'train.csv', root_dir = root_dir,
                         transform = composed)
trainloader = DataLoader(trainset, batch_size = 4,
                        shuffle=True, num_workers=4)

"""
Train data
"""
import torch.optim as optim

criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr = 0.001, momentum = 0.9, 
                      weight_decay = 1e-6)

for epoch in range(num_epoch):
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        inputs, labels = data['image'], data['label']
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        print('[%d, %5d] loss: %.3f' %
             (epoch + 1, i + 1, loss.item()))
        running_loss = 0.0
print('Finished Training')

"""Load validation data and validate network"""
valiset = ImagesDataset(csv_file = root_dir + 'validate.csv', root_dir = root_dir,
                         transform = ToTensor())
valiloader = DataLoader(valiset, batch_size = 4,
                        shuffle=False, num_workers=4)
denormalize = Denormalize()

with torch.no_grad():
    for i, data in enumerate(valiloader):
        inputs, labels = data['image'], data['label']
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = net(inputs)
        outputs = denormalize(outputs.cpu())
        print('[%d] loss:' % (i + 1))
        print(outputs)

#torch.save(net.state_dict(), root_dir)
#torch.save(net, r'train/')