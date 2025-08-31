# Run test at root directory with below:
#   python -m pytest labx

import labx
import pytest
from unittest.mock import patch, MagicMock
from typing import List
from labx.client import (
  Profile, Task, RunStatus, RunOutput
)

# ----------------------------
# Fixtures
# ----------------------------

@pytest.fixture
def mock_get():
    with patch("labx.client.httpx.Client.get") as m_get:
        yield m_get

@pytest.fixture
def mock_post():
    with patch("labx.client.httpx.Client.post") as m_post:
        yield m_post

@pytest.fixture
def connect(mock_get):
    # configure a default mock for connect
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "Connected to Labx.\n"
    mock_get.return_value = mock_response
    res = labx.connect()
    return res

# ----------------------------
# Connect Tests
# ----------------------------

def test_connect(connect, mock_get):
    assert connect == "Connected to Labx.\n"
    assert labx.connected()
    mock_get.assert_called_once_with(labx.DEFAULT_LABX_URL)

def test_connect_with_url(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "Connected to Labx.\n"
    mock_get.return_value = mock_response

    res = labx.connect("http://fake-url")

    assert res == "Connected to Labx.\n"
    assert labx.connected()
    mock_get.assert_called_once_with("http://fake-url")

# ----------------------------
# Profiles Tests
# ----------------------------

@pytest.fixture
def sample_profiles():
    return [
        {
            "name": "gpu-light",
            "desc": "gpu light",
            "cores": 20,
            "mem_gib": 250,
            "gpus": 1,
            "max_scale": 4,
        },
        {
            "name": "cpu-heavy",
            "desc": "cpu heavy",
            "cores": 8,
            "mem_gib": 100,
            "gpus": 0,
            "max_scale": 10,
        },
    ]

def test_profiles(connect, mock_get, sample_profiles):
    mock_get.reset_mock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_profiles
    mock_get.return_value = mock_response

    profiles: List[Profile] = labx.profiles()

    assert [p.model_dump() for p in profiles] == sample_profiles
    mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/profiles")

# ----------------------------
# Tasks Tests
# ----------------------------

@pytest.fixture
def sample_tasks():
    return [
        {
            "name": "image-registration",
            "desc": "image registration",
            "image": "image-registration:latest",
            "env_hints": {"gpu": True, "min_memory_gib": 32},
            "i_schema": {"img_url": "String", "resol": "Int"},
            "o_schema": {"result_url": "String"},
        },
        {
            "name": "image-segmentation",
            "desc": "image segmentation",
            "image": "image-segmentation:latest",
            "env_hints": {"min_memory_gib": 256},
            "i_schema": {"img_url": "String", "resol": "Int"},
            "o_schema": {"result_url": "String"},
        },
    ]

def test_tasks(connect, mock_get, sample_tasks):
    mock_get.reset_mock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_tasks
    mock_get.return_value = mock_response

    tasks: List[Task] = labx.tasks()

    assert [t.model_dump() for t in tasks] == sample_tasks
    mock_get.assert_called_once_with(f"{labx.DEFAULT_LABX_URL}/tasks")

# ----------------------------
# Run Tests
# ----------------------------

@pytest.fixture
def sample_run_request():
    run_req = labx.RunRequest(
        task_name="my_task",
        profile_name="gpu-light",
        params_list=[
            {"img_url": "url1", "resol": 0},
            {"img_url": "url2", "resol": 0},
        ],
        extra_cfg={},
    )
    return run_req

def test_run(connect, mock_post, sample_run_request):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "xxxx-0000-xxxx"
    mock_post.return_value = mock_response

    run_id = labx.run(sample_run_request)

    assert run_id == "xxxx-0000-xxxx"
    mock_post.assert_called_once_with(
        f"{labx.DEFAULT_LABX_URL}/run",
        json=sample_run_request.model_dump()
    )

# ----------------------------
# Status Tests
# ----------------------------

@pytest.fixture
def sample_status():
    return {
        "state": "running",
        "started_at": "",
        "finished_at": "",
    }

def test_status(connect, mock_post, sample_status):
    run_id = "xxxx-0000-xxxx"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_status
    mock_post.return_value = mock_response

    status: RunStatus = labx.status(run_id)

    assert status == RunStatus(**sample_status)
    mock_post.assert_called_once_with(
        f"{labx.DEFAULT_LABX_URL}/status", json={"run_id": run_id}
    )

# ----------------------------
# Output Tests
# ----------------------------

@pytest.fixture
def sample_output():
    return {
        "errors": [None, "Redis Error..."],
        "results": [{"result_url": "url1"}, None],
    }

def test_output(connect, mock_post, sample_output):
    run_id = "xxxx-0000-xxxx"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_output
    mock_post.return_value = mock_response

    output: RunOutput = labx.output(run_id)

    assert output == RunOutput(**sample_output)
    mock_post.assert_called_once_with(
        f"{labx.DEFAULT_LABX_URL}/output", json={"run_id": run_id}
    )
