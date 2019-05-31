# Coherent-labmax-top-energy-meter-reader
*Hardware*

Coherent LabMax_TOP Laser Power/Energy Meter
https://www.coherent.com/measurement-control/measurement/labmax-top
Drivers

https://www.coherent.com/measurement-control/measurement/laser-measurement-and-control-help-center
http://www.asix.com.tw/products.php?op=pItemdetail&PItemID=122;74;110 (RS232 to PCI-E controller driver)
Get LabMax LabVIEW Drivers
Get LabMax LabVIEW-PC V1.7.1

*Setup*

Recommended to us RS232 serial connection over USB

Power meter communications
Press menu button
scroll down to 'communications'
set to RS232
set correct Baud Rate
Use serial cable to connect to pc
make sure serial ports show in device manager
download rs232 to pci-e controller drivers if necessary
Set correct Baud Rate
Validate that Labmax PC software shows readings
LabMax PC: Serial Connection Validation

Choose communication mode as: RS232
Pick address as COM port number
Set correct Baud Rate
Select correct "Available Mete' (should show up automaticall)
Click "Start Data Collection"

*RS-232 initialization*

https://github.com/ZhuangLab/storm-control/blob/master/sc_hardware/serial/RS232.py
Download Ver. 2.7.X to have pip package
You can use pyCharm's interface to download pyserial
http://pyserial.readthedocs.io/en/latest/shortintro.html
