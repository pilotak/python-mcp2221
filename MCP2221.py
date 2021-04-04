""" MIT License

Copyright (c) 2021 Pavel Slama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. """

import hid
from time import sleep
from enum import Enum, unique
from typing import Dict, List, Union


@unique
class GP0(Enum):
    INPUT = 4
    OUTPUT = 3
    LED_RX = 2
    SSPND = 1


@unique
class GP1(Enum):
    INPUT = 6
    OUTPUT = 5
    INTERRUPT = 4
    LEDX = 3
    ADC = 2
    CLOCK_OUT = 1


@unique
class GP2(Enum):
    INPUT = 5
    OUTPUT = 4
    DAC = 3
    ADC = 2
    USBCFG = 1


@unique
class GP3(Enum):
    INPUT = 5
    OUTPUT = 4
    DAC = 3
    ADC = 2
    LED_I2C = 1


@unique
class VRM(Enum):
    VDD = 0
    REF_1_024V = 1
    REF_2_048V = 2
    REF_4_096V = 3


@unique
class DUTY(Enum):
    CYCLE_0 = 0
    CYCLE_25 = 1
    CYCLE_50 = 2
    CYCLE_75 = 3


@unique
class CLOCK(Enum):
    DIV_375KHZ = 0b111
    DIV_750KHZ = 0b110
    DIV_1_5MHZ = 0b101
    DIV_3MHZ = 0b100
    DIV_6MHZ = 0b011
    DIV_12MHZ = 0b010
    DIV_24MHZ = 0b001


@unique
class FLASH(Enum):
    CHIP_SETTING = 0x00
    GP_SETTING = 0x01
    USB_MANUFACTURER = 0x02
    USB_PRODUCT_DESCRIPTOR = 0x03
    USB_SERIAL_NUMBER = 0x04
    CHIP_SERIAL_NUMBER = 0x05


class MCP2221:
    def __init__(self, VID=0x04D8, PID=0x00DD, dev=0):
        self.mcp2221 = hid.device()
        self.mcp2221.open_path(hid.enumerate(VID, PID)[dev]["path"])
        self.VID = VID
        self.PID = PID

    def _getConfig(self):
        """ Get current config & prepare for set """

        buf = [0] * 65
        buf[1] = 0x61  # get SRAM settings
        rbuf = self._send(buf)
        print(rbuf)

        buf[0 + 1] = 0x60  # set SRAM settings

        # Clock Output Divider Value
        buf[2 + 1] |= (rbuf[5] & 0b11111)
        print("Clock divider:", rbuf[5] & 0b111,
              "duty:", (rbuf[5] >> 3) & 0b11)

        # DAC Voltage Reference
        buf[3 + 1] |= rbuf[6] >> 5
        print("DAC ref:", (rbuf[6] >> 6) & 0b11, "VRM:", (rbuf[6] >> 5) & 0b1)

        # ADC Voltage Reference
        buf[5 + 1] |= (rbuf[7] >> 2) & 0b111
        print("ADC ref:", (rbuf[7] >> 3) & 0b11, "VRM:", (rbuf[7] >> 2) & 0b1)

        # Interrupt detection
        # TODO

        # GP0 Settings
        buf[8 + 1] = rbuf[22]
        print("GP0 type:", rbuf[22] & 0b111, "input:", (rbuf[22] >> 3) & 0b1)

        # GP1 Settings
        buf[9 + 1] = rbuf[23]
        print("GP1 type:", rbuf[23] & 0b111, "input:", (rbuf[23] >> 3) & 0b1)

        # GP2 Settings
        buf[10 + 1] = rbuf[24]
        print("GP2 type:", rbuf[24] & 0b111, "input:", (rbuf[24] >> 3) & 0b1)

        # GP3 Settings
        buf[11 + 1] = rbuf[25]
        print("GP3 type:", rbuf[25] & 0b111, "input:", (rbuf[25] >> 3) & 0b1)

        return buf

    def _send(self, buffer: List[int]) -> List[int]:
        """ Send buffer """

        self.mcp2221.write(buffer)
        return self.mcp2221.read(65)

    def SetClockOutput(self, value: DUTY, clock: CLOCK):
        """ Set clock output """

        if not isinstance(value, DUTY):
            raise ValueError("Invalid duty cycle value")
        if not isinstance(clock, CLOCK):
            raise ValueError("Invalid clock divider value")

        buf = self._getConfig()
        buf[2 + 1] |= 0b10000000  # set mode
        buf[2 + 1] |= clock.value
        buf[2 + 1] |= value.value << 3

        self._send(buf)

    def SetDACVoltageReference(self, ref: VRM):
        """ Set DAC voltage reference """

        if not isinstance(ref, VRM):
            raise ValueError("Invalid DAC voltage reference")

        buf = self._getConfig()
        buf[3 + 1] = 0b10000000  # set mode

        if ref != VRM.VDD:
            buf[3 + 1] |= ref.value << 1
            buf[3 + 1] |= 0b1

        self._send(buf)

    def WriteDAC(self, value: int):
        """ Write DAC value (0-31) """

        if not 0 <= value <= 31:
            raise ValueError("Invalid value")

        buf = self._getConfig()
        buf[4 + 1] |= 0b10000000  # set mode
        buf[4 + 1] |= value

        self._send(buf)

    def SetADCVoltageReference(self, ref: VRM):
        """ Set ADC voltage reference """

        if not isinstance(ref, VRM):
            raise ValueError("Invalid ADC voltage reference")

        buf = self._getConfig()
        buf[5 + 1] = 0b10000000  # set mode

        if ref != VRM.VDD:
            buf[5 + 1] |= ref.value << 1
            buf[5 + 1] |= 0b1  # VRM is used

        self._send(buf)

    def SetInterruptDetection(self):
        # TODO
        raise Exception("Not yet implemented")

    def InitGP(self, pin: int, type: Union[GP0, GP1, GP2, GP3],
               value: int = 0):
        """ Init GPIO """

        buf = self._getConfig()
        buf[7 + 1] = 0b10000000  # alter GPIO

        if pin == 0:
            if not isinstance(type, GP0):
                raise ValueError("Invalid type on pin GP0")

            buf[8 + 1] = 0
            if type == GP0.INPUT:
                buf[8 + 1] |= 1 << 3
            elif type == GP0.OUTPUT:
                buf[8 + 1] |= (value & 1) << 4
            else:
                buf[8 + 1] |= type.value

        elif pin == 1:
            if not isinstance(type, GP1):
                raise ValueError("Invalid type on pin GP1")

            buf[9 + 1] = 0
            if type == GP1.INPUT:
                buf[9 + 1] |= 1 << 3
            elif type == GP1.OUTPUT:
                buf[9 + 1] |= (value & 1) << 4
            else:
                buf[9 + 1] |= type.value

        elif pin == 2:
            if not isinstance(type, GP2):
                raise ValueError("Invalid type on pin GP2")

            buf[10 + 1] = 0
            if type == GP2.INPUT:
                buf[10 + 1] |= 1 << 3
            elif type == GP2.OUTPUT:
                buf[10 + 1] |= (value & 1) << 4
            else:
                buf[10 + 1] |= type.value

        elif pin == 3:
            if not isinstance(type, GP3):
                raise ValueError("Invalid type on pin GP3")

            buf[11 + 1] = 0
            if type == GP3.INPUT:
                buf[11 + 1] |= 1 << 3
            elif type == GP3.OUTPUT:
                buf[11 + 1] |= (value & 1) << 4
            else:
                buf[11 + 1] |= type.value
        else:
            raise ValueError("Invalid pin number")

        self._send(buf)

    def ReadGP(self):
        """ Read GPIOs in bulk (when set as input or output) """

        buf = [0] * 65
        buf[1] = 0x51  # Get GPIO Values
        buf = self._send(buf)

        if buf[0] == 0x51 and buf[1] == 0x00:
            return [buf[2], buf[4], buf[6], buf[8]]
        else:
            return None

    def ReadGP(self, pin: int) -> Union[int, None]:
        """ Read GPIO pin value (when set as input or output) """

        if not 0 <= pin <= 3:
            raise ValueError("Invalid pin number")

        gpio = self.ReadGP()

        if gpio:
            return gpio[pin]
        else:
            return None

    def WriteGP(self, gp0: Union[int, None], gp1: Union[int, None],
                gp2: Union[int, None], gp3: Union[int, None]):
        """ Write GPIO output """

        buf = [0] * 65
        buf[0 + 1] = 0x50  # Set GPIO Values

        if gp0 is not None:
            buf[2 + 1] = 1  # Alter GPIO output
            buf[3 + 1] = gp0  # output value

        if gp1 is not None:
            buf[6 + 1] = 1  # Alter GPIO output
            buf[7 + 1] = gp1  # output value

        if gp2 is not None:
            buf[10 + 1] = 1  # Alter GPIO output
            buf[11 + 1] = gp2  # output value

        if gp3 is not None:
            buf[14 + 1] = 1  # Alter GPIO output
            buf[15 + 1] = gp3  # output value

        self._send(buf)

    def WriteGP(self, pin: int, value: int):
        """ Write GPIO output """

        if not 0 <= pin <= 3:
            raise ValueError("Invalid pin number")

        buf = [0] * 65
        buf[0 + 1] = 0x50  # Set GPIO Values
        buf[2 + pin * 4 + 1] = 1  # Alter GPIO output
        buf[3 + pin * 4 + 1] = value & 1  # output value

        self._send(buf)

    def ReadADC(self):
        """ Read ADC in bulk """

        buf = [0] * 65
        buf[0 + 1] = 0x10  # Status/Set Parameters

        buf = self._send(buf)

        if buf[0] == 0x10 and buf[1] == 0x00:
            return [buf[50] | (buf[51] << 8),
                    buf[52] | (buf[53] << 8),
                    buf[54] | (buf[55] << 8)]
        else:
            return None

    def ReadADC(self, channel: int) -> Union[int, None]:
        """ Read specific ADC channel """

        if not 0 <= channel <= 2:
            raise ValueError("Invalid channel number")

        adc = self.ReadADC()

        if adc:
            return adc[channel]
        else:
            return None

    def GetDeviceInfo(self) -> Dict[str, str]:
        """ Get device information """

        output = dict()
        output["manufacturer"] = self.mcp2221.get_manufacturer_string()
        output["product"] = self.mcp2221.get_product_string()
        output["serial"] = self.mcp2221.get_serial_number_string()

        return output

    def ReadFlash(self, address: FLASH):
        """ Read data from flash """

        if not isinstance(address, FLASH):
            raise ValueError("Invalid flash address")

        buf = [0] * 65
        buf[0 + 1] = 0xB0  # Read Flash Data
        buf[1 + 1] = address.value

        buf = self._send(buf)

        if buf[0] == 0xB0 and buf[1] == 0x00:
            return buf[3:(3+buf[2])]
        else:
            return []

    def WriteFlash(self, address: FLASH, data: List[int]) -> Union[int, None]:
        """ Write data to flash """

        if not isinstance(address, FLASH) \
                or address == FLASH.CHIP_SERIAL_NUMBER:
            raise ValueError("Invalid flash address")

        if len(data) == 0 or len(data) > 60:
            raise ValueError("Invalid data length")

        buf = [0] * 3
        buf[0 + 1] = 0xB1  # Write Flash Data
        buf[1 + 1] = address.value

        fill = [0] * (65 - 3 - len(data))

        buf = self._send([*buf, *data, *fill])

        if buf[0] == 0xB1:
            return buf[1]
        else:
            return None

    def Reset(self):
        """ Reset the device """

        buf = [0x00, 0x70, 0xAB, 0xCD, 0xEF]
        fill = [0] * 60
        self.mcp2221.write([*buf, *fill])
        sleep(1)
