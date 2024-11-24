# bambu-cli

A command-line interface for controlling Bambu Lab 3D printers via MQTT and FTPS protocols.

## Features

- Connect to Bambu Lab printers over local network
- Upload print files to printer
- Trigger print and track progress
- Pause, resume and cancel print in progress

## Installation

Either as a Python library:
```bash
pip install bambu-cli
```

or as a Docker image:
```bash
docker pull thegeektechworkshop/bambu-cli 
```

## Usage

If using the Docker image, it is recommended to create a shell script wrapper such as:
```bash
#!/usr/bin/env bash
docker run -it -v ~/.bambu-cli:/root/.bambu-cli -v $PWD:/root -w /root thegeektechworkshop/bambu-cli $@
```

First, add your printer configuration (ip, serial-number, access-code):
```bash
bambu add 192.168.1.100 01ABCD123456789 12345678 --name myP1S
```

Upload a file to print:
```bash
bambu upload myP1S my_print.gcode.3mf
```

Print the file
```bash
bambu print myP1S my_print.gcode.3mf
```

While print is in progress:
 - Press 'p' to pause the print job
 - Press 'r' to resume a paused print job
 - Press 'c' to cancel the print job
 - Press 'q' to exit the interface without affecting the print job

## License
GNU 3.0 License - see LICENSE file for details ```
