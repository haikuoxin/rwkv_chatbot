
import torch
from src.module.backends import Backends
from src.module.backends.base import module
import torch
from typing import Dict
from tqdm import tqdm


def loadWeights(mode, Path, *args, **kwargs):
    n_layer = 0

    w: Dict[str, torch.Tensor] = torch.load(
        Path, map_location="cpu")
    # refine weights
    keys = list(w.keys())
    for x in keys:
        if '.time_' in x:
            w[x] = w[x].squeeze()

        if '.time_decay' in x:
            w[x] = torch.exp(-torch.exp(w[x].double())
                             )

        if 'receptance.weight' in x:
            w[x] = -w[x]

        w[x].requires_grad = False

        try:
            if (int(x.split('.')[1])+1 > n_layer):
                n_layer = int(x.split('.')[1])+1
        except:
            pass

    # store weights in self.w

    keys = list(w.keys())

    # Load Backend
    ops: module = Backends[mode](
        n_layer, len(w[f"blocks.0.ffn.time_mix_k"]), *args, **kwargs)

    # Transform Weights from backend
    for x in tqdm(list(w.keys())):
        if "emb.weight" in x:
            w[x] = ops.stack(list(map(lambda rrx: ops.initTensor(
                rrx.squeeze()), w[x].split(1, 0))))
        else:
            w[x] = ops.initTensor(w[x])

    return ops, w