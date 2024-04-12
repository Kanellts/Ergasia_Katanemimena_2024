# this was run in google colab to get the diagrams

import numpy as np
import matplotlib.pyplot as plt

N = 3
ind = np.arange(N)  # the x locations for the groups
width = 0.3      # the width of the bars

fig = plt.figure(figsize = (10,8))
ax = fig.add_subplot(111)


yvals = [2.83,9.145,10.335]
rects1 = ax.bar(ind, yvals, width, color='g')
zvals = [5.1099,4.8709,6.9813]
zvals = [5.87,8.05,12.67]
rects2 = ax.bar(ind+width, zvals, width, color='y')
plt.title('Throughput',fontsize = 20)
ax.set_ylabel('Throughput',fontsize = 15)
ax.set_xticks(ind+width)
ax.set_xticklabels( ('c=5', 'c=10', 'c=20') )
ax.legend( (rects1[0], rects2[0]), ('5 clients', '10 clients') ,fontsize = 10)
plt.grid()
def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')



import numpy as np
import matplotlib.pyplot as plt

N = 3
ind = np.arange(N)  # the x locations for the groups
width = 0.3    # the width of the bars

fig = plt.figure(figsize = (10,8))
ax = fig.add_subplot(111)

yvals = [0.21,0.145,0.26]

rects1 = ax.bar(ind, yvals, width, color='c')
zvals = [0.13, 0.35, 0.798]
rects2 = ax.bar(ind+width, zvals, width, color='m')
plt.title('Average Block Time',fontsize = 20)
ax.set_ylabel('Average Block Time',fontsize = 15)
ax.set_xticks(ind+width)
ax.set_xticklabels( ('c=5', 'c=10', 'c=20') )
ax.legend( (rects1[0], rects2[0]), ('5 clients', '10 clients') ,fontsize = 10)
plt.grid()
def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                ha='center', va='bottom')