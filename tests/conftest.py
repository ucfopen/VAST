import pytest
from click.testing import CliRunner

from vast.vast import Vast, VastConfig


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [("authorization", "DUMMY")],
    }


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture(scope="module")
def vast():
    return Vast(config=VastConfig.from_env())
