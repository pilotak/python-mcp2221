#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


@pytest.mark.parametrize("pin", [1, 2, 3])
def testInitADC(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.ADC)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[pin + 22] & 0b111

    assert gp_type == 0b010


def testVrefVDD():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.SetADCVoltageReference(MCP2221.VRM.VDD)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    vref = (buf[7] >> 3) & 0b11
    vrm = (buf[7] >> 2) & 0b1

    assert (vref, vrm) == (MCP2221.VRM.VDD.value, 0)


def testVrefVRM():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.SetADCVoltageReference(MCP2221.VRM.REF_2_048V)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    vref = (buf[7] >> 3) & 0b11
    vrm = (buf[7] >> 2) & 0b1

    assert (vref, vrm) == (MCP2221.VRM.REF_2_048V.value, 1)


def testInvalidVref():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(TypeError):
        mcp2221.SetADCVoltageReference(123)


def testReadAllADC():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(1, MCP2221.TYPE.ADC)
    mcp2221.InitGP(2, MCP2221.TYPE.ADC)
    mcp2221.InitGP(3, MCP2221.TYPE.ADC)

    adc = mcp2221.ReadAllADC()

    assert adc is not None


@pytest.mark.parametrize("pin", [1, 2, 3])
def testReadADC(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.ADC)

    adc = mcp2221.ReadADC(pin)

    assert 0 < adc < 1024


def testInvalidMaxADC():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(2, MCP2221.TYPE.ADC)

    with pytest.raises(ValueError):
        mcp2221.ReadADC(4)


def testInvalidMinADC():
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(2, MCP2221.TYPE.ADC)

    with pytest.raises(ValueError):
        mcp2221.ReadADC(0)
