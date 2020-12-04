import pytest
import numpy as np
import os

import dxx


@pytest.fixture
def mock_data_file() -> str:
    mock_file_name = "mock.DSB"
    sampling_freq = 48000
    mock_data = np.arange(5 * sampling_freq, dtype=np.int16)
    dxx.write(mock_file_name, mock_data)
    yield mock_file_name
    os.remove(mock_file_name)


def test_dxx_len_file(mock_data_file):
    assert dxx.len_file(mock_data_file) == 5 * 48000
