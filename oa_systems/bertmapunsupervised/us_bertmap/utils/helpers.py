import random
import sys

import numpy as np
import torch


def get_device(device_num=0):
    if torch.cuda.is_available():
        # Tell PyTorch to use the GPU.
        device = torch.device(f"cuda:{device_num}")
        print("There are %d GPU(s) available." % torch.cuda.device_count())
        print("We will use the GPU:", torch.cuda.get_device_name(device_num))
    else:
        print("No GPU available, using the CPU instead.")
        device = torch.device("cpu")
    return device


def set_seed(seed_val=888):
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)


def uniqify(ls):
    non_empty_ls = list(filter(lambda x: x != "", ls))
    return list(dict.fromkeys(non_empty_ls))


def exclude_randrange(start, end, exclude):
    result = random.randrange(start, end)
    while result == exclude and end - start > 1:
        result = random.randrange(start, end)
    return result


def log_print(log_info, log_path: str):
    """Logging information"""
    print(log_info)
    with open(log_path, "a+") as f:
        f.write(f"{log_info}\n")
    # flush() is important for printing logs during multiprocessing
    sys.stdout.flush()


def banner(info=None, banner_len=60, sym="-"):
    print()
    if not info:
        print(sym * banner_len)
    else:
        info = sym * ((banner_len - len(info)) // 2 - 1) + " " + info
        info = info + " " + sym * (banner_len - len(info) - 1)
        print(info)
    print()
