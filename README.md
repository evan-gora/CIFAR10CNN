# CIFAR10 Convolutional Nerual Network

This project is a convolutional neural network for the CIFAR10 dataset built using Pytorch

I began with a base network that was only 40% accurate and was given the task to improve it to at least 85% using a maximum of 10 layers. I spent a lot of time reading 
Pytorch documentation and about different ways to improve convolutional neural networks for this task. One of the most helpful changes I made was the addition of 2 schedulers 
for an adaptive learning rate. Using both an exponential learning rate scheduler and a step learning rate scheduler that decreased the learning rate every 10 epochs, I was 
able to get the best results. Some other changes I made to the network to improve its accuracy were to add a dropout layer after all of the convolutions were completed and 
initalize weights for the model. The final accuracy for the model is 86%.

