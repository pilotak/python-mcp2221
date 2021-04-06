#!/usr/bin/env python3

import pytest
from MCP2221 import MCP2221


def testDeviceInfo():
    mcp2221 = MCP2221.MCP2221()
    info = mcp2221.GetDeviceInfo()

    m = "manufacturer" in info
    p = "product" in info
    s = "serial" in info

    assert (m, p, s) == (True, True, True)


def testWriteReadFlash():
    mcp2221 = MCP2221.MCP2221()
    buf = [0] * 4

    buf[0] = 0b1000  # GP0 as input
    buf[1] = 0b1000  # GP1 as input
    buf[2] = 0b1000  # GP2 as input
    buf[3] = 0b1000  # GP3 as input

    mcp2221.WriteFlash(MCP2221.FLASH.GP_SETTING, buf)
    buf = mcp2221.ReadFlash(MCP2221.FLASH.GP_SETTING)

    gp0 = buf[0] & 0b1111
    gp1 = buf[1] & 0b1111
    gp2 = buf[2] & 0b1111
    gp3 = buf[3] & 0b1111

    assert (gp0, gp1, gp2, gp3) == (0b1000, 0b1000, 0b1000, 0b1000)


def testReadSerialNumber():
    mcp2221 = MCP2221.MCP2221()
    buf = mcp2221.ReadFlash(MCP2221.FLASH.USB_SERIAL_NUMBER)

    valid = buf[0] == 3
    buf_len = len(buf)

    assert (buf_len, valid) == (22, True)


def testInvalidReadFlashAddress():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(TypeError):
        mcp2221.ReadFlash(123)


def testInvalidWriteFlashAddress():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(TypeError):
        mcp2221.WriteFlash(123, [])


def testInvalidWriteFlashAddressMax():
    mcp2221 = MCP2221.MCP2221()
    buf = [0] * 61

    with pytest.raises(ValueError):
        mcp2221.WriteFlash(MCP2221.FLASH.USB_SERIAL_NUMBER, buf)


def testInvalidWriteFlashAddressMin():
    mcp2221 = MCP2221.MCP2221()

    with pytest.raises(ValueError):
        mcp2221.WriteFlash(MCP2221.FLASH.USB_SERIAL_NUMBER, [])
