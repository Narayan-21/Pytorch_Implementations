# To get into the detail of this architecture, visit: https://arxiv.org/pdf/1409.4842.pdf.

import torch
import torch.nn as nn


class GoogleNet(nn.Module):
    def __init__(self, in_channels = 3, num_classes=1000):
        super(GoogleNet, self).__init__()
        self.conv1 = conv_block(in_channels=in_channels, out_channels=64, kernel_size= (7,7), stride=(2,2), padding=(3,3))
        self.maxpool1 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.conv2 = conv_block(64, 192, kernel_size=3, stride=1, padding=1)
        self.maxpool2 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # Argument order of InceptionBlock: in_channels, out_1X1, red_3X3, out_3X3, red_5X5, out_5X5, out_1X1pool
        self.inception3a = InceptionBlock(192,64,96,128,16,32,32)
        self.inception3b = InceptionBlock(256,128, 128, 192, 32, 96, 64)
        self.maxpool3 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.inception4a = InceptionBlock(480, 192, 96, 208, 16, 48, 64)
        self.inception4b = InceptionBlock(512, 160, 112, 224, 24, 64, 64)
        self.inception4c = InceptionBlock(512, 128, 128, 256, 24, 64, 64)
        self.inception4d = InceptionBlock(512, 112, 144, 288, 32, 64, 64)
        self.inception4e = InceptionBlock(528, 256, 160, 320, 32, 128, 128)
        self.maxpool4 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.inception5a = InceptionBlock(832, 256, 160, 320, 32, 128, 128)
        self.inception5b = InceptionBlock(832, 384, 192, 384, 48, 128, 128)
        self.avgpool = nn.AvgPool2d(kernel_size=7, stride=1)
        self.dropout = nn.Dropout(p=0.4)
        self.fc1 = nn.Linear(1024, 1000)

    def forward(self, x):
        x = self.conv1(x)
        x = self.maxpool1(x)
        x = self.conv2(x)
        x = self.maxpool2(x)
        x = self.inception3a(x)
        x = self.inception3b(x)
        x = self.maxpool3(x)
        x = self.inception4a(x)
        x = self.inception4b(x)
        x = self.inception4c(x)
        x = self.inception4d(x)
        x = self.inception4e(x)
        x = self.maxpool4(x)
        x = self.inception5a(x)
        x = self.inception5b(x)
        x = self.avgpool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.dropout(x)
        x = self.fc1(x)
        return x

class InceptionBlock(nn.Module):
    def __init__(self, in_channels, out_1X1, red_3X3, out_3X3, red_5X5, out_5X5, out_1X1pool):
        super(InceptionBlock, self).__init__()
        self.branch1 = conv_block(in_channels, out_1X1, kernel_size=1)
        self.branch2 = nn.Sequential(
            conv_block(in_channels, red_3X3, kernel_size=1),
            conv_block(red_3X3, out_3X3, kernel_size=3, padding=1) # Default padding=0, stride=1
        )
        self.branch3 = nn.Sequential(
            conv_block(in_channels, red_5X5, kernel_size=1),
            conv_block(red_5X5, out_5X5, kernel_size=5, padding=2)
        )
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            conv_block(in_channels, out_1X1pool, kernel_size=1)
        )

    def forward(self,x):
        return torch.cat([self.branch1(x), self.branch2(x), self.branch3(x), self.branch4(x)], 1)

# A convolutional block from which we will build the InceptionBlock, which in-turn will be a key to our Inception architecture.
class conv_block(nn.Module):
    def __init__(self, in_channels, out_channels, **kwargs):
        super(conv_block, self).__init__()
        self.relu = nn.ReLU()
        self.conv = nn.Conv2d(in_channels,out_channels, **kwargs)
        self.batchnorm = nn.BatchNorm2d(out_channels)
    def forward(self, x):
        return self.relu(self.batchnorm(self.conv(x)))

# Checking out the dimension of the output to be sure if the model architecture is fine.

if __name__ == '__main__':
    x = torch.randn(3,3,224,224)
    model = GoogleNet()
    print(model(x).shape)