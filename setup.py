import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcp2221",
    version="1.0.0",
    author="Pavel Slama",
    author_email="info@pavelslama.cz",
    description="Python driver for MCP2221A",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['MCP2221', 'MCP2221A', 'GPIO', 'ADC', 'DAC', 'I2C'],
    url="https://github.com/pilotak/python-mcp2221",
    project_urls={
        "Bug Tracker": "https://github.com/pilotak/python-mcp2221/issues",
    },
    packages=setuptools.find_packages(),
    install_requires=['hidapi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
