from ant.antplus.controller import AntPlusController
from ant.antplus.fec import FECDevice
from ant.antplus.bsc import BSBCDevice
from ant.antplus.pwr import PwrDevice
from ant.antplus.hrm import HrmDevice

import logging
import time  # for show_status time.sleep quick & dirty

# logging.basicConfig(filename='antplus_test.log',level=logging.INFO, format='%(asctime)s %(message)s')
logging.basicConfig(
    level=logging.FATAL, format="%(asctime)s %(message)s"
)  # not logging to file means printing to console
_logger = logging.getLogger("examples.antplus.test")


def on_new_device(channel_id):
    print(f"controller bgscan found device with channel id : {channel_id}")


def show_status(device):
    while True:
        print(device.status)
        print()
        time.sleep(1.0)


controller = AntPlusController()
controller.on_new_device = on_new_device


def start_scan():
    controller.start_scan()


def stop_scan():
    controller.stop_scan()


# test Direto
"""
direto profiles : 
device_number, device_type, transmission_type
6574, 11, 5
6574, 17, 5
6574, 121, 1
"""
fec = None
bsc = None
pwr = None
hrm = None


def start_fec():
    global fec
    fec = FECDevice(
        controller.node, 6574, 17, 5
    )  # device_number, device_type, transmission_type


def start_bsc():
    global bsc
    bsc = BSBCDevice(controller.node, 6574, 121, 1)


def start_pwr():
    global pwr
    pwr = PwrDevice(controller.node, 6574, 11, 5)

def start_hrm():
    global hrm
    hrm = HrmDevice(controller.node, 1, 120, 1)

def fec_calibration_callback(data):
    print(data)


def start_calibration():
    if fec:
        fec.start_calibration(None, fec_calibration_callback)


"""
calibratie Direto:
    -> je moet ZERO_OFFSET calib doen, dan krijg je quasi onmiddellijk een CALIBRATION_PROGRESS page
    -> de SPINDOWN calib is duidelijk niet ondersteund, want er komt geen enkele respons
    -> de PROGRESS messages komen ongeveer om de 3 seconden
    -> als je te traag trapt -> Speed : too low, als snel genoeg -> speed = OK
    -> dan stoppen met trappen, en na een paar seconden -> zero_offset_calibration_success = 1
    -> met temperature = FF, spindown_time : FFFF, zero_offset = 6279
    -> deze zero offset was telkens 6279 en 1x 6280
    
-> ook als je pwr.start_calibration() doet krijg je hetzelfde
-> pwr geeft geen progress updates, enkel een respons op het einde
-> we krijgen nu wel meer progress data, maar dat is allicht door de ant.py omdat die nu afwisselend van pwr en fec data krijgt 
en niet checkt of het dezelfde data zijn op hetzelfde kanaal
pwr geeft :status:success, calibration_data: 6279, auto_zero_status : ff (niet ondersteund)

"""


def stop():
    if fec:
        fec.close()
    if bsc:
        bsc.close()
    if pwr:
        pwr.close()
    if hrm:
        hrm.close()
    if controller:
        controller.close()


"""
Actual test

Start an instance of the power and heart rate monitors and print the available data.
The test is time limited, so the test can properly close the devices and ANT system before termination.
"""

start_hrm()
start_pwr()

for i in range(1, 60) :
    time.sleep(0.5)

    if pwr:
        cur_pwr = pwr.status["instant_power"]
        cur_cad = pwr.status["instant_cadence"]
    else:
        cur_pwr = -1
        cur_cad = -1

    if hrm:
        cur_hr = hrm.status["calculated_heart_rate"]
    else:
        cur_hr = -1
    
    print("Active HR: %3d, Cadence: %3d, Power: %3d." % (cur_hr, cur_cad, cur_pwr))

stop()