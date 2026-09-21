import os, time, requests
from huggingface_hub import HfApi

TOKEN = os.environ["HF_TOKEN"]
REPO = "carvendxu/sketchgraphs-full"
URL = "https://sketchgraphs.cs.princeton.edu/sequence/sg_all.npy"
CHUNK = 900 * 1024 * 1024

api = HfApi(token=TOKEN)
total = int(requests.head(URL, timeout=60).headers["Content-Length"])
print("total", total, flush=True)
n = (total + CHUNK - 1) // CHUNK
existing = set(api.list_repo_files(REPO, repo_type="dataset"))
for i in range(n):
    name = f"parts/sg_all.npy.part{i:03d}"
    if name in existing:
        print("skip", name, flush=True); continue
    start, end = i * CHUNK, min((i + 1) * CHUNK, total) - 1
    path = "/tmp/chunk.bin"
    t = time.time()
    with requests.get(URL, headers={"Range": f"bytes={start}-{end}"}, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for c in r.iter_content(4 * 1024 * 1024):
                f.write(c)
    print(f"chunk {i}: {os.path.getsize(path)} bytes in {time.time()-t:.0f}s", flush=True)
    api.upload_file(path_or_fileobj=path, path_in_repo=name, repo_id=REPO, repo_type="dataset")
    os.remove(path)
print("ALL DONE", flush=True)
