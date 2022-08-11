import tqdm
import time

pbar = tqdm.trange(0, 400, 1)

for idx, element in enumerate(pbar):
    time.sleep(0.01)
    pbar.set_description(f"No.{idx} -> {element}")
