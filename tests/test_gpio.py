#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221

mcp2221 = MCP2221.MCP2221()


@pytest.mark.parametrize("pin", [0, 1, 2, 3])
def testInitOutput(pin):
    mcp2221.InitGP(pin, MCP2221.TYPE.OUTPUT)
    buf = mcp2221._getConfig()

    assert buf[pin + 22] & 0b111 == 0 and ((buf[pin + 22] >> 3) & 0b1) == 0
