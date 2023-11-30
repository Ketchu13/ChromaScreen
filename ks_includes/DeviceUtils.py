import subprocess
import time

import pyudev


class DeviceUtils:

    def __init__(self, timeout=120, _callback=None):
        self.wait_device_timeout = timeout
        self.observer = None
        self.process_run = True
        self.device = None
        self.callback = _callback
        self.detected_devices = []
        self.time_to_stop = False

    def get_existing_usb_serial(self):

        pass

    def get_device_by_devlink(self, devlink):
        context = pyudev.Context()
        devices = context.list_devices(subsystem='tty')
        for device in devices:
            if devlink in device['DEVLINKS']:
                return device

    def get_deviceDict_by_devlink(self, devlink):
        device = self.get_device_by_devlink(devlink)

        if device:

            frdevice = {}
            # print("\n\n")
            device_props_keys = list(device.properties)
            print("device_props_keys", device_props_keys)
            for device_p_prop in device_props_keys:

                print(device_p_prop,device.properties[device_p_prop])
                frdevice[device_p_prop] = device.properties[device_p_prop]
            """device_child_count = len(list(device.children))
            print("device_child_count", device_child_count)
            device_data = list(device.children)[1].properties
            print("device_data", device_data)
            properties = list(device_data)
            print(properties)
            for _property in properties:
                print(_property, device_data[_property])
                frdevice[_property] = device_data[_property]"""

            return frdevice
        return None

    def wait_for_new_devicez(self):
        # timeout
        start_time = time.time()

        context_udev = pyudev.Context()

        monitor = pyudev.Monitor.from_netlink(context_udev)
        monitor.filter_by(subsystem='usb')
        monitor.start()
        print("monitor started")
        self.observer = pyudev.MonitorObserver(monitor, self.events_manager)


        try:
            self.observer.start()
            print("observer started")
            while self.process_run and ((time.time() - start_time) < self.wait_device_timeout):
                continue
        except KeyboardInterrupt:
            pass
        finally:
            self.process_run = False
            self.observer.stop()
            self.observer.join()

    # stop observer
    def stop(self):
        self.process_run = False

    # start observer
    def start(self):
        self.process_run = True
        self.wait_for_new_devicez()

    # events manager for observer
    def events_manager(self, action, device, oth=None):
        if device.action == "remove":
            return None
        if device.action == "add":
            frdevice = {}
            #print("\n\n")
            device_props_keys = list(device.properties)
            for device_p_prop in device_props_keys:
                # print(device_p_prop,device.properties[device_p_prop])
                frdevice[device_p_prop] = device.properties[device_p_prop]
            device_data = list(device.children)[1].properties
            properties = list(device_data)
            # print(properties)
            if "SUBSYSTEM" in properties:

                for _property in properties:
                    #print(_property, device_data[_property])
                    frdevice[_property] = device_data[_property]

                if "DEVNAME" in frdevice:
                    device_name = frdevice["DEVNAME"]
                    device_exist = False
                    for detected_device in self.detected_devices:
                        if detected_device["DEVNAME"] == device_name or detected_device["ID_PATH"] == frdevice["ID_PATH"] or detected_device["ID_PATH"].startswith(frdevice["ID_PATH"]) or frdevice["ID_PATH"].startswith(detected_device["ID_PATH"]):
                            device_exist = True
                            detected_device.update(frdevice)
                            break

                    if not device_exist:
                        # print(self.detected_devices)
                        self.detected_devices.append(frdevice)
                        # print(self.detected_devices)

                # serial available stop now
                if device_data["SUBSYSTEM"] == "tty" and frdevice["DEVTYPE"] == "usb_interface":
                    # callbak device ready to test
                    # print("call callback")
                    self.callback(self.detected_devices[0])
                    self.stop()
                    return
