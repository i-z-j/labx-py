import os
import httpx

# ----- Pydantic models -----
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# TODO: use dedicated repo to sync api schema between client and backend

class Profile(BaseModel):
    name        : str
    desc        : str
    cores       : int
    mem_gib     : int
    gpus        : int
    max_scale   : int

class Task(BaseModel):
    name        : str
    desc        : str
    image       : str
    env_hints   : Dict[str, Any]
    i_schema    : Dict[str, Any]
    o_schema    : Dict[str, Any]

class RunRequest(BaseModel):
    task_name       : str
    profile_name    : str
    params_list     : List[Dict[str, Any]]
    extra_cfg       : Dict[str, Any]

class RunIdRequest(BaseModel):
    run_id: str

class RunStatus(BaseModel):
    state         : str
    started_at    : str
    finished_at   : str

class RunOutput(BaseModel):
    errors    : List[Optional[str]]
    results   : List[Optional[str]]


# ----- Global configuration -----
DEFAULT_LABX_URL = os.getenv("LABX_URL", "http://labx-manager.labx.svc.cluster.local")

# ----- Main class -----
class LabxClient:

    def __init__(self):
        self.url = None
        self.client = httpx.Client()
        self.connected = False

    def connect(self, url:str=DEFAULT_LABX_URL):
        self.url = url
        try:
            response = self.client.get(self.url)
            response.raise_for_status()
            self.connected = True
            return response.text
        except httpx.RequestError as e:
            print(f"Connection error: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")

    def profiles(self):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            response = self.client.get(f"{self.url}/profiles")
            response.raise_for_status()
            profiles = [Profile(**p) for p in response.json()]
            return profiles
        except httpx.HTTPError as e:
            print(f"Tasks request failed: {e}")
            return None

    def tasks(self):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            response = self.client.get(f"{self.url}/tasks")
            response.raise_for_status()
            tasks = [Task(**t) for t in response.json()]
            return tasks
        except httpx.HTTPError as e:
            print(f"Tasks request failed: {e}")
            return None

    def run(self, run_req:RunRequest):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            response = self.client.post(
                f"{self.url}/run",
                json=run_req.model_dump(),
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"Run request failed: {e}")
            return None

    def status(self, run_id:str):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            run_id_req = RunIdRequest(run_id=run_id)
            response = self.client.post(
                f"{self.url}/status",
                json=run_id_req.model_dump(),
            )
            response.raise_for_status()
            return RunStatus(**response.json())
        except httpx.HTTPError as e:
            print(f"Run request failed: {e}")
            return None

    def output(self, run_id:str):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            run_id_req = RunIdRequest(run_id=run_id)
            response = self.client.post(
                f"{self.url}/output",
                json=run_id_req.model_dump(),
            )
            response.raise_for_status()
            return RunOutput(**response.json())
        except httpx.HTTPError as e:
            print(f"Run request failed: {e}")
            return None
