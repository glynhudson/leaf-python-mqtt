# leaf-python-mqtt

Hacked together script to extract data from Nissan Leaf API using [pycarwings2](https://github.com/cedric222/pycarwings2) and post to mqtt

## Install Requirements

**Requires python 2.7.9 & python pip**

### Install carwings python lib

`pip install git+https://github.com/jdhorne/pycarwings2.git`

See [pycarwings2 repo](https://github.com/cedric222/pycarwings2) for more info

### Install other python libs

`pip install schedule datetime paho-mqtt time`

*pip may require `sudo`*


## Install Script 

Clone this repo:

`$ git clone https://github.com/glynhudson/leaf-python-mqtt`

Create config file using default file as a template:

```
$ cd leaf-python-mqtt
$ cp default.config.ini config.ini
$ nano config.ini
```
Test script by running

`$ ./leaf-python-mqtt.py`

## Run script as system service

### Create logfile

```
$ sudo mkdir /var/log/leaf-python-mqtt
$ sudo touch /var/log/leaf-python-mqtt/leaf-python-mqtt.log
$ sudo chmod 666 /var/log/leaf-python-mqtt/leaf-python-mqtt.log
```

### Create Systemd service 

Create systemd service, assuming repo was cloned to `/home/pi` folder on a RaspberryPi, adjust paths if needed

`$ sudo cp leaf-python-mqtt.service /lib/systemd/system/leaf-python-mqtt.service`

Set permissions: 

`sudo chmod 644  /lib/systemd/system/leaf-python-mqtt.service`

Reload systemd then enable the service:

```
$ sudo systemctl daemon-reload
$ sudo systemctl enable leaf-python-mqtt.service
```
Reboot the Pi

`$ sudo reboot`

Check service status with:

`sudo systemctl status leaf-python-mqtt.service`

Check log file with:

`$ tail /var/log/leaf-python-mqtt/leaf-python-mqtt.log`   
