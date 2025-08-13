import os
import httpx

DEFAULT_LABX_URL = os.getenv("LABX_URL", "http://labx.labx.svc.cluster.local:80")

class LabxClient:

    def __init__(self,):
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
            return response.json()
        except httpx.HTTPError as e:
            print(f"Tasks request failed: {e}")
            return None

    def tasks(self):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            response = self.client.get(f"{self.url}/tasks")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Tasks request failed: {e}")
            return None

    def run(self, task_name: str, cluster_cfg: dict, params: list):
        if not self.connected:
            raise RuntimeError("Not connected to the Labx server.")
        try:
            response = self.client.post(
                f"{self.url}/run",
                json={"task_name": task_name, "cluster_cfg": cluster_cfg, "params": params},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Run request failed: {e}")
            return None
