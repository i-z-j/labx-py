# Run test at root directory with below:
#   python -m unittest labx/tests/test_client.py

import unittest
from unittest.mock import MagicMock, patch
import labx


class TestConnect(unittest.TestCase):

    def setUp(self):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.mock_response.text = "Connected to Labx.\n"

    @patch("labx.client.httpx.Client.get")
    def test_connect(self, mock_get):
        mock_get.return_value = self.mock_response

        res = labx.connect()

        self.assertEqual(res, "Connected to Labx.\n")
        self.assertTrue(labx.connected())
        mock_get.assert_called_once_with(labx.DEFAULT_LABX_URL)

    @patch("labx.client.httpx.Client.get")
    def test_connect_with_url(self, mock_get):
        mock_get.return_value = self.mock_response

        res = labx.connect("http://fake-url")

        self.assertEqual(res, "Connected to Labx.\n")
        self.assertTrue(labx.connected())
        mock_get.assert_called_once_with("http://fake-url")


class TestProfiles(unittest.TestCase):

    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.profiles = [
            {
                "name"              : "gpu-light",
                "description"       : "gpu light",
                "worker_cores"      : 4,
                "worker_memory_gib" : 32,
                "worker_gpus"       : 1,
            },
            {
                "name"              : "cpu-heavy",
                "description"       : "cpu heavy",
                "worker_cores"      : 8,
                "worker_memory_gib" : 256,
                "worker_gpus"       : 0,
            }
        ]
        self.mock_response.json.return_value = self.profiles

        labx.connect()

    @patch("labx.client.httpx.Client.get")
    def test_profiles(self, mock_get):
        mock_get.return_value = self.mock_response

        profiles = labx.profiles()

        self.assertEqual(profiles, self.profiles)
        mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/profiles")


class TestTasks(unittest.TestCase):

    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.tasks = [
            {
                "name"         : "image-registration",
                "description"  : "image registration",
                "worker_image" : "image-registration:latest",
                "requirements" : {"gpu": True, "min_memory_gib": 32},
                "input"        : {"img_url": "String", "resol": "Int"},
                "output"       : {"result_url": "String"},
            },
            {
                "name"         : "image-segmentation",
                "description"  : "image segmentation",
                "worker_image" : "image-segmentation:latest",
                "requirements" : {"min_memory_gib": 256},
                "input"        : {"img_url": "String", "resol": "Int"},
                "output"       : {"result_url": "String"},
            }
        ]
        self.mock_response.json.return_value = self.tasks

        labx.connect()

    @patch("labx.client.httpx.Client.get")
    def test_tasks(self, mock_get):
        mock_get.return_value = self.mock_response

        tasks = labx.tasks()

        self.assertEqual(tasks, self.tasks)
        mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/tasks")


class TestRun(unittest.TestCase):

    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.run_id = "xxxx-0000-xxxx"
        self.mock_response.text = self.run_id
        self.task_name = "my-task"
        self.cluster_cfg = {"worker_profile": "gpu-light", "worker_scale": 2}
        self.params = [
            {"img_url": "url1", "resol": 0},
            {"img_url": "url2", "resol": 0},
        ]

        labx.connect()

    @patch("labx.client.httpx.Client.post")
    def test_run(self, mock_post):
        mock_post.return_value = self.mock_response

        run_id = labx.run(self.task_name, self.cluster_cfg, self.params)

        self.assertEqual(run_id, self.run_id)
        mock_post.assert_called_once_with(
            f"{labx.DEFAULT_LABX_URL}/run",
            json={
                "task_name": self.task_name,
                "cluster_cfg": self.cluster_cfg,
                "params": self.params,
            },
        )


class TestStatus(unittest.TestCase):
    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.run_id = "xxxx-0000-xxxx"
        self.status = "running"
        self.mock_response.text = self.status

        labx.connect()

    @patch("labx.client.httpx.Client.post")
    def test_status(self, mock_post):
        mock_post.return_value = self.mock_response

        status = labx.status(self.run_id)

        self.assertEqual(status, self.status)
        mock_post.assert_called_once_with(
            f"{labx.DEFAULT_LABX_URL}/status",
            json={
                "run_id": self.run_id,
            },
        )


class TestOutput(unittest.TestCase):
    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.run_id = "xxxx-0000-xxxx"
        # Note: below value is for test
        #       in pratice only one of error/results would have non-empty value
        self.output = {
            "error": {"message": "Redis Error..."},
            "results": [
                {"result_url": "url1"},
                {"result_url": "url2"},
            ],
        }

        self.mock_response.json.return_value = self.output

        labx.connect()

    @patch("labx.client.httpx.Client.post")
    def test_output(self, mock_post):
        mock_post.return_value = self.mock_response

        output = labx.output(self.run_id)

        self.assertEqual(output, self.output)
        mock_post.assert_called_once_with(
            f"{labx.DEFAULT_LABX_URL}/output",
            json={
                "run_id": self.run_id,
            },
        )


if __name__ == "__main__":
    unittest.main()
