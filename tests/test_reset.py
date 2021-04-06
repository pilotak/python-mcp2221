#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


def testReset():
    mcp2221 = MCP2221.MCP2221()

    try:
        mcp2221.Reset()
    except Exception as err:
        pytest.fail(err)
