
# Experimentation Process

In this document, I describe my experimentation process testing different architectures for the traffic sign classification model.

What did you try? What worked well? What didn’t work well? What did you notice?

## 1st Trial

In this first trial I used 2 convolutional layers, and I obtained a final accuracy of 96%, the initial accuracy in epoch 1 started at 0.403, and it reached 0.934 by epoch 10, which is a significant improvement. The final loss during training was 0.2301.

## 2nd Trial

In this second trial I used 3 convolutional layers and the final accuracy I obtained was 98.4%, this process was much slower, since both were performed without GPU. But it can be observed that 
the initial accuracy in epoch 1 (0.494) was not much higher than in the previous trial. A very noticeable difference is the final loss during training, which was significantly lower in tjis trial, 0.041. 

So overall the second model is more accurate, but each epoch is slower.


