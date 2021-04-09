# Python driver for MCP2221/A
[![Build](https://github.com/pilotak/python-mcp2221/actions/workflows/validate.yaml/badge.svg)](https://github.com/pilotak/python-mcp2221/actions/workflows/validate.yaml)
[![PyPI](https://img.shields.io/pypi/v/mcp2221)](https://pypi.org/project/mcp2221/)

## Examples

Read GP0
```python
from MCP2221 import MCP2221

mcp2221 = MCP2221.MCP2221()
mcp2221.InitGP(0, MCP2221.TYPE.INPUT)
print(mcp2221.ReadGP(0))
```

Write GP0
```python
from MCP2221 import MCP2221

mcp2221 = MCP2221.MCP2221()
mcp2221.InitGP(0, MCP2221.TYPE.OUTPUT)
print(mcp2221.WriteGP(0, 1))
```

Read ADC on GP1
```python
from MCP2221 import MCP2221

mcp2221 = MCP2221.MCP2221()
mcp2221.InitGP(1, MCP2221.TYPE.ADC)
mcp2221.SetADCVoltageReference(MCP2221.VRM.VDD)
print(mcp2221.ReadADC(1))
```

Write DAC on GP2
```python
from MCP2221 import MCP2221

mcp2221 = MCP2221.MCP2221()
mcp2221.InitGP(2, MCP2221.TYPE.DAC)
mcp2221.SetDACVoltageReference(MCP2221.VRM.REF_2_048V)
mcp2221.WriteDAC(12)
```

## Tests
```sh
pip install pytest pytest-cov
pytest tests/ --doctest-modules --cov=MCP2221
```