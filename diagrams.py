import pandas as pd
import matplotlib.pyplot as plt
res5=pd.read_csv('results5.txt', sep=" ", header=None, error_bad_lines=False)
res10=pd.read_csv('results10.txt', sep=" ", header=None, error_bad_lines=False)
res5.columns = ["throughput_5", "block_time_5"]
res10.columns = ["throughput_10", "block_time"]
res5["throughput_10"]=res10['throughput']
res5["block_time_10"]=res10['block_time']
res5["capacity"]=[1,5,10,1,5,10]
res5.iloc[:3].plot(x="capacity", y=["throughput_5", "throughput_10"], kind="bar")
f1=plt.figure(1)
plt.title('throughput for 5 nodes')
res5.iloc[3:].plot(x="capacity", y=["throughput_5", "throughput_10"], kind="bar")
f2=plt.figure(2)
plt.title('throughput for 10 nodes')
plt.show()