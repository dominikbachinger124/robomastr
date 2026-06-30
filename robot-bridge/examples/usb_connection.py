"""RoboMaster S1 USB/RNDIS Connection.

Alternative zu WiFi - sehr stabil für lange Sessions.
Nutzt USB-Kabel direkt am Smart Central Control.
"""

from robomaster import robot, config

# Für USB/RNDIS Verbindung
config.LOCAL_IP_STR = "192.168.42.20"  # Beliebige IP im 192.168.42.x Netz

ep_robot = robot.Robot()

# conn_type='rndis' für USB-Verbindung
ep_robot.initialize(conn_type="rndis")

print(f"Verbunden via USB!")
print(f"Version: {ep_robot.get_version()}")
print(f"SN: {ep_robot.get_sn()}")

# Dein Code hier...
# ep_robot.chassis.move(x=1, y=0).wait_for_completed()

ep_robot.close()
