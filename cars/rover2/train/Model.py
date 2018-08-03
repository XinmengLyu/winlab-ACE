import torch
import torch.nn as nn
import torch.nn.functional as F

dp=0.125 # dropout rate 

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.norm1 = nn.BatchNorm2d(3)
        self.conv1 = nn.Conv2d(3, 24, 5, stride=2, padding=2)
        self.norm2 = nn.BatchNorm2d(24)
        self.conv2 = nn.Conv2d(24, 32, 5, stride=2, padding=2)
        self.norm3 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 40, 5, stride=2, padding=2)
        self.norm4 = nn.BatchNorm2d(40)
        self.conv4 = nn.Conv2d(40, 48, 3, stride=2, padding=1)
        self.norm5 = nn.BatchNorm2d(48)
        self.conv5 = nn.Conv2d(48, 48, 3, stride=2, padding=1)
        self.fc1 = nn.Linear(48 * 3 * 4, 100)
        self.fc2 = nn.Linear(100, 3)
        self.dp2d = nn.Dropout2d(dp)
        self.dp = nn.Dropout(dp)
    
    def forward(self, x):
        x = self.norm1(x)
        x = F.elu(self.conv1(x))
        x = self.dp2d(x)
        x = self.norm2(x)
        x = F.elu(self.conv2(x))
        x = self.dp2d(x)
        x = self.norm3(x)
        x = F.elu(self.conv3(x))
        x = self.dp2d(x)
        x = self.norm4(x)
        x = F.elu(self.conv4(x))
        x = self.dp2d(x)
        x = self.norm5(x)
        x = F.elu(self.conv5(x))
        x = self.dp2d(x)
        x = x.view(-1, self.num_flat_features(x))
        x = F.elu(self.fc1(x))
        x = self.dp(x)
        x = self.fc2(x)
        return x
    
    def num_flat_features(self, x):
        size = x.size()[1:]
        num_features = 1
        for s in size:
            num_features *= s
        return num_features