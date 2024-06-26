# -*- coding: utf-8 -*-
"""CIFAR10CNN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YK6hIrcEKA92x9599Y_ztDkv1Zyug5uF
"""

from __future__ import print_function
import torch  # import the torch library
import torch.nn as nn # use the nn module (class)
import torch.nn.functional as F    # use the nn module as function
import torch.optim as optim # optimization (i.e., SGD, ada,)
import torchvision # load the dataset
import torchvision.transforms as transforms # adjust the input image
import time # check the processing overhead
import torch.nn.init as init

# Define transformations for the dataset.
# Preparing for Data
print('==> Preparing data..')

# Training Data augmentation
transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])
# Testing Data preparation
transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

# Define the class for the model
class CIFAR10Net(nn.Module):
  def __init__(self):
    super(CIFAR10Net, self).__init__()
    # Define the convolutional layers
    self.c1 = nn.Conv2d(3, 32, 11, 1, 5)
    self.c2 = nn.Conv2d(32, 64, 7, 1, 3)
    self.c3 = nn.Conv2d(64, 128, 5, 1, 2)
    self.c4 = nn.Conv2d(128, 256, 5)
    self.c5 = nn.Conv2d(256, 2560, 5)

    # Initialize weights for each convolutional layer
    torch.nn.init.xavier_uniform_(self.c1.weight)
    torch.nn.init.xavier_uniform_(self.c2.weight)
    torch.nn.init.xavier_uniform_(self.c3.weight)
    torch.nn.init.xavier_uniform_(self.c4.weight)
    torch.nn.init.xavier_uniform_(self.c5.weight)

    # Define the fully connected layers
    self.F1 = nn.Linear(40960, 128)
    self.F2 = nn.Linear(128, 10)

    # Initialize weights for the fully connected layers
    torch.nn.init.zeros_(self.F1.weight)
    torch.nn.init.zeros_(self.F2.weight)

    self.MyRelu = nn.ReLU()

  # Forward Propogation for the model
  def forward(self, x):
    x = self.c1(x)
    x = F.relu(x)
    x = self.c2(x)
    x = F.relu(x)
    x = self.c3(x)
    x = F.relu(x)
    x = F.max_pool2d(x, 2, 2)
    x = self.c4(x)
    x = F.relu(x)
    x = self.c5(x)
    x = F.relu(x)
    x = F.max_pool2d(x, 2, 2)

    drop = nn.Dropout(0.5)
    x = drop(x)

    x = torch.flatten(x, 1)

    x = self.F1(x)
    x = self.MyRelu(x)
    x = self.F2(x)

    return x

# Training the model
def train(model, device, train_loader, optimizer, epoch, scheduler1, scheduler2):
  model.train()
  count = 0

  lossFunc = nn.CrossEntropyLoss()
  for batch_idx, (x, y) in enumerate(train_loader):
    # Pass the data to the model to get the predicted value and perform the back propogation.
    x, y = x.to(device), y.to(device)
    y_pred = model(x)
    loss = lossFunc(y_pred, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print the results during each epoch with the loss value
    if batch_idx % 10 == 0:
      print("Train Epoch: " + str(epoch) + " Loss: " + str(loss.item()))
  scheduler1.step()
  scheduler2.step()

# Method to test the model
def test(model, device, test_loader):
  model.eval()
  testLoss = 0
  correct = 0
  # Testing
  with torch.no_grad():
    for x, y in test_loader:
      x, y = x.to(device), y.to(device)
      y_pred = model(x)
      y_pred = F.log_softmax(y_pred, dim = 1)
      testLoss += F.nll_loss(y_pred, y, reduction = 'sum').item()
      pred = y_pred.argmax(dim = 1, keepdim = True)
      correct += pred.eq(y.view_as(pred)).sum().item()

    # Print the results
    testLoss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        testLoss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

# Main function to run the program
def main():
  time0 = time.time()
  # Settings for training
  batchSize = 128
  epochs = 50
  learnRate = 0.05
  no_cuda = False
  save_model = False
  use_cuda = not no_cuda and torch.cuda.is_available()
  torch.manual_seed(100)
  device = torch.device("cuda" if use_cuda else "cpu")


  # Download the data and create data loaders
  trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
  train_loader = torch.utils.data.DataLoader(trainset, batch_size=128, shuffle=True)
  testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)
  test_loader = torch.utils.data.DataLoader(testset, batch_size=128, shuffle=False)

  # Set up the model optimzier
  model = CIFAR10Net().to(device)
  # Initialize weights and biases for the model
  optimizer = optim.SGD(model.parameters(), lr = learnRate, momentum = 0.9, weight_decay = 5e-4)
  # Define schedulers for adaptive learning rate
  scheduler1 = optim.lr_scheduler.ExponentialLR(optimizer, gamma = 0.9)
  scheduler2 = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[10, 20, 30, 40], gamma=0.9)

  # Print the results of the training and testing
  for epoch in range(1, epochs + 1):
    train(model, device, train_loader, optimizer, epoch, scheduler1, scheduler2)
    test(model, device, test_loader)

  if (save_model):
    torch.save(model.state_dict(), "cifar_net.pt")
  time1 = time.time()
  print ('Training and Testing total execution time is: %s seconds ' % (time1-time0))

# Run the function
if __name__ == '__main__':
  main()