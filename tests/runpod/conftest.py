import pytest

def pytest_addoption(parser):

    # Pod名
    parser.addoption(
        "--pod-name", 
        action="store", 
        default="personyx_runpod_environment",
        help="RunPodのPod名を指定します"
    )

    # マシンタイプ
    parser.addoption(
        "--machine-type", 
        action="store", 
        default="cpu",
        help="RunPodのマシンタイプ(cpu or gpu)を指定します"
    )

@pytest.fixture
def pod_name(request):
    return request.config.getoption("--pod-name")

@pytest.fixture
def machine_type(request):
    return request.config.getoption("--machine-type")