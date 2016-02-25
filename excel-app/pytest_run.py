#!/bin/env python3

import pytest

pytest.main('--cov --cov-report html --ignore=venv/')
