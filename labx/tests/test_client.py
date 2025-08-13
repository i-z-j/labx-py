# Run test at root directory with below:
#   python -m unittest labx/tests/test_client.py

import unittest
from unittest.mock import MagicMock, patch
import labx


class TestClientConnect(unittest.TestCase):

    def setUp(self):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None

    @patch("labx.client.httpx.Client.get")
    def test_connect(self, mock_get):
        mock_get.return_value = self.mock_response

        labx.connect()

        self.assertTrue(labx.connected())
        mock_get.assert_called_once_with(labx.DEFAULT_LABX_URL)

    @patch("labx.client.httpx.Client.get")
    def test_connect_with_url(self, mock_get):
        mock_get.return_value = self.mock_response

        labx.connect("http://fake-url")

        self.assertTrue(labx.connected())
        mock_get.assert_called_once_with("http://fake-url")


class TestClientMethods(unittest.TestCase):

    @patch("labx.client.httpx.Client.get")
    def setUp(self, _):
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status.return_value = None
        self.mock_response.json.return_value = {"outputs": ["output1", "output2"]}

        labx.connect()

    @patch("labx.client.httpx.Client.get")
    def test_profiles(self, mock_get):
        mock_get.return_value = self.mock_response

        profiles = labx.profiles()

        self.assertEqual(profiles, {"outputs": ["output1", "output2"]})
        mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/profiles")

    @patch("labx.client.httpx.Client.get")
    def test_tasks(self, mock_get):
        mock_get.return_value = self.mock_response

        tasks = labx.tasks()

        self.assertEqual(tasks, {"outputs": ["output1", "output2"]})
        mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/tasks")

    @patch("labx.client.httpx.Client.post")
    def test_run(self, mock_post):
        mock_post.return_value = self.mock_response

        cluster_cfg = {"num_worker": 8, "worker_cfg": "gpu-light"}
        params = [
            {"img_url": "url1", "resol": 0},
            {"img_url": "url2", "resol": 0},
        ]
        results = labx.run("my_task", cluster_cfg, params)

        self.assertEqual(results, {"outputs": ["output1", "output2"]})
        mock_post.assert_called_once_with(
            f"{labx.DEFAULT_LABX_URL}/run",
            json={
                "task_name": "my_task",
                "cluster_cfg": {"num_worker": 8, "worker_cfg": "gpu-light"},
                "params": [
                    {"img_url": "url1", "resol": 0},
                    {"img_url": "url2", "resol": 0},
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
