from __future__ import print_function

import sys
import time

from dagster.core.execution.compute_logs import mirror_stream_to_file
from dagster.utils.test import get_temp_file_name


def test_capture():
    with get_temp_file_name() as capture_filepath:
        with mirror_stream_to_file(sys.stdout, capture_filepath):
            time.sleep(0.5)
            print('HELLO')
            time.sleep(0.5)

        with open(capture_filepath, 'r') as capture_stream:
            assert 'HELLO' in capture_stream.read()
