import subprocess
import time

import pyudev


class SDCardUtils:

    def __init__(self, timeout=60):
        self.wait_device_timeout = timeout
        self.observer = None
        self.process_run = True
        self.device = None

    @staticmethod
    def get_mount_point_path(device):
        # print("get name point mount start")
        dev_name = device["DEVNAME"]
        try:
            # Exécuter la commande df pour obtenir les informations sur les points de montage
            resultat = subprocess.check_output(["df", "--output=target", dev_name], text=True)
            lignes = resultat.strip().split('\n')
            # Ignorer la première ligne (en-tête)
            if len(lignes) > 1:
                return dev_name, lignes[1]
        except subprocess.CalledProcessError:
            pass
        # print("Device: %s - Mount point: %s" % (dev_name, mount_point))
        return dev_name, None

    def get_device(self, device):
        if "usb" in str(device) and len(list(device.children)) > 0:
            list_d = list(device.children)[0].properties

            if 'ID_BUS' in list_d and list_d["ID_BUS"] == "usb":
                return self.get_mount_point_path(list_d)

        return None

    def get_existing_sd(self):
        context = pyudev.Context()
        # list all devices
        mp = None
        return [
            {"name": dev_name, "mp": mp}
            for device in context.list_devices(subsystem='block', DEVTYPE='disk')
            if (device_i := self.get_device(device))
            if (dev_name := device_i[0]) and (mp := device_i[1])
        ]

    def wait_for_new_device(self):
        # timeout
        start_time = time.time()
        self.process_run = True
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='block', device_type='disk')

        observer = pyudev.MonitorObserver(monitor, callback=self.events_manager)
        self.observer = observer

        try:
            observer.start()
            while self.process_run and ((time.time() - start_time) < self.wait_device_timeout):
                continue
        except KeyboardInterrupt:
            pass
        finally:
            self.process_run = False
            observer.stop()
            observer.join()

        return self.device

    # stop observer
    def stop(self):
        self.process_run = False

    # start observer
    def start(self):
        self.process_run = True
        return self.wait_for_new_device()

    # events manager for observer
    def events_manager(self, device):
        if device.action == "remove":
            return
        time.sleep(2)
        devices = self.get_existing_sd()
        if len(devices) > 0:
            # set device
            self.device = devices
            # stop observer loop
            self.process_run = False


# Exemple d'utilisation
"""sdu = SDCardUtils()

existing_sd_card = sdu.get_existing_sd()
if existing_sd_card:
    print("Existing sd device:", existing_sd_card)
else:
    print("No device found, waiting for new device..")
    print("New device:", sdu.start())"""
