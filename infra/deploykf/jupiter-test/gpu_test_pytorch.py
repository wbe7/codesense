import torch

print("PyTorch version:", torch.__version__)

if torch.cuda.is_available():
    print("GPU (CUDA) is available and configured.")
    print("Number of GPUs:", torch.cuda.device_count())
    print("Current GPU:", torch.cuda.current_device())
    print("GPU Name:", torch.cuda.get_device_name(0))

    try:
        device = torch.device("cuda:0")
        a = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], device=device)
        b = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], device=device)
        c = torch.matmul(a, b)
        print("GPU calculation successful:\n", c.cpu().numpy())
    except Exception as e:
        print("Error performing GPU calculation:", e)
else:
    raise RuntimeError("No CUDA-enabled GPU devices found. This code requires a GPU.")