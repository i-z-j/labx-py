# Labx
Lab Environment Task Manager
## labx-py
Labx Python Client
### Usage
#### Install
```sh
pip install labx-py
```
#### Example
```py
import labx

# Initiate labx client and test connection
labx.connect()
# Or with custom labx service url
# labx.connect("http://labx-svc")
# Default labx service url can be set via env variable LABX_URL 

# Print connected state
print(labx.connected())

# Print worker profiles
print(labx.profiles())

# Print tasks
print(labx.tasks())

# Config and Run Task
cluster_cfg = {
    "worker_profile": "gpu-light",
    "worker_scale": 2
}
params = [
    {"img_url": "url1", "resol": 0},
    {"img_url": "url2", "resol": 0},
]
results = labx.run("my_task", cluster_cfg, params)
```
