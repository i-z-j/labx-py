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
run_req = labx.RunRequest(
    task_name="my_task",
    profile_name="gpu-light",
    params_list=[
        {"img_url": "url1", "resol": 0},
        {"img_url": "url2", "resol": 0},
    ],
    extra_cfg={}
)
run_id = labx.run(run_req)

# Waiting for Run ...
import time
while "running" == labx.status(run_id).state:
    time.sleep(60)
    print(f"Task {run_id} is running ...")

# Check Run Status and Output
print("Final Status:", labx.status(run_id))
print("Output:", labx.output(run_id))
```
