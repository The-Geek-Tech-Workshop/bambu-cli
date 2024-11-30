# bambu-cli

A command-line interface for controlling Bambu Lab 3D printers via MQTT and FTPS protocols.

## Features

- Connect to Bambu Lab printers over local network or Bambu Cloud
- Upload print files to local printer
- Trigger print and track progress
- Pause, resume and cancel print in progress

## Disclaimer

This tool is in a development state and is likely to have missing features, bugs and changes. Use freely within the terms of the license, but at your own risk

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

You can add a printer available directly on your local network: (ip, serial-number, access-code):
```bash
bambu add-local 192.168.1.100 01ABCD123456789 12345678 --name myP1S
```

Or you can login to your Bambu Cloud account...:
```bash
pdm run bambu-cli login --email user@example.com --password mypassword
```

... and then add a printer already associated with that account:
```bash
pdm run bambu-cli add-cloud
```

Upload a file to print:
```bash
bambu upload myP1S my_print.gcode.3mf
```

Print the file
```bash
bambu print myP1S my_print.gcode.3mf
```

AMS is supported, to enable it add the filament-slot mapping:
```bash
bambu print myP1S my_print.gcode.3mf --ams 2 x 0
```


While print is in progress:
 - Press 'p' to pause the print job
 - Press 'r' to resume a paused print job
 - Press 'c' to cancel the print job
 - Press 'q' to exit the interface without affecting the print job

## License
GNU 3.0 License - see LICENSE file for details 
