#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


@pytest.mark.parametrize("pin", [2, 3])
def testInitDAC(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.DAC)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[pin + 22] & 0b111

    assert gp_type == 0b011


def testVrefVDD():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.SetDACVoltageReference(MCP2221.VRM.VDD)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    vref = (buf[6] >> 6) & 0b11
    vrm = (buf[6] >> 5) & 0b1

    assert (vref, vrm) == (MCP2221.VRM.VDD.value, 0)


def testVrefVRM():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.SetDACVoltageReference(MCP2221.VRM.REF_2_048V)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    vref = (buf[6] >> 6) & 0b11
    vrm = (buf[6] >> 5) & 0b1

    assert (vref, vrm) == (MCP2221.VRM.REF_2_048V.value, 1)


def testInvalidVref():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(TypeError):
        mcp2221.SetDACVoltageReference(123)


@pytest.mark.parametrize("pin", [2, 3])
def testWriteDAC(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.DAC)

    mcp2221.WriteDAC(12)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    assert buf[6] & 0b1111 == 12


def testInvalidMaxDAC():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(2, MCP2221.TYPE.DAC)

    with pytest.raises(ValueError):
        mcp2221.WriteDAC(32)


def testInvalidMinDAC():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(2, MCP2221.TYPE.DAC)

    with pytest.raises(ValueError):
        mcp2221.WriteDAC(-1)
