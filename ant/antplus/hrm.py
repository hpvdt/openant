from .device import AntPlusDevice

import array
import logging

_logger = logging.getLogger("ant.antplus.HRM")

# Heartrate monitor
class HrmDevice(AntPlusDevice):
    CHANNEL_PERIOD = 8070
    DEVICE_TYPE = 120

    class Page:
        DEFAULT_DATA = 0
        CUMMULATIVE_OPERATING_TIME = 1
        PREV_BEAT_TIME = 4
        SWIM_INTERVAL_SUMMARY = 5
        CAPABILITIES = 6
        MODE_SETTINGS = 76

        # Overwrite some device defaults
        MANUFACTURER_INFO = 2
        PRODUCT_INFO = 3
        BATTERY_STATUS = 7
        

    def __init__(self, node, device_number, device_type, transmission_type):
        if device_type != HrmDevice.DEVICE_TYPE:
            # TODO : eigenlijk willen we hier een error genereren en een leeg object teruggeven
            print(
                f"Error, device_type = {device_type} is not a heart rate sensor!"
            )
            return
        channel_period = HrmDevice.CHANNEL_PERIOD

        super().__init__(
            node, device_number, device_type, transmission_type, channel_period
        )
        # specific init for the HRM device
        self.status["calculated_heart_rate"] = 0
        self.status["heart_beat_count"] = 0
        self.status["heart_beat_event_time"] = 0
        self.status["cumulative_operating_time"] = 0
        self.status["previous_heart_beat_time"] = 0
        self.status["interval_average_heart_rate"] = 0
        self.status["interval_max_heart_rate"] = 0
        self.status["interval_min_heart_rate"] = 0
        self.status["features_supported"] = 0
        self.status["features_enabled"] = 0

    def on_antplus_bcdata(self, data):
        # handle HRM specific pages here
        status = self.status

        # HRM uses bits 0:6 for page (omit bit 7 since it alternates every 4 messages)
        data[0] = data[0] & 0x7F

        # Constant info in every package
        self.status["calculated_heart_rate"] = data[7]
        self.status["heart_beat_count"] = data[6]
        self.status["heart_beat_event_time"] = (1.0/1024.0) * int.from_bytes(
            data[4:5], byteorder="little"
        )

        # Process bytes 1 to 3 as needed

        if  data[0] == HrmDevice.Page.DEFAULT_DATA:
            # All bytes will be 0xFF
            pass
        elif data[0] == HrmDevice.Page.CUMMULATIVE_OPERATING_TIME:
            self.status["cumulative_operating_time"] = 2 * int.from_bytes(
                data[1:3], byteorder="little"
            )
        elif data[0] == HrmDevice.Page.PREV_BEAT_TIME:
            self.status["previous_heart_beat_time"] = (1.0/1024.0) * int.from_bytes(
                data[2:3], byteorder="little"
            )
        elif data[0] == HrmDevice.Page.SWIM_INTERVAL_SUMMARY:
            self.status["interval_average_heart_rate"] = data[1]
            self.status["interval_max_heart_rate"] = data[2]
            self.status["interval_min_heart_rate"] = data[3]
        elif data[0] == HrmDevice.Page.CAPABILITIES:
            self.status["features_supported"] = data[2]
            self.status["features_enabled"] = data[3]
        else:
            pass
        
        # TODO: Add code specific to HRM for getting battery, manufacturer, and product information
        # TODO: Add code for changing HRM mode (data page 76)

        # base class gets everything too, so it can handle the wait for page events
        super().on_antplus_bcdata(data)
        # notify callback or polling self.status?

    