"""USB Connection Test and Debugger for RoboMaster S1.

Tests connection step by step to identify issues.
"""

import socket
import subprocess
import sys
import time
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# RoboMaster S1 Settings
ROBOT_IP = "192.168.42.2"
ROBOT_PORT = 40923
LOCAL_IP = "192.168.42.20"


def test_network_interface():
    """Test 1: Check if network interface is configured."""
    print("\n" + "=" * 60)
    print("TEST 1: Network Interface")
    print("=" * 60)

    try:
        result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True)

        if "192.168.42" in result.stdout:
            print("✅ Interface with 192.168.42.x found")
            # Extract interface name
            for line in result.stdout.split("\n"):
                if "192.168.42" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ No interface with 192.168.42.x IP found")
            print("\nFix: Configure interface manually:")
            print("   sudo ip addr add 192.168.42.20/24 dev <INTERFACE>")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ping():
    """Test 2: Ping the robot."""
    print("\n" + "=" * 60)
    print("TEST 2: Ping Robot")
    print("=" * 60)

    print(f"Pinging {ROBOT_IP}...")
    try:
        result = subprocess.run(
            ["ping", "-c", "3", "-W", "2", ROBOT_IP], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Robot responds to ping")
            print(result.stdout)
            return True
        else:
            print("❌ Robot not responding to ping")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tcp_connection():
    """Test 3: Test raw TCP connection."""
    print("\n" + "=" * 60)
    print("TEST 3: Raw TCP Connection")
    print("=" * 60)

    print(f"Connecting to {ROBOT_IP}:{ROBOT_PORT}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ROBOT_IP, ROBOT_PORT))
        print("✅ TCP connection successful!")

        # Try to send a command
        print("\nSending 'command' to enter SDK mode...")
        sock.send(b"command;")

        try:
            response = sock.recv(1024)
            print(f"✅ Response received: {response.decode('utf-8')}")
        except socket.timeout:
            print("⚠️ No response (timeout)")

        sock.close()
        return True

    except ConnectionRefusedError:
        print("❌ Connection refused - is the robot in SDK mode?")
        print("   Try: Restart robot and wait 10 seconds")
        return False
    except socket.timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sdk_import():
    """Test 4: Check if SDK can be imported."""
    print("\n" + "=" * 60)
    print("TEST 4: SDK Import")
    print("=" * 60)

    try:
        from robomaster import robot, config

        print("✅ robomaster SDK imported successfully")
        print(f"   SDK location: {robot.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Cannot import SDK: {e}")
        return False


def test_sdk_connection():
    """Test 5: Test SDK connection."""
    print("\n" + "=" * 60)
    print("TEST 5: SDK Connection")
    print("=" * 60)

    try:
        from robomaster import robot, config

        # Set local IP
        config.LOCAL_IP_STR = LOCAL_IP
        print(f"Set local IP to: {LOCAL_IP}")

        print("Creating robot instance...")
        ep_robot = robot.Robot()

        print("Initializing (conn_type='rndis')...")
        print("   (This may take 5-10 seconds)")

        ep_robot.initialize(conn_type="rndis")
        print("✅ SDK connection successful!")

        print("\nGetting robot info...")
        version = ep_robot.get_version()
        print(f"   Version: {version}")

        sn = ep_robot.get_sn()
        print(f"   SN: {sn}")

        battery = ep_robot.battery.get_battery()
        print(f"   Battery: {battery}%")

        ep_robot.close()
        print("✅ Connection test complete!")
        return True

    except Exception as e:
        print(f"❌ SDK connection failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_with_ap_mode():
    """Test 6: Try AP mode instead of RNDIS."""
    print("\n" + "=" * 60)
    print("TEST 6: Try AP Mode (alternative)")
    print("=" * 60)

    # For AP mode, robot is at 192.168.2.1
    ap_ip = "192.168.2.1"

    print(f"Testing AP mode ({ap_ip})...")
    print("(Requires WiFi connection to RoboMaster)")

    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ap_ip], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ Robot reachable at {ap_ip} via WiFi")
            print("   You can use conn_type='ap' with WiFi connection")
            return True
        else:
            print(f"❌ Robot not reachable at {ap_ip}")
            print("   Connect to RoboMaster WiFi first")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def diagnose_issue(results):
    """Diagnose the issue based on test results."""
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)

    network_ok = results.get("network", False)
    ping_ok = results.get("ping", False)
    tcp_ok = results.get("tcp", False)
    sdk_import_ok = results.get("sdk_import", False)
    sdk_conn_ok = results.get("sdk_conn", False)

    if not network_ok:
        print("\n🔴 PROBLEM: Network interface not configured")
        print("\nSolution:")
        print("1. Find your USB interface:")
        print("   ip addr | grep -E 'usb|enx'")
        print("\n2. Configure IP:")
        print("   sudo ip addr add 192.168.42.20/24 dev <INTERFACE>")
        print("   sudo ip link set <INTERFACE> up")
        return

    if not ping_ok:
        print("\n🔴 PROBLEM: Robot not reachable")
        print("\nPossible causes:")
        print("• RoboMaster is not powered on")
        print("• USB cable not connected to Smart Central Control")
        print("• RNDIS driver not loaded")
        print("• Wait 10+ seconds after powering on")
        print("\nCheck:")
        print("• dmesg | tail -20")
        print("• lsusb")
        return

    if not tcp_ok:
        print("\n🔴 PROBLEM: TCP connection refused")
        print("\nPossible causes:")
        print("• Robot not in SDK mode")
        print("• Port 40923 not open")
        print("\nSolution:")
        print("• Restart robot and try again")
        print("• Wait 10 seconds after power on")
        return

    if not sdk_import_ok:
        print("\n🔴 PROBLEM: SDK not installed")
        print("\nSolution:")
        print("   source .venv/bin/activate")
        print("   pip install robomaster")
        return

    if not sdk_conn_ok:
        print("\n🔴 PROBLEM: SDK cannot connect")
        print("\nThis is likely a compatibility issue.")
        print("\nThe 'robomaster' SDK is designed for EP/EP Core,")
        print("not specifically for the S1 model.")
        print("\nPossible solutions:")
        print("1. Try direct TCP socket connection (see test 3)")
        print("2. Use the raw protocol instead of SDK")
        print("3. Check if S1 requires different initialization")
        return

    print("\n✅ All tests passed! Connection should work.")


def main():
    """Run all tests."""
    print("=" * 60)
    print("RoboMaster S1 - USB Connection Debugger")
    print("=" * 60)

    results = {}

    results["network"] = test_network_interface()
    results["ping"] = test_ping()
    results["tcp"] = test_tcp_connection()
    results["sdk_import"] = test_sdk_import()
    results["sdk_conn"] = test_sdk_connection()
    results["ap_mode"] = test_with_ap_mode()

    diagnose_issue(results)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test:15} {status}")

    if all(results.values()):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. See diagnosis above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
