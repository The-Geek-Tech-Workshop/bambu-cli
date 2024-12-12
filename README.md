# bambu-cli

A command-line interface for controlling Bambu Lab 3D printers via MQTT, HTTPS and FTPS protocols.

## Features

- Connect to Bambu Lab printers over LAN or Bambu Cloud
- Upload print files to local printer
- Trigger print and track progress
- Pause, resume and cancel print in progress

## Disclaimer

This tool is in a development state and is likely to have missing features, bugs and changes. Use freely within the terms of the license, but at your own risk

## Installation

Either from pip:
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

You can add a printer available directly on your local network: 
```bash
bambu add-local 
```

Or you can login to your Bambu Cloud account...:
```bash
bambu login user@example.com --password mypassword
```

... and then add a printer already associated with that account:
```bash
bambu add-cloud
```

Print a file. If the printer can be found on the local network it will be uploaded via FTPS first
```bash
bambu print myP1S my_print.gcode.3mf
```

AMS is supported. To enable it add the filament-slot mapping:
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
