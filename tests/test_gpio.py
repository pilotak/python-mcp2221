#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


@pytest.mark.parametrize("pin", [0, 1, 2, 3])
def testInitOutput(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.OUTPUT)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[pin + 22] & 0b111
    direction = ((buf[pin + 22] >> 3) & 0b1)

    assert (gp_type, direction) == (0, 0)


@pytest.mark.parametrize("pin", [0, 1, 2, 3])
def testRead(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.OUTPUT)
    mcp2221.WriteGP(pin, 1)
    state = mcp2221.ReadGP(pin)

    assert state == 1


def testIOAll():
    mcp2221 = MCP2221.MCP2221()
    for i in range(4):
        mcp2221.InitGP(i, MCP2221.TYPE.OUTPUT)

    mcp2221.WriteAllGP(1, 1, 1, 1)
    state = mcp2221.ReadAllGP()

    assert state == [1, 1, 1, 1]


@pytest.mark.parametrize("pin", [0, 1, 2, 3])
def testInitInput(pin):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, MCP2221.TYPE.INPUT)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[pin + 22] & 0b111
    direction = ((buf[pin + 22] >> 3) & 0b1)

    assert (gp_type, direction) == (0, 1)


@pytest.mark.parametrize("pin,type,value", [
    (0, MCP2221.TYPE.SSPND, 0b001),
    (0, MCP2221.TYPE.LED_RX, 0b010),
    (1, MCP2221.TYPE.LED_TX, 0b011),
    (2, MCP2221.TYPE.USBCFG, 0b001),
    (3, MCP2221.TYPE.LED_I2C, 0b001)])
def testValidType(pin, type, value):
    mcp2221 = MCP2221.MCP2221()
    mcp2221.InitGP(pin, type)

    buf = [0] * 65
    buf[1] = 0x61  # get SRAM settings
    buf = mcp2221._send(buf)

    gp_type = buf[pin + 22] & 0b111

    assert gp_type == value


@pytest.mark.parametrize("pin,type", [
    (0, MCP2221.TYPE.LED_I2C),
    (1, MCP2221.TYPE.LED_RX),
    (2, MCP2221.TYPE.SSPND),
    (3, MCP2221.TYPE.CLOCK_OUT)])
def testInvalidType(pin, type):
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(TypeError):
        mcp2221.InitGP(pin, type)


def testInitInvalidPinNumber():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(ValueError):
        mcp2221.InitGP(4, MCP2221.TYPE.INPUT)


def testInvalidReadPin():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(ValueError):
        mcp2221.ReadGP(4)


def testInvalidWritePin():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(ValueError):
        mcp2221.WriteGP(4, 1)
