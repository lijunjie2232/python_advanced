from memory_profiler import profile
import numpy as np
import torch


@profile
def my_func():
    a = [i for i in range(100000)]
    b = [i * 2 for i in range(100000)]
    return a, b


@profile
def np_mem():
    a = np.random.randn(3, 1024, 1024)
    b = np.random.randn(3, 1024, 1024)
    c = a @ b
    return c


@profile
def tensor_mem():
    a = torch.randn(3, 1024, 1024)
    b = torch.randn(3, 1024, 1024)
    c = a @ b
    return c

@profile
def tensor_cuda_mem():
    a = torch.randn(3, 1024, 1024, device='cuda')
    b = torch.randn(3, 1024, 1024, device='cuda')
    c = a @ b
    return c

if __name__ == "__main__":
    my_func()
    np_mem()
    tensor_mem()
    tensor_cuda_mem()
    