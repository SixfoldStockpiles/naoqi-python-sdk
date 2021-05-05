import numpy as np
import matplotlib.pyplot as plt

fig=plt.figure(figsize=(8, 4))

# make up some data for demo purposes
raw = np.random.randint(10, size=(6,6))
# apply some logic operatioin to the data
O = (raw >= 5) * 1   # get either 0 or 1 in the array
I = np.random.randint(10, size=(6,6))  # get 0-9 in the array

# plot each image ...
# ... side by side
fig.add_subplot(1, 2, 1)   # subplot one
plt.imshow(I, cmap=plt.cm.gray)

fig.add_subplot(1, 2, 2)   # subplot two
# my data is OK to use gray colormap (0:black, 1:white)
plt.imshow(O, cmap=plt.cm.gray)  # use appropriate colormap here
plt.show()
