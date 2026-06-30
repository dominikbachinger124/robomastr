"""Test script for RoboMaster S1 controller.

This script tests the RoboMasterController without requiring a physical robot.
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def test_import():
    """Test that the module imports correctly."""
    try:
        from app.robot import RoboMasterController

        print("✓ Module import successful")
        return True
    except ImportError as e:
        print(f"✗ Module import failed: {e}")
        return False


def test_controller_creation():
    """Test that the controller can be instantiated."""
    try:
        from app.robot import RoboMasterController

        ctrl = RoboMasterController()
        assert ctrl.is_connected is False
        assert ctrl.chassis is None
        assert ctrl.gimbal is None
        assert ctrl.led is None
        print("✓ Controller instantiation successful")
        return True
    except Exception as e:
        print(f"✗ Controller creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("RoboMaster S1 Controller Tests")
    print("=" * 50)
    print()

    tests = [
        ("Import Test", test_import),
        ("Controller Creation Test", test_controller_creation),
    ]

    results = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    # Summary
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Controller is ready.")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
