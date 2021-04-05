#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


def testInitInterrupt():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(1, MCP2221.TYPE.INTERRUPT)

    with pytest.raises(Exception):
        mcp2221.SetInterruptDetection()


def testInterruptPin():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(1, MCP2221.TYPE.INTERRUPT)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[23] & 0b111

    assert gp_type == 0b100
