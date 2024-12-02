import cupy as cp

# 获取第一个 CUDA 设备（索引 0）
device = cp.cuda.Device(0)
print(device)
