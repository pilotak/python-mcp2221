import hid
from time import sleep
from enum import Enum, unique, auto
from typing import Dict, List, Union


class TYPE(Enum):
    INPUT = auto()
    OUTPUT = auto()
    ADC = auto()
    DAC = auto()
    CLOCK_OUT = auto()
    INTERRUPT = auto()
    LED_RX = auto()
    LED_TX = auto()
    LED_I2C = auto()
    SSPND = auto()
    USBCFG = auto()


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
        # print(rbuf)

        buf[0 + 1] = 0x60  # set SRAM settings

        # Clock Output Divider Value
        buf[2 + 1] |= (rbuf[5] & 0b11111)

        # DAC Voltage Reference
        buf[3 + 1] |= rbuf[6] >> 5

        # ADC Voltage Reference
        buf[5 + 1] |= (rbuf[7] >> 2) & 0b111

        # Interrupt detection
        # TODO

        # GP0 Settings
        buf[8 + 1] = rbuf[22]

        # GP1 Settings
        buf[9 + 1] = rbuf[23]

        # GP2 Settings
        buf[10 + 1] = rbuf[24]

        # GP3 Settings
        buf[11 + 1] = rbuf[25]

        return buf

    def _send(self, buffer: List[int]) -> List[int]:
        """ Send buffer """

        self.mcp2221.write(buffer)
        return self.mcp2221.read(65)

    def SetClockOutput(self, duty: DUTY, clock: CLOCK):
        """ Set clock output """

        if not isinstance(duty, DUTY):
            raise TypeError("Invalid duty cycle value")
        if not isinstance(clock, CLOCK):
            raise TypeError("Invalid clock divider value")

        buf = self._getConfig()
        buf[2 + 1] = 0b10000000  # set mode
        buf[2 + 1] |= clock.value
        buf[2 + 1] |= (duty.value << 3)

        self._send(buf)

    def SetDACVoltageReference(self, ref: VRM):
        """ Set DAC voltage reference """

        if not isinstance(ref, VRM):
            raise TypeError("Invalid DAC voltage reference")

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
            raise TypeError("Invalid ADC voltage reference")

        buf = self._getConfig()
        buf[5 + 1] = 0b10000000  # set mode

        if ref != VRM.VDD:
            buf[5 + 1] |= ref.value << 1
            buf[5 + 1] |= 0b1  # VRM is used

        self._send(buf)

    def SetInterruptDetection(self):
        # TODO
        raise Exception("Not yet implemented")

    def InitGP(self, pin: int, type: TYPE, value: int = 0):
        """ Init GPIO """

        buf = self._getConfig()
        buf[7 + 1] = 0b10000000  # alter GPIO

        if pin == 0:
            buf[8 + 1] = 0

            if type == TYPE.INPUT:
                buf[8 + 1] |= 1 << 3
            elif type == TYPE.OUTPUT:
                buf[8 + 1] |= (value & 1) << 4
            elif type == TYPE.SSPND:
                buf[8 + 1] |= 1
            elif type == TYPE.LED_RX:
                buf[8 + 1] |= 2
            else:
                raise TypeError("Invalid type on pin GP0")

        elif pin == 1:
            buf[9 + 1] = 0

            if type == TYPE.INPUT:
                buf[9 + 1] |= 1 << 3
            elif type == TYPE.OUTPUT:
                buf[9 + 1] |= (value & 1) << 4
            elif type == TYPE.CLOCK_OUT:
                buf[9 + 1] |= 1
            elif type == TYPE.ADC:
                buf[9 + 1] |= 2
            elif type == TYPE.LED_TX:
                buf[9 + 1] |= 3
            elif type == TYPE.INTERRUPT:
                buf[9 + 1] |= 4
            else:
                raise TypeError("Invalid type on pin GP1")

        elif pin == 2:
            buf[10 + 1] = 0

            if type == TYPE.INPUT:
                buf[10 + 1] |= 1 << 3
            elif type == TYPE.OUTPUT:
                buf[10 + 1] |= (value & 1) << 4
            elif type == TYPE.USBCFG:
                buf[10 + 1] |= 1
            elif type == TYPE.ADC:
                buf[10 + 1] |= 2
            elif type == TYPE.DAC:
                buf[10 + 1] |= 3
            else:
                raise TypeError("Invalid type on pin GP2")

        elif pin == 3:
            buf[11 + 1] = 0

            if type == TYPE.INPUT:
                buf[11 + 1] |= 1 << 3
            elif type == TYPE.OUTPUT:
                buf[11 + 1] |= (value & 1) << 4
            elif type == TYPE.LED_I2C:
                buf[11 + 1] |= 1
            elif type == TYPE.ADC:
                buf[11 + 1] |= 2
            elif type == TYPE.DAC:
                buf[11 + 1] |= 3
            else:
                raise TypeError("Invalid type on pin GP3")

        else:
            raise ValueError("Invalid pin number")

        self._send(buf)

    def ReadAllGP(self):
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

        gpio = self.ReadAllGP()

        if gpio:
            return gpio[pin]
        else:
            return None

    def WriteAllGP(self, gp0: Union[int, None], gp1: Union[int, None],
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

    def ReadAllADC(self):
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

        if not 1 <= channel <= 3:
            raise ValueError("Invalid channel number")

        adc = self.ReadAllADC()

        if adc:
            return adc[channel - 1]
        else:
            return None

    def GetDeviceInfo(self) -> Dict[str, Union[str, None]]:
        """ Get device information """

        output = dict()
        output["manufacturer"] = self.mcp2221.get_manufacturer_string()
        output["product"] = self.mcp2221.get_product_string()
        output["serial"] = self.mcp2221.get_serial_number_string()

        return output

    def ReadFlash(self, address: FLASH):
        """ Read data from flash """

        if not isinstance(address, FLASH):
            raise TypeError("Invalid flash address")

        buf = [0] * 65
        buf[0 + 1] = 0xB0  # Read Flash Data
        buf[1 + 1] = address.value

        buf = self._send(buf)

        if buf[0] == 0xB0 and buf[1] == 0x00:

            if address == FLASH.GP_SETTING or \
                    address == FLASH.CHIP_SETTING or \
                    address == FLASH.CHIP_SERIAL_NUMBER:
                return buf[4:(4+buf[2])]
            else:
                return buf[3:(3+buf[2])]
        else:
            return []

    def WriteFlash(self, address: FLASH, data: List[int]) -> Union[int, None]:
        """ Write data to flash """

        if not isinstance(address, FLASH) \
                or address == FLASH.CHIP_SERIAL_NUMBER:
            raise TypeError("Invalid flash address")

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
