#!/usr/bin/env python3

from MCP2221 import MCP2221

def testClockOut():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(1, MCP2221.TYPE.CLOCK_OUT)
    mcp2221.SetClockOutput(MCP2221.DUTY.CYCLE_50, MCP2221.CLOCK.DIV_3MHZ)
    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    duty = (buf[5] >> 3) & 0b11
    clock = buf[5] & 0b111

    assert (duty, clock) == (
        MCP2221.DUTY.CYCLE_50.value, MCP2221.CLOCK.DIV_3MHZ.value)
