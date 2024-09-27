import torch
from torchvision import models
from memory_profiler import profile
from inspect import unwrap
from time import time


@profile
def model_test():
    device = torch.device("cuda:0")
    model = models.resnet50().cuda()
    print(torch.cuda.memory_allocated() / 1024**2, "MB")
    model = model.cpu()
    print(torch.cuda.max_memory_allocated() / 1024**2, "MB")
    print(torch.cuda.memory_summary())
    model = model.cuda()

    with torch.profiler.profile(
        activities=[
            torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA,
        ],
        # execution_trace_observer=(
        #     torch.profiler.ExecutionTraceObserver().register_callback("./execution_trace.json")
        # ),
        record_shapes=True,
        profile_memory=True,  # 启用显存分析
        with_stack=True,
    ) as prof:
        x = torch.randn(1, 3, 224, 224).cuda()
        model(x)
    print(prof.key_averages().table(sort_by="cuda_time_total"))

    x = torch.randn(32, 3, 224, 224).cuda()
    torch.cuda.synchronize()
    start = time()
    model(x)
    torch.cuda.synchronize()
    end = time()
    print(end - start, "ms")


if __name__ == "__main__":
    model_test()
    unwrap(model_test)()
